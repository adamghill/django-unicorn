import { $, contains, getCsrfToken, isEmpty, toKebabCase, walk } from "./utils.js";
import { debounce } from "./delayers.js";
import { Element } from "./element.js";
import morphdom from "./morphdom/2.6.1/morphdom.js"

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

    this.root = undefined;
    this.modelEls = [];
    this.errors = {};
    this.poll = {};
    this.actionQueue = [];
    this.currentActionQueue = null;
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
    this.root = $(`[unicorn\\:id="${this.id}"]`);

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
    document.addEventListener(eventType, (event) => {
      const targetElement = new Element(event.target);

      if (targetElement && targetElement.isUnicorn && !isEmpty(targetElement.action)) {
        this.actionEvents[eventType].forEach((element) => {
          // Use isSameNode (not isEqualNode) because we want to check the nodes reference the same object
          if (targetElement.el.isSameNode(element.el)) {
            if (!isEmpty(targetElement.model) && targetElement.model.isLazy) {
              const action = { type: "syncInput", payload: { name: targetElement.model.name, value: targetElement.getValue() } };
              this.actionQueue.push(action);
            }

            if (element.action.isPrevent) {
              event.preventDefault();
            }

            if (element.action.isStop) {
              event.stopPropagation();
            }

            if (element.action.key) {
              if (element.action.key === toKebabCase(event.key)) {
                this.callMethod(element.action.name);
              }
            } else {
              this.callMethod(element.action.name);
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
      const action = { type: "syncInput", payload: { name: element.model.name, value: element.getValue() } };

      if (element.model.isDefer) {
        let foundAction = false;

        this.actionQueue.forEach((a) => {
          if (a.payload.name === element.model.name) {
            a.payload.value = element.getValue();
            foundAction = true;
          }
        });

        if (!foundAction) {
          this.actionQueue.push(action);
        }

        return;
      }

      this.actionQueue.push(action);

      this.sendMessage(element.model.debounceTime, (excludeElement, err) => {
        if (err) {
          console.error(err);
        } else if (excludeElement) {
          this.setModelValues(element);
        } else {
          this.setModelValues();
        }
      });
    });
  }

  /**
   * Sets event listeners on unicorn elements.
   */
  refreshEventListeners() {
    this.actionEvents = {};

    walk(this.root, (el) => {
      if (el.isSameNode(this.root)) {
        // Skip the component root element
        return;
      }

      const element = new Element(el);

      if (element.isUnicorn) {
        if (!isEmpty(element.model)) {
          if (this.modelEls.filter((m) => m.el.isSameNode(element.el)).length === 0) {
            this.modelEls.push(element);
            this.addModelEventListener(element, element.model.eventType);
          }
        }

        if (!isEmpty(element.action)) {
          if (this.actionEvents[element.action.eventType]) {
            this.actionEvents[element.action.eventType].push(element);
          } else {
            this.actionEvents[element.action.eventType] = [element];

            if (this.attachedEventTypes.filter((et) => et === element.action.eventType).length === 0) {
              this.attachedEventTypes.push(element.action.eventType);
              this.addActionEventListener(element.action.eventType);
            }
          }
        }
      }
    });
  }

  /**
   * Calls the method for a particular component.
   */
  callMethod(methodName, errCallback) {
    const action = { type: "callMethod", payload: { name: methodName, params: [] } };
    this.actionQueue.push(action);

    this.sendMessage(-1, (_, err) => {
      if (err && typeof errCallback === "function") {
        errCallback(err);
      } else if (err) {
        console.error(err);
      } else {
        this.setModelValues();
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

      document.addEventListener("visibilitychange", () => {
        if (document.hidden) {
          if (this.poll.timer) {
            clearInterval(this.poll.timer);
          }
        } else {
          this.startPolling();
        }
      }, false);

      this.startPolling();
    }
  }

  /**
   * Starts polling and handles stopping the polling if there is an error.
   */
  startPolling() {
    this.poll.timer = null;

    function handleError(err) {
      if (err) {
        console.error(err);
      }
      if (this.poll.timer) {
        clearInterval(this.poll.timer);
      }
    }

    // Call the method once before the timer starts
    this.callMethod(this.poll.method, handleError);

    this.poll.timer = setInterval(this.callMethod.bind(this), this.poll.timing, this.poll.method, handleError);
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
    const modelNamePieces = element.model.name.split(".");
    // Get local version of data in case have to traverse into a nested property
    let _data = this.data;

    for (let i = 0; i < modelNamePieces.length; i++) {
      const modelNamePiece = modelNamePieces[i];

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
   * Sets all model values.
   * @param {Object} elementToExclude Prevent a particular element from being updated. Object example: `{id: 'elementId', key: 'elementKey'}`.
   */
  setModelValues(elementToExclude) {
    elementToExclude = elementToExclude || {};
    let elementFocused = false;

    // Focus on the element that is being excluded since that is what triggered the update.
    // Prevents validation errors from stealing focus.
    if (!isEmpty(elementToExclude) && !elementToExclude.model.isLazy) {
      ["id", "key"].forEach((attr) => {
        this.modelEls.forEach((element) => {
          if (!elementFocused) {
            if (elementToExclude[attr] && elementToExclude[attr] === element[attr]) {
              element.focus();
              elementFocused = true;
            }
          }
        });
      });
    }

    this.modelEls.forEach((element) => {
      if (element.id !== elementToExclude.id || element.key !== elementToExclude.key) {
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

      // Prevent newtwork call when the action queue gets repeated
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

          throw Error(`Error when getting response: ${response.statusText} (${response.status})`);
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

          const morphdomOptions = {
            childrenOnly: false,
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
            onBeforeElUpdated(fromEl, toEl) {
              // Because morphdom also supports vDom nodes, it uses isSameNode to detect
              // sameness. When dealing with DOM nodes, we want isEqualNode, otherwise
              // isSameNode will ALWAYS return false.
              if (fromEl.isEqualNode(toEl)) {
                return false;
              }
            },
          };

          // eslint-disable-next-line no-undef
          morphdom(_component.root, rerenderedComponent, morphdomOptions);

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

          // Check if the current actionQueue contains a callMethod. Prevents excluding
          // an element from getting a value set because calling a component function can
          // potentially have side effects which have to be reflected on the current element.
          let hasCallMethod = false;

          _component.currentActionQueue.forEach((action) => {
            if (action.type === "callMethod") {
              hasCallMethod = true;
            }
          });

          // Clear the current action queue
          _component.currentActionQueue = null;

          if (callback && typeof callback === "function") {
            callback(!hasCallMethod, null);
          }
        })
        .catch((err) => {
          // Make sure to clear the current queues in case of an error
          _component.actionQueue = [];
          _component.currentActionQueue = null;

          if (callback && typeof callback === "function") {
            callback(null, err);
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
