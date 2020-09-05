const Unicorn = (() => {
  const unicorn = {}; // contains all methods exposed publicly in the Unicorn object
  let messageUrl = "";
  const csrfTokenHeaderName = "X-CSRFToken";
  const data = {};
  const errors = {};

  /*
  Checks if a string has the search text.
  */
  function contains(str, search) {
    return str.indexOf(search) > -1;
  }

  /*
  Checks if an object is empty. Useful for check if a dictionary has any values.
  */
  function isEmpty(obj) {
    return Object.keys(obj).length === 0 && obj.constructor === Object;
  }

  /*
  Encapsulate DOM element attribute for Unicorn-related information.
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

    /*
    Init the attribute.
    */
    init() {
      if (contains(this.name, "unicorn:")) {
        this.isUnicorn = true;

        if (contains(this.name, "unicorn:model")) {
          this.isModel = true;
        } else if (contains(this.name, "unicorn:poll")) {
          this.isPoll = true;
        } else if (contains(this.name, "unicorn:key")) {
          this.isKey = true;
        } else if (contains(this.name, "unicorn:error:")) {
          this.isError = true;
        } else {
          this.eventType = this.name.replace("unicorn:", "");
        }

        if (!this.eventType) {
          // Find modifiers and any potential arguments
          this.name.split(".").slice(1).forEach((modifier) => {
            const modifierArgs = modifier.split("-");
            this.modifiers[modifierArgs[0]] = modifierArgs.length > 1 ? modifierArgs[1] : true;
          });
        }
      }
    }
  }

  /*
  Encapsulate DOM element for Unicorn-related information.
  */
  class Element {
    constructor(el) {
      this.el = el;
      this.init();
    }

    /*
    Init the element.
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

      for (let i = 0; i < this.el.attributes.length; i++) {
        const attribute = new Attribute(this.el.attributes[i]);
        this.attributes.push(attribute);

        if (attribute.isUnicorn) {
          this.isUnicorn = true;
        }

        if (attribute.isModel) {
          this.model.name = attribute.value;
          this.model.eventType = attribute.modifiers.lazy ? "blur" : "input";
          this.model.debounceTime = attribute.modifiers.debounce ? parseInt(attribute.modifiers.debounce, 10) || -1 : -1;
        } else if (attribute.isPoll) {
          this.poll.method = attribute.value ? attribute.value : "refresh";
          this.poll.timing = parseInt(Object.keys(attribute.modifiers)[0], 10) || 2000;
        } else if (attribute.eventType) {
          this.action.name = attribute.value;
          this.action.eventType = attribute.eventType;
        }

        if (attribute.isKey) {
          this.key = attribute.value;
        }
      }
    }

    /*
    Focuses the element.
    */
    focus() {
      this.el.focus();
    }

    /*
    Gets the value from the element.
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

    /*
    Set a value on the element.
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

    /*
    Add an error to the element.
    */
    addError(error) {
      this.errors.push(error);
      this.el.setAttribute(`unicorn:error:${error.code}`, error.message);
    }

    /*
    Remove all errors from the element.
    */
    removeErrors() {
      this.errors.forEach((error) => {
        this.el.removeAttribute(error.code);
      });

      this.errors = [];
    }
  }

  /*
  Initializes the Unicorn object.
  */
  unicorn.init = (_messageUrl) => {
    messageUrl = _messageUrl;
  };

  /*
  A simple shortcut for querySelector that everyone loves.
  */
  function $(selector, scope) {
    if (scope === undefined) {
      scope = document;
    }

    return scope.querySelector(selector);
  }

  /*
  Returns a function, that, as long as it continues to be invoked, will not
  be triggered. The function will be called after it stops being called for
  N milliseconds. If `immediate` is passed, trigger the function on the
  leading edge, instead of the trailing.

  Derived from underscore.js's implementation in https://davidwalsh.name/javascript-debounce-function.
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

  /*
  The function is executed the number of times it is called,
  but there is a fixed wait time before each execution.
  From https://medium.com/ghostcoder/debounce-vs-throttle-vs-queue-execution-bcde259768.
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

  /*
  Get the CSRF token used by Django.
  */
  function getCsrfToken() {
    const csrfElements = document.getElementsByName("csrfmiddlewaretoken");

    if (csrfElements) {
      return csrfElements[0].getAttribute("value");
    }

    throw Error("CSRF token is missing. Do you need to add {% csrf_token %}?");
  }

  /*
  Handles calling the message endpoint and merging the results into the document.
  */
  function sendMessage(componentName, componentRoot, unicornId, modelEls, action, debounceTime, callback) {
    function _sendMessage() {
      const syncUrl = `${messageUrl}/${componentName}`;
      const checksum = componentRoot.getAttribute("unicorn:checksum");
      const actionQueue = [action];

      const body = {
        id: unicornId,
        data: data[unicornId],
        checksum,
        actionQueue,
      };

      const headers = {
        Accept: "application/json",
        "X-Requested-With": "XMLHttpRequest",
      };
      headers[csrfTokenHeaderName] = getCsrfToken();

      fetch(syncUrl, {
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

          // Get the data from the response
          data[unicornId] = responseJson.data || {};
          errors[unicornId] = responseJson.errors || {};
          const { dom } = responseJson;

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

          // Store elements so that errors can be re-added after morphdom
          const elementsWithErrors = [];

          // Remove any unicorn validation messages before trying to merge with morphdom
          modelEls.forEach((element) => {
            // Re-initialize elements to make sure they are up to date
            element.init();

            elementsWithErrors.push(element);
            element.removeErrors();
          });

          // eslint-disable-next-line no-undef
          morphdom(componentRoot, dom, morphdomOptions);

          // Add unicorn validation messages from errors
          elementsWithErrors.forEach((element) => {
            Object.keys(errors[unicornId]).forEach((modelName) => {
              if (element.model.name === modelName) {
                const error = errors[unicornId][modelName][0];
                element.addError(error);
              }
            });
          });

          if (callback && typeof callback === "function") {
            callback();
          }
        })
        .catch((err) => {
          if (callback && typeof callback === "function") {
            callback(err);
          }
        });
    }

    if (debounceTime === -1) {
      // debounce(_sendMessage, 250, true)();
      queue(_sendMessage, 250)();
    } else {
      debounce(_sendMessage, debounceTime, false)();
    }
  }

  /*
  Traverses the DOM looking for child elements.
  */
  function walk(el, callback) {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_ELEMENT, null, false);

    while (walker.nextNode()) {
      // TODO: Handle sub-components?
      callback(walker.currentNode);
    }
  }

  /*
  Sets the value of an element. Tries to deal with HTML weirdnesses.
  */
  function setValue(unicornId, element) {
    const modelNamePieces = element.model.name.split(".");
    // Get local version of data in case have to traverse into a nested property
    let _data = data[unicornId];

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

  /*
  Sets all model values.

  `elementToExclude`: Prevent a particular element from being updated. Object example: `{id: 'elementId', key: 'elementKey'}`.
  */
  function setModelValues(unicornId, modelEls, elementToExclude) {
    elementToExclude = elementToExclude || {};

    modelEls.forEach((element) => {
      // Focus on the element that is being excluded since that is what triggered the update.
      // Prevents validation errors from stealing focus.
      if (elementToExclude.modelName === element.model.name) {
        element.focus();
      }

      if (element.id !== elementToExclude.id || element.key !== elementToExclude.key) {
        setValue(unicornId, element);
      }
    });
  }

  /*
  Calls the method for a particular component.
  */
  function callMethod(componentName, componentRoot, unicornId, modelEls, methodName, errCallback) {
    const action = { type: "callMethod", payload: { name: methodName, params: [] } };

    sendMessage(componentName, componentRoot, unicornId, modelEls, action, -1, (err) => {
      if (err && typeof errCallback === "function") {
        errCallback(err);
      } else {
        setModelValues(unicornId, modelEls);
      }
    });
  }

  /*
  Starts polling and handles stopping the polling if there is an error.
  */
  function startPolling(componentName, componentRoot, unicornId, modelEls, poll) {
    let timer;

    function handleError(err) {
      if (err && timer) {
        clearInterval(timer);
      }
    }

    // Call the method once before the timer starts
    callMethod(componentName, componentRoot, unicornId, modelEls, poll.method, handleError);

    timer = setInterval(callMethod, poll.timing, componentName, componentRoot, unicornId, modelEls, poll.method, handleError);
    return timer;
  }

  /*
  Initializes the component.
  */
  unicorn.componentInit = (args) => {
    const unicornId = args.id;
    const componentName = args.name;
    const componentRoot = $(`[unicorn\\:id="${unicornId}"]`);
    const modelEls = [];
    data[unicornId] = args.data;

    if (!componentRoot) {
      throw Error("No id found");
    }

    walk(componentRoot, (el) => {
      if (el.isSameNode(componentRoot)) {
        // Skip the component root element
        return;
      }

      const element = new Element(el);

      if (element.isUnicorn) {
        if (!isEmpty(element.model)) {
          modelEls.push(element);

          el.addEventListener(element.model.eventType, () => {
            const action = { type: "syncInput", payload: { name: element.model.name, value: element.getValue() } };

            sendMessage(componentName, componentRoot, unicornId, modelEls, action, element.model.debounceTime, (err) => {
              if (err) {
                console.error(err);
              } else {
                setModelValues(unicornId, modelEls, { id: element.id, key: element.key, modelName: element.model.name });
              }
            });
          });
        } else if (!isEmpty(element.poll)) {
          let timer;

          document.addEventListener("visibilitychange", () => {
            if (document.hidden) {
              if (timer) {
                clearInterval(timer);
              }
            } else {
              timer = startPolling(componentName, componentRoot, unicornId, modelEls, element.poll);
            }
          }, false);

          timer = startPolling(componentName, componentRoot, unicornId, modelEls, element.poll);
        } else if (!isEmpty(element.action)) {
          el.addEventListener(element.action.eventType, () => {
            callMethod(componentName, componentRoot, unicornId, modelEls, element.action.name);
          });
        }
      }
    });

    setModelValues(unicornId, modelEls);
  };

  /*
  Call an action on the specified component.
  */
  unicorn.call = (componentName, methodName) => {
    const componentRoot = $(`[unicorn\\:name="${componentName}"]`);
    const modelEls = [];

    if (!componentRoot) {
      throw Error("No component found for: ", componentName);
    }

    const unicornId = componentRoot.getAttribute("unicorn:id");

    if (!unicornId) {
      throw Error("No id found");
    }

    walk(componentRoot, (el) => {
      if (el.isSameNode(componentRoot)) {
        // Skip the component root element
        return;
      }

      const element = new Element(el);

      if (!isEmpty(element.model)) {
        modelEls.push(element);
      }
    });

    callMethod(componentName, componentRoot, unicornId, modelEls, methodName);
  };

  return unicorn;
})();
