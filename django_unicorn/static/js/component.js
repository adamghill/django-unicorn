import { $, contains, isEmpty, walk } from "./utils.js";
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
        if (!isEmpty(element.model)) {
          if (
            this.modelEls.filter((e) => e.el.isSameNode(element.el)).length ===
            0
          ) {
            this.modelEls.push(element);
            addModelEventListener(this, element, element.model.eventType);
          }
        }

        if (!isEmpty(element.db) && !isEmpty(element.field)) {
          if (!this.dbEls.some((e) => e.el.isSameNode(element.el))) {
            this.dbEls.push(element);
            addDbEventListener(this, element, element.field.eventType);
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
      payload: { name: methodName, params: [] },
    };
    this.actionQueue.push(action);

    this.queueMessage(-1, (triggeringElements, _, err) => {
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
