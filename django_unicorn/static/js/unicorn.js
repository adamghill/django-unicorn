const Unicorn = (() => {
  const unicorn = {}; // contains all methods exposed publicly in the Unicorn object
  let messageUrl = "";
  const csrfTokenHeaderName = "X-CSRFToken";
  const components = {};

  /**
   * Initializes the Unicorn object.
   */
  unicorn.init = (_messageUrl) => {
    messageUrl = _messageUrl;
  };

  /**
   * Checks if a string has the search text.
   */
  function contains(str, search) {
    return str.indexOf(search) > -1;
  }

  /**
   * Checks if an object is empty. Useful for check if a dictionary has any values.
   */
  function isEmpty(obj) {
    return typeof obj === "undefined" || (Object.keys(obj).length === 0 && obj.constructor === Object);
  }

  /**
   * A simple shortcut for querySelector that everyone loves.
   */
  function $(selector, scope) {
    if (scope === undefined) {
      scope = document;
    }

    return scope.querySelector(selector);
  }

  /**
   * Get the CSRF token used by Django.
   */
  function getCsrfToken() {
    // Default to looking for the CSRF in the cookie
    const cookieKey = "csrftoken=";
    const csrfTokenCookie = document.cookie.split(";").filter((item) => item.trim().startsWith(cookieKey));

    if (csrfTokenCookie.length > 0) {
      return csrfTokenCookie[0].replace(cookieKey, "");
    }

    // Fall back to check for the CSRF hidden input
    const csrfElements = document.getElementsByName("csrfmiddlewaretoken");

    if (csrfElements && csrfElements.length > 0) {
      return csrfElements[0].getAttribute("value");
    }

    throw Error("CSRF token is missing. Do you need to add {% csrf_token %}?");
  }

  /**
   * Converts a string to "kebab-case", aka lower-cased with hyphens.
   * @param {string} str The string to be converted.
   */
  function toKebabCase(str) {
    return str
      .match(/[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g)
      .map((x) => x.toLowerCase())
      .join("-");
  }

  /**
   * Returns a function, that, as long as it continues to be invoked, will not
   * be triggered. The function will be called after it stops being called for
   * N milliseconds. If `immediate` is passed, trigger the function on the
   * leading edge, instead of the trailing.

   * Derived from underscore.js's implementation in https://davidwalsh.name/javascript-debounce-function.
   */
  function debounce(func, wait, immediate) {
    let timeout;

    if (typeof immediate === "undefined") {
      immediate = true;
    }

    return (...args) => {
      const context = this;

      const later = () => {
        timeout = null;
        if (!immediate) {
          func.apply(context, args);
        }
      };

      const callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);

      if (callNow) {
        func.apply(context, args);
      }
    };
  }

  /**
   * The function is executed the number of times it is called,
   * but there is a fixed wait time before each execution.
   * From https://medium.com/ghostcoder/debounce-vs-throttle-vs-queue-execution-bcde259768.
   */
  const funcQueue = [];
  function queue(func, waitTime) {
    let isWaiting;

    const play = () => {
      let params;
      isWaiting = false;

      if (funcQueue.length) {
        params = funcQueue.shift();
        executeFunc(params);
      }
    };

    const executeFunc = (params) => {
      isWaiting = true;
      func(params);
      setTimeout(play, waitTime);
    };

    return (params) => {
      if (isWaiting) {
        funcQueue.push(params);
      } else {
        executeFunc(params);
      }
    };
  }

  /**
   * Traverses the DOM looking for child elements.
   */
  function walk(el, callback) {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_ELEMENT, null, false);

    while (walker.nextNode()) {
      // TODO: Handle sub-components?
      callback(walker.currentNode);
    }
  }

  /**
   * Encapsulate DOM element attribute for Unicorn-related information.
   */
  class Attribute {
    constructor(attribute) {
      this.attribute = attribute;
      this.name = this.attribute.name;
      this.value = this.attribute.value;
      this.isUnicorn = false;
      this.isModel = false;
      this.isPoll = false;
      this.isKey = false;
      this.isError = false;
      this.modifiers = {};
      this.eventType = null;

      this.init();
    }

    /**
     * Init the attribute.
     */
    init() {
      if (contains(this.name, "unicorn:")) {
        this.isUnicorn = true;

        if (contains(this.name, "unicorn:model")) {
          this.isModel = true;
        } else if (contains(this.name, "unicorn:poll")) {
          this.isPoll = true;
        } else if (this.name === "unicorn:key") {
          this.isKey = true;
        } else if (contains(this.name, "unicorn:error:")) {
          this.isError = true;
        } else {
          const actionEventType = this.name.replace("unicorn:", "");

          if (actionEventType !== "id" && actionEventType !== "name" && actionEventType !== "checksum") {
            this.eventType = actionEventType;
          }
        }

        let potentialModifiers = this.name;
        if (this.eventType) {
          potentialModifiers = this.eventType;
        }

        // Find modifiers and any potential arguments
        potentialModifiers.split(".").slice(1).forEach((modifier) => {
          const modifierArgs = modifier.split("-");
          this.modifiers[modifierArgs[0]] = modifierArgs.length > 1 ? modifierArgs[1] : true;
        });
      }
    }
  }

  /**
   * Encapsulate DOM element for Unicorn-related information.
   */
  class Element {
    constructor(el) {
      this.el = el;
      this.init();
    }

    /**
     * Init the element.
     */
    init() {
      this.id = this.el.id;
      this.isUnicorn = false;
      this.attributes = [];
      this.value = this.getValue();

      this.model = {};
      this.poll = {};
      this.action = {};

      this.key = undefined;
      this.errors = [];

      if (!this.el.attributes) {
        return;
      }

      for (let i = 0; i < this.el.attributes.length; i++) {
        const attribute = new Attribute(this.el.attributes[i]);
        this.attributes.push(attribute);

        if (attribute.isUnicorn) {
          this.isUnicorn = true;
        }

        if (attribute.isModel) {
          this.model.name = attribute.value;
          this.model.eventType = attribute.modifiers.lazy ? "blur" : "input";
          this.model.isLazy = !!attribute.modifiers.lazy;
          this.model.debounceTime = attribute.modifiers.debounce ? parseInt(attribute.modifiers.debounce, 10) || -1 : -1;
        } else if (attribute.isPoll) {
          this.poll.method = attribute.value ? attribute.value : "refresh";
          this.poll.timing = parseInt(Object.keys(attribute.modifiers)[0], 10) || 2000;
        } else if (attribute.eventType) {
          this.action.name = attribute.value;
          this.action.eventType = attribute.eventType;

          if (attribute.modifiers) {
            this.action.key = Object.keys(attribute.modifiers)[0];
          }

          if (this.action.key) {
            this.action.eventType = this.action.eventType.replace(`.${this.action.key}`, "");
          }
        }

        if (attribute.isKey) {
          this.key = attribute.value;
        }

        if (attribute.isError) {
          const code = attribute.name.replace("unicorn:name:", "");
          this.errors.push({ code, message: attribute.value });
        }
      }
    }

    /**
     * Focuses the element.
     */
    focus() {
      this.el.focus();
    }

    /**
     * Gets the value from the element.
     */
    getValue() {
      let { value } = this.el;

      if (this.el.type) {
        if (this.el.type.toLowerCase() === "checkbox") {
          // Handle checkbox
          value = this.el.checked;
        } else if (this.el.type.toLowerCase() === "select-multiple") {
          // Handle multiple select options
          value = [];
          for (let i = 0; i < this.el.selectedOptions.length; i++) {
            value.push(this.el.selectedOptions[i].value);
          }
        }
      }

      return value;
    }

    /**
     * Sets the value of an element. Tries to deal with HTML weirdnesses.
     */
    setValue(val) {
      if (this.el.type.toLowerCase() === "radio") {
        // Handle radio buttons
        if (this.el.value === val) {
          this.el.checked = true;
        }
      } else if (this.el.type.toLowerCase() === "checkbox") {
        // Handle checkboxes
        this.el.checked = val;
      } else {
        this.el.value = val;
      }
    }

    /**
     * Add an error to the element.
     */
    addError(error) {
      this.errors.push(error);
      this.el.setAttribute(`unicorn:error:${error.code}`, error.message);
    }

    /**
     * Remove all errors from the element.
     */
    removeErrors() {
      this.errors.forEach((error) => {
        this.el.removeAttribute(error.code);
      });

      this.errors = [];
    }
  }

  /**
   * Encapsulate component.
   */
  class Component {
    constructor(args) {
      this.id = args.id;
      this.name = args.name;

      if (contains(this.name, ".")) {
        const names = this.name.split(".");
        this.name = names[names.length - 2];
      }

      this.data = args.data;
      this.syncUrl = `${messageUrl}/${this.name}`;

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
        headers[csrfTokenHeaderName] = getCsrfToken();

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

  /**
   * Initializes the component.
   */
  unicorn.componentInit = (args) => {
    const component = new Component(args);
    component.init();
    components[component.id] = component;

    component.setModelValues();
  };

  /**
   * Call an action on the specified component.
   */
  unicorn.call = (componentName, methodName) => {
    let component;

    Object.keys(components).forEach((id) => {
      if (typeof component === "undefined") {
        const _component = components[id];

        if (_component.name === componentName) {
          component = _component;
        }
      }
    });

    if (!component) {
      throw Error("No component found for: ", componentName);
    }

    component.callMethod(methodName, (err) => {
      console.error(err);
    });
  };

  return unicorn;
})();
