import {
  $,
  contains,
  getCsrfToken,
  isEmpty,
  toKebabCase,
  walk,
} from "./utils.js";
import { debounce } from "./delayers.js";
import { Element } from "./element.js";
import morphdom from "./morphdom/2.6.1/morphdom.js";

export const MORPHDOM_OPTIONS = {
  childrenOnly: false,
  // eslint-disable-next-line consistent-return
  getNodeKey(node) {
    // A node's unique identifier. Used to rearrange elements rather than
    // creating and destroying an element that already exists.
    if (node.attributes) {
      const key = node.getAttribute("unicorn:key") || node.id;

      if (key) {
        return key;
      }
    }
  },
  // eslint-disable-next-line consistent-return
  onBeforeElUpdated(fromEl, toEl) {
    // Because morphdom also supports vDom nodes, it uses isSameNode to detect
    // sameness. When dealing with DOM nodes, we want isEqualNode, otherwise
    // isSameNode will ALWAYS return false.
    if (fromEl.isEqualNode(toEl)) {
      return false;
    }
  },
};

/**
 * Encapsulate component.
 */
export class Component {
  constructor(args) {
    this.id = args.id;
    this.name = args.name;
    this.messageUrl = args.messageUrl;
    this.csrfTokenHeaderName = args.csrfTokenHeaderName;

    if (contains(this.name, ".")) {
      const names = this.name.split(".");
      this.name = names[names.length - 2];
    }

    this.data = args.data;
    this.syncUrl = `${this.messageUrl}/${this.name}`;

    this.document = args.document || document;
    this.walker = args.walker || walk;

    this.root = undefined;
    this.modelEls = [];
    this.dbEls = [];
    this.errors = {};
    this.poll = {};

    this.actionQueue = [];
    this.currentActionQueue = null;
    this.lastTriggeringElements = [];

    this.actionEvents = {};
    this.attachedEventTypes = [];

    this.init();
    this.refreshEventListeners();
    this.initPolling();
  }

  /**
   * Initializes the Component.
   */
  init() {
    this.root = $(`[unicorn\\:id="${this.id}"]`, this.document);

    if (!this.root) {
      throw Error("No id found");
    }

    this.refreshChecksum();
  }

  /**
   * Adds an action event listener to the document for each type of event (e.g. click, keyup, etc).
   * Added at the document level because validation errors would sometimes remove the
   * events when attached directly to the element.
   */
  addActionEventListener(eventType) {
    this.document.addEventListener(eventType, (event) => {
      const targetElement = new Element(event.target);

      if (
        targetElement &&
        targetElement.isUnicorn &&
        targetElement.actions.length > 0
      ) {
        this.actionEvents[eventType].forEach((actionEvent) => {
          const { action } = actionEvent;
          const { element } = actionEvent;

          // Use isSameNode (not isEqualNode) because we want to check the nodes reference the same object
          if (targetElement.el.isSameNode(element.el)) {
            // Add the value of any child element of the target that is a lazy model to the action queue
            // Handles situations similar to https://github.com/livewire/livewire/issues/528
            walk(element.el, (childEl) => {
              const modelElsInTargetScope = this.modelEls.filter((e) =>
                e.el.isSameNode(childEl)
              );

              modelElsInTargetScope.forEach((modelElement) => {
                if (!isEmpty(modelElement.model) && modelElement.model.isLazy) {
                  const actionForQueue = {
                    type: "syncInput",
                    payload: {
                      pk: modelElement.model.pk,
                      name: modelElement.model.name,
                      value: modelElement.getValue(),
                    },
                  };
                  this.actionQueue.push(actionForQueue);
                }
              });
            });

            if (action.isPrevent) {
              event.preventDefault();
            }

            if (action.isStop) {
              event.stopPropagation();
            }

            if (action.key) {
              if (action.key === toKebabCase(event.key)) {
                this.callMethod(action.name);
              }
            } else {
              this.callMethod(action.name);
            }
          }
        });
      }
    });
  }

