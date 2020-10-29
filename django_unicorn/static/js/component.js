import { $, contains, hasValue, isEmpty, isFunction, walk } from "./utils.js";
import { debounce } from "./delayers.js";
import { Element } from "./element.js";
import { send } from "./messageSender.js";
import {
  addActionEventListener,
  addDbEventListener,
  addModelEventListener,
} from "./eventListeners.js";

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
    this.attachedModelEvents = [];
    this.attachedDbEvents = [];

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
        if (
          hasValue(element.field) &&
          (hasValue(element.db) || hasValue(element.model))
        ) {
          if (!this.attachedDbEvents.some((e) => e.isSame(element))) {
            this.attachedDbEvents.push(element);
            addDbEventListener(this, element.el, element.field.eventType);
          }

          if (!this.dbEls.some((e) => e.isSame(element))) {
            this.dbEls.push(element);
          }
        } else if (
          hasValue(element.model) &&
          isEmpty(element.db) &&
          isEmpty(element.field)
        ) {
          if (!this.attachedModelEvents.some((e) => e.isSame(element))) {
            this.attachedModelEvents.push(element);
            addModelEventListener(this, element.el, element.model.eventType);
          }

          if (!this.modelEls.some((e) => e.isSame(element))) {
            this.modelEls.push(element);
          }
        }

        element.actions.forEach((action) => {
          if (this.actionEvents[action.eventType]) {
            this.actionEvents[action.eventType].push({ action, element });
          } else {
            this.actionEvents[action.eventType] = [{ action, element }];

            if (
              !this.attachedEventTypes.some((et) => et === action.eventType)
            ) {
              this.attachedEventTypes.push(action.eventType);
              addActionEventListener(this, action.eventType);
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
      payload: { name: methodName },
    };
    this.actionQueue.push(action);

    this.queueMessage(-1, (triggeringElements, err) => {
      if (err && isFunction(errCallback)) {
        errCallback(err);
      } else if (err) {
        console.error(err);
      } else {
        this.setModelValues(triggeringElements);
        this.setDbModelValues();
      }
    });
  }

  /**
   * Sets up polling if it is defined on the component's root.
   */
  initPolling() {
    const rootElement = new Element(this.root);

    if (rootElement.isUnicorn && hasValue(rootElement.poll)) {
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

    this.setNestedValue(element, element.model.name, this.data);
  }

  /**
   * Sets an element value dealing with potential nested values
   * @param {Element} element Element to set values on
   * @param {String} name Name of the property
   * @param {Object} data Data to get values from
   */
  // eslint-disable-next-line class-methods-use-this
  setNestedValue(element, name, data) {
    const namePieces = name.split(".");
    // Get local version of data in case have to traverse into a nested property
    let _data = data;

    for (let i = 0; i < namePieces.length; i++) {
      const namePiece = namePieces[i];

      if (_data == null) {
        return;
      }

      if (Object.prototype.hasOwnProperty.call(_data, namePiece)) {
        if (i === namePieces.length - 1) {
          element.setValue(_data[namePiece]);
        } else {
          _data = _data[namePiece];
        }
      }
    }
  }

  /**
   * Sets all db model values.
   */
  setDbModelValues() {
    this.dbEls.forEach((element) => {
      if (element.db.pk === "") {
        // Empty string for the PK implies that the model is not associated to an actual model instance
        element.setValue("");
      } else {
        if (isEmpty(element.model.name)) {
          throw Error("Setting a field value requires a model to be set");
        }

        let datas = this.data[element.model.name];

        // Force the data to be an array if it isn't already for the next step
        if (!Array.isArray(datas)) {
          datas = [datas];
        }

        datas.forEach((model) => {
          // Convert the model's pk to a string because it will always be a string on the element
          if (hasValue(model.pk)) {
            if (model.pk.toString() === element.db.pk) {
              element.setValue(model[element.field.name]);
            }
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
        hasValue(lastTriggeringElement) &&
        hasValue(lastTriggeringElement.model) &&
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
        if (!element.isSame(triggeringElement)) {
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
   * Queues the `messageSender.send` call.
   */
  queueMessage(debounceTime, callback) {
    if (debounceTime === -1) {
      debounce(send, 250, false)(this, callback);
    } else {
      debounce(send, debounceTime, false)(this, callback);
    }
  }
}
