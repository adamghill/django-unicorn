import { debounce } from "./delayers.js";
import { Element } from "./element.js";
import {
  addActionEventListener,
  addDbEventListener,
  addModelEventListener,
} from "./eventListeners.js";
import { components } from "./store.js";
import { send } from "./messageSender.js";
import morphdom from "./morphdom/2.6.1/morphdom.js";
import { $, hasValue, isEmpty, isFunction, walk, FilterSkipNested } from "./utils.js";

/**
 * Encapsulate component.
 */
export class Component {
  constructor(args) {
    this.id = args.id;
    this.name = args.name;
    this.key = args.key;
    this.messageUrl = args.messageUrl;
    this.csrfTokenHeaderName = args.csrfTokenHeaderName;
    this.hash = args.hash;
    this.data = args.data || {};
    this.syncUrl = `${this.messageUrl}/${this.name}`;

    this.document = args.document || document;
    this.walker = args.walker || walk;
    this.window = args.window || window;
    this.morphdom = args.morphdom || morphdom;

    this.root = undefined;
    this.modelEls = [];
    this.dbEls = [];
    this.loadingEls = [];
    this.keyEls = [];
    this.errors = {};
    this.return = {};
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

    this.callCalls(args.calls);
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
   * Gets the children components of the current component.
   */
  getChildrenComponents() {
    const elements = [];

    this.walker(this.root, (el) => {
      if (el.isSameNode(this.root)) {
        // Skip the component root element
        return;
      }
      const componentId = el.getAttribute("unicorn:id");

      if (componentId) {
        const childComponent = components[componentId] || null;

        if (childComponent) {
          elements.push(childComponent);
        }
      }
    });

    return elements;
  }

  /**
   * Gets the parent component of the current component.
   * @param {int} parentComponentId Parent component id.
   */
  getParentComponent(parentComponentId) {
    if (typeof parentComponentId !== "undefined") {
      return components[parentComponentId] || null;
    }

    let currentEl = this.root;
    let parentComponent = null;

    while (!parentComponent && currentEl.parentElement !== null) {
      currentEl = currentEl.parentElement;
      const componentId = currentEl.getAttribute("unicorn:id");

      if (componentId) {
        parentComponent = components[componentId] || null;
      }
    }

    return parentComponent;
  }

  /**
   * Call JavaScript functions on the `window`.
   * @param {Array} calls A list of objects that specify the methods to call.
   *
   * `calls`: [{"fn": "someFunctionName"},]
   * `calls`: [{"fn": "someFunctionName", args: ["world"]},]
   * `calls`: [{"fn": "SomeModule.someFunctionName"},]
   * `calls`: [{"fn": "SomeModule.someFunctionName", args: ["world", "universe"]},]
   *
   * Returns:
   * Array of results for each method call.
   */
  callCalls(calls) {
    calls = calls || [];
    const results = [];

    calls.forEach((call) => {
      let functionName = call.fn;
      let module = this.window;

      call.fn.split(".").forEach((obj, idx) => {
        // only traverse down modules to the first dot, because the last portion is the function name
        if (idx < call.fn.split(".").length - 1) {
          module = module[obj];
          // account for the period when slicing
          functionName = functionName.slice(obj.length + 1);
        }
      });

      if (call.args) {
        results.push(module[functionName](...call.args));
      } else {
        results.push(module[functionName]());
      }
    });

    return results;
  }

  /**
   * Sets event listeners on unicorn elements.
   */
  refreshEventListeners() {
    this.actionEvents = {};
    this.modelEls = [];
    this.dbEls = [];

    try {
      this.walker(this.root, (el) => {
        if (el.isSameNode(this.root)) {
          // Skip the component root element
          return;
        }

        const element = new Element(el);

        if (element.isUnicorn) {
          if (hasValue(element.field) && hasValue(element.db)) {
            if (!this.attachedDbEvents.some((e) => e.isSame(element))) {
              this.attachedDbEvents.push(element);
              addDbEventListener(this, element);

              // If a field is lazy, also add an event listener for input for dirty states
              if (element.field.isLazy) {
                // This input event for isLazy will be stopped after dirty is checked when the event fires
                addDbEventListener(this, element, "input");
              }
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
              addModelEventListener(this, element);

              // If a model is lazy, also add an event listener for input for dirty states
              if (element.model.isLazy) {
                // This input event for isLazy will be stopped after dirty is checked when the event fires
                addModelEventListener(this, element, "input");
              }
            }

            if (!this.modelEls.some((e) => e.isSame(element))) {
              this.modelEls.push(element);
            }
          } else if (hasValue(element.loading)) {
            this.loadingEls.push(element);

            // Hide loading elements that are shown when an action happens
            if (element.loading.show) {
              element.hide();
            }
          }

          if (hasValue(element.key)) {
            this.keyEls.push(element);
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
                element.events.push(action.eventType);
              }
            }
          });
        }
      }, FilterSkipNested);
    } catch (err) {
      // nothing
    }
  }

  /**
   * Calls the method for a particular component.
   */
  callMethod(methodName, debounceTime, partials, errCallback) {
    const action = {
      type: "callMethod",
      payload: { name: methodName },
      partials,
    };
    this.actionQueue.push(action);

    // Debounce timeout defaults to 0 in element.js to remove any perceived lag, but can be overridden
    this.queueMessage(debounceTime, (triggeringElements, _, err) => {
      if (err && isFunction(errCallback)) {
        errCallback(err);
      } else if (err) {
        console.error(err);
      } else {
        // Can hard-code `forceModelUpdate` to `true` since it is always required for
        // `callMethod` actions
        this.setModelValues(triggeringElements, true);
        this.setDbModelValues();
      }
    });
  }

  /**
   * Handles poll errors.
   * @param {Error} err Error.
   */
  handlePollError(err) {
    if (err) {
      console.error(err);
    } else if (this.poll.timer) {
      clearInterval(this.poll.timer);
    }
  }

  /**
   * Check to see if the poll is disabled.
   */
  isPollEnabled() {
    if (!this.poll.disable) {
      if (hasValue(this.poll.disableData)) {
        if (this.poll.disableData.startsWith("!")) {
          // Manually negate this and re-negate it after the check
          this.poll.disableData = this.poll.disableData.slice(1);

          if (this.data[this.poll.disableData]) {
            return true;
          }

          this.poll.disableData = `!${this.poll.disableData}`;
        } else if (!this.data[this.poll.disableData]) {
          return true;
        }
      } else {
        return true;
      }
    }

    return false;
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
            // Call the poll method once the tab is visible again
            this.startPolling(true);
          }
        },
        false
      );

      this.poll.partials = rootElement.partials;

      // Call the method once before the timer starts
      this.startPolling(true);
    }
  }

  /**
   * Starts polling and handles stopping the polling if there is an error.
   */
  startPolling(fireImmediately) {
    if (fireImmediately && this.isPollEnabled()) {
      this.callMethod(
        this.poll.method,
        0,
        this.poll.partials,
        this.handlePollError
      );
    }

    this.poll.timer = setInterval(() => {
      if (this.isPollEnabled()) {
        this.callMethod(
          this.poll.method,
          0,
          this.poll.partials,
          this.handlePollError
        );
      }
    }, this.poll.timing);
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
      if (isEmpty(element.db.pk)) {
        // Empty string for the PK implies that the model is not associated to an actual model instance
        element.setValue("");
      } else {
        const dbName = element.db.name || element.model.name;

        if (isEmpty(dbName)) {
          throw Error(
            "Setting a field value requires a db or model name to be set"
          );
        }

        let datas = this.data[dbName];

        // Force the data to be an array if it isn't already for the next step
        if (!Array.isArray(datas)) {
          datas = [datas];
        }

        datas.forEach((model) => {
          // Convert the model's pk to a string because it will always be a string on the element
          if (hasValue(model) && hasValue(model.pk)) {
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
  setModelValues(triggeringElements, forceModelUpdates) {
    triggeringElements = triggeringElements || [];
    forceModelUpdates = forceModelUpdates || false;

    let lastTriggeringElement = null;

    // Focus on the last element which triggered the update.
    // Prevents validation errors from stealing focus.
    if (triggeringElements.length > 0) {
      let elementFocused = false;
      lastTriggeringElement = triggeringElements.slice(-1)[0];

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
      if (
        forceModelUpdates ||
        !lastTriggeringElement ||
        !lastTriggeringElement.isSame(element)
      ) {
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