  /**
   * Adds a model event listener to the element.
   * @param {Element} element Element that will get the event attached to.
   * @param {string} eventType Event type to listen for.
   */
  addModelEventListener(element, eventType) {
    element.el.addEventListener(eventType, () => {
      const action = {
        type: "syncInput",
        payload: {
          name: element.model.name,
          value: element.getValue(),
        },
      };

      if (element.model.isDefer) {
        let foundAction = false;

        // Update the existing action with the current value
        this.actionQueue.forEach((a) => {
          if (a.payload.name === element.model.name) {
            a.payload.value = element.getValue();
            foundAction = true;
          }
        });

        // Add a new action
        if (!foundAction) {
          this.actionQueue.push(action);
          this.lastTriggeringElements.push(element);
        }

        return;
      }

      this.actionQueue.push(action);
      this.lastTriggeringElements.push(element);

      this.sendMessage(
        element.model.debounceTime,
        (triggeringElements, _, err) => {
          if (err) {
            console.error(err);
          } else {
            this.setModelValues(triggeringElements);
            this.setDbModelValues(triggeringElements);
          }
        }
      );
    });
  }

  addDbEventListener(element, eventType) {
    element.el.addEventListener(eventType, () => {
      if (!element.db.name || !element.db.pk) {
        return;
      }

      const action = {
        type: "dbInput",
        payload: {
          db: element.db.name,
          pk: element.db.pk,
          fields: {},
        },
      };

      action.payload.fields[element.field.name] = element.getValue();

      if (element.field.isDefer) {
        let foundAction = false;

        // Update the existing action with the current value
        this.actionQueue.forEach((a) => {
          if (
            a.payload.db === element.db.name &&
            a.payload.pk === element.db.pk
          ) {
            a.payload.fields[element.field.name] = element.getValue();
            foundAction = true;
          }
        });

        // Add a new action
        if (!foundAction) {
          this.actionQueue.push(action);
        }

        this.lastTriggeringElements.push(element);

        return;
      }

      this.actionQueue.push(action);
      this.lastTriggeringElements.push(element);

      this.sendMessage(
        element.model.debounceTime,
        (triggeringElements, dbUpdates, err) => {
          if (err) {
            console.error(err);
          } else {
            this.setDbModelValues(triggeringElements, dbUpdates);
          }
        }
      );
    });
  }

  /**
   * Sets event listeners on unicorn elements.
   */
  refreshEventListeners() {
    this.actionEvents = {};
    this.modelEls = [];
    this.dbEls = [];

    this.walker(this.root, (el) => {
      if (el.isSameNode(this.root)) {
        // Skip the component root element
        return;
      }

      const element = new Element(el);

      if (element.isUnicorn) {
        if (!isEmpty(element.model)) {
          if (
            this.modelEls.filter((e) => e.el.isSameNode(element.el)).length ===
            0
          ) {
            this.modelEls.push(element);
            this.addModelEventListener(element, element.model.eventType);
          }
        }

        if (!isEmpty(element.db) && !isEmpty(element.field)) {
          if (
            this.dbEls.filter((e) => e.el.isSameNode(element.el)).length === 0
          ) {
            this.dbEls.push(element);
            this.addDbEventListener(element, "input");
          }
        }

        // if (!isEmpty(element.db))
        element.actions.forEach((action) => {
          // if (element.actions.length > 0) {
          if (this.actionEvents[action.eventType]) {
            this.actionEvents[action.eventType].push({ action, element });
          } else {
            this.actionEvents[action.eventType] = [{ action, element }];

            if (
              this.attachedEventTypes.filter((et) => et === action.eventType)
                .length === 0
            ) {
              this.attachedEventTypes.push(action.eventType);
              this.addActionEventListener(action.eventType);
            }
          }
        });
      }
    });
  }

  /**
   * Calls the method for a particular component.
   */
  callMethod(methodName, errCallback) {
    const action = {
      type: "callMethod",
      payload: { name: methodName, params: [] },
    };
    this.actionQueue.push(action);

    this.sendMessage(-1, (triggeringElements, dbUpdates, err) => {
      if (err && typeof errCallback === "function") {
        errCallback(err);
      } else if (err) {
        console.error(err);
      } else {
        this.setModelValues(triggeringElements);
        this.setDbModelValues(triggeringElements);
      }
    });
  }

  /**
   * Sets up polling if it is defined on the component's root.
   */
  initPolling() {
    const rootElement = new Element(this.root);

    if (rootElement.isUnicorn && !isEmpty(rootElement.poll)) {
      this.poll = rootElement.poll;
      this.poll.timer = null;

      this.document.addEventListener(
        "visibilitychange",
        () => {
          if (this.document.hidden) {
            if (this.poll.timer) {
              clearInterval(this.poll.timer);
            }
          } else {
            this.startPolling();
          }
        },
        false
      );

      this.startPolling();
    }
  }

  /**
   * Starts polling and handles stopping the polling if there is an error.
   */
  startPolling() {
    this.poll.timer = null;
    const { timer } = this.poll;

    function handleError(err) {
      if (err) {
        console.error(err);
      }
      if (timer) {
        clearInterval(timer);
      }
    }

    // Call the method once before the timer starts
    this.callMethod(this.poll.method, handleError);

    this.poll.timer = setInterval(
      this.callMethod.bind(this),
      this.poll.timing,
      this.poll.method,
      handleError
    );
  }

  /**
   * Refresh the checksum.
   */
  refreshChecksum() {
    this.checksum = this.root.getAttribute("unicorn:checksum");
  }

  /**
   * Sets the value of an element. Tries to deal with HTML weirdnesses.
   * @param {Element} element Element to set value to (value retrieved from `component.data`).
   */
  setValue(element) {
    if (isEmpty(element.model)) {
      // Don't try to set the value if there isn't a model on the element
      return;
    }

    const modelNamePieces = element.model.name.split(".");
    // Get local version of data in case have to traverse into a nested property
    let _data = this.data;

    for (let i = 0; i < modelNamePieces.length; i++) {
      const modelNamePiece = modelNamePieces[i];

      if (_data == null) {
        return;
      }

      if (Object.prototype.hasOwnProperty.call(_data, modelNamePiece)) {
        if (i === modelNamePieces.length - 1) {
          element.setValue(_data[modelNamePiece]);
        } else {
          _data = _data[modelNamePiece];
        }
      }
    }
  }

  /**
   * Sets all db model values.
   * @param {[Element]} triggeringElements The elements that triggered the event.
   * @param {Element} dbUpdates Updates from the database.
   */
  setDbModelValues(triggeringElements, dbUpdates) {
    triggeringElements = triggeringElements || [];
    dbUpdates = dbUpdates || {};

    const lastTriggeringElement = triggeringElements.slice(-1)[0];

    this.dbEls.forEach((element) => {
      if (
        typeof lastTriggeringElement === "undefined" ||
        !lastTriggeringElement.el.isSameNode(element.el)
      ) {
        Object.keys(dbUpdates).forEach((key) => {
          if (element.dbKey() === key) {
            Object.keys(dbUpdates[key]).forEach((fieldName) => {
              if (element.field.name === fieldName) {
                element.setValue(dbUpdates[key][fieldName]);
              }
            });
          }
        });
      }
    });
  }

  /**
   * Sets all model values.
   * @param {[Element]} triggeringElements The elements that triggered the event.
   */
  setModelValues(triggeringElements) {
    triggeringElements = triggeringElements || [];

    // Focus on the last element on what triggered the update.
    // Prevents validation errors from stealing focus.
    if (triggeringElements.length > 0) {
      let elementFocused = false;
      const lastTriggeringElement = triggeringElements.slice(-1)[0];

      if (
        typeof lastTriggeringElement !== "undefined" &&
        !isEmpty(lastTriggeringElement.model) &&
        !lastTriggeringElement.model.isLazy
      ) {
        ["id", "key"].forEach((attr) => {
          this.modelEls.forEach((element) => {
            if (!elementFocused) {
              if (
                lastTriggeringElement[attr] &&
                lastTriggeringElement[attr] === element[attr]
              ) {
                element.focus();
                elementFocused = true;
              }
            }
          });
        });
      }
    }

    this.modelEls.forEach((element) => {
      let shouldSetValue = false;

      triggeringElements.forEach((triggeringElement) => {
        if (!element.el.isSameNode(triggeringElement.el)) {
          shouldSetValue = true;
        }
      });

      // Set the value if there are no triggering elements (happens on initial page load)
      // or when the model element doesn't match one of the triggering elements
      if (shouldSetValue || triggeringElements.length === 0) {
        this.setValue(element);
      }
    });
  }

  /**
   * Calls the message endpoint and merges the results into the document.
   */
  sendMessage(debounceTime, callback) {
    function _sendMessage(_component) {
      // Prevent network call when there isn't an action
      if (_component.actionQueue.length === 0) {
        return;
      }

      // Prevent network call when the action queue gets repeated
      if (_component.currentActionQueue === _component.actionQueue) {
        return;
      }

      // Set the current action queue and clear the action queue in case another event happens
      _component.currentActionQueue = _component.actionQueue;
      _component.actionQueue = [];

      const body = {
        id: _component.id,
        data: _component.data,
        checksum: _component.checksum,
        actionQueue: _component.currentActionQueue,
      };

      const headers = {
        Accept: "application/json",
        "X-Requested-With": "XMLHttpRequest",
      };
      headers[_component.csrfTokenHeaderName] = getCsrfToken();

      fetch(_component.syncUrl, {
        method: "POST",
        headers,
        body: JSON.stringify(body),
      })
        .then((response) => {
          if (response.ok) {
            return response.json();
          }

          throw Error(
            `Error when getting response: ${response.statusText} (${response.status})`
          );
        })
        .then((responseJson) => {
          if (!responseJson) {
            return;
          }

          if (responseJson.error) {
            // TODO: Check for "Checksum does not match" error and try to fix it
            throw Error(responseJson.error);
          }

          // Remove any unicorn validation messages before trying to merge with morphdom
          _component.modelEls.forEach((element) => {
            // Re-initialize element to make sure it is up to date
            element.init();
            element.removeErrors();
          });

          // Get the data from the response
          _component.data = responseJson.data || {};
          _component.errors = responseJson.errors || {};
          const rerenderedComponent = responseJson.dom;

          morphdom(_component.root, rerenderedComponent, MORPHDOM_OPTIONS);

          // Refresh the checksum based on the new data
          _component.refreshChecksum();

          // Reset all event listeners
          _component.refreshEventListeners();

          // Re-add unicorn validation messages from errors
          _component.modelEls.forEach((element) => {
            Object.keys(_component.errors).forEach((modelName) => {
              if (element.model.name === modelName) {
                const error = _component.errors[modelName][0];
                element.addError(error);
              }
            });
          });

          const triggeringElements = _component.lastTriggeringElements;
          _component.lastTriggeringElements = [];

          // Clear the current action queue
          _component.currentActionQueue = null;

          const dbUpdates = responseJson.db || {};

          if (callback && typeof callback === "function") {
            callback(triggeringElements, dbUpdates, null);
          }
        })
        .catch((err) => {
          // Make sure to clear the current queues in case of an error
          _component.actionQueue = [];
          _component.currentActionQueue = null;
          _component.lastTriggeringElements = [];

          if (callback && typeof callback === "function") {
            callback(null, null, err);
          }
        });
    }

    if (debounceTime === -1) {
      debounce(_sendMessage, 250, false)(this);
      // queue(_sendMessage, 250)(this);
    } else {
      debounce(_sendMessage, debounceTime, false)(this);
    }
  }
}
