const Unicorn = (() => {
  const unicorn = {}; // contains all methods exposed publicly in the Unicorn object
  let messageUrl = "";
  const csrfTokenHeaderName = "X-CSRFToken";
  let data = {};

  /*
  Checks if a string has the search text.
  */
  function contains(str, search) {
    return str.indexOf(search) > -1;
  }

  /*
  Encapsulate looking at element attributes for anything Unicorn-related.
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
      this.modifiers = {};
      this.eventType = null;

      this.init();
    }

    init() {
      if (contains(this.name, "unicorn:")) {
        this.isUnicorn = true;

        if (contains(this.name, "unicorn:model")) {
          this.isModel = true;
        } else if (contains(this.name, "unicorn:poll")) {
          this.isPoll = true;
        } else if (contains(this.name, "unicorn:key")) {
          this.isKey = true;
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
  Initializes the Unicorn object.
  */
  unicorn.init = (_messageUrl) => {
    messageUrl = _messageUrl;
  };

  /*
  Gets the value of the `unicorn:model` attribute from an element even if there are modifiers.
  */
  function getModelName(el) {
    for (let i = 0; i < el.attributes.length; i++) {
      const attribute = el.attributes[i];

      if (attribute.name.indexOf("unicorn:model") > -1) {
        return el.getAttribute(attribute.name);
      }
    }
  }

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
  Get a value from an element. Tries to deal with HTML weirdnesses.
  */
  function getValue(el) {
    let { value } = el;

    if (el.type.toLowerCase() === "checkbox") {
      // Handle checkbox
      value = el.checked;
    } else if (el.type.toLowerCase() === "select-multiple") {
      // Handle multiple select options
      value = [];
      for (let i = 0; i < el.selectedOptions.length; i++) {
        value.push(el.selectedOptions[i].value);
      }
    }

    return value;
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
  Get the CSRF token used by Django.
  */
  function getCsrfToken() {
    let csrfToken = "";
    const csrfElements = document.getElementsByName("csrfmiddlewaretoken");

    if (csrfElements) {
      csrfToken = csrfElements[0].getAttribute("value");
    }

    if (!csrfToken) {
      Error("CSRF token is missing. Do you need to add {% csrf_token %}?");
    }

    return csrfToken;
  }

  /*
  Handles calling the message endpoint and merging the results into the document.
  */
  function sendMessage(componentName, componentRoot, unicornId, action, debounceTime, callback) {
    function _sendMessage() {
      const syncUrl = `${messageUrl}/${componentName}`;
      const checksum = componentRoot.getAttribute("unicorn:checksum");
      const actionQueue = [action];

      const body = {
        id: unicornId,
        data,
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

          Error(`Error when getting response: ${response.statusText} (${response.status})`);
        })
        .then((responseJson) => {
          if (!responseJson) {
            return;
          }

          if (responseJson.error) {
            Error(responseJson.error);
          }

          unicorn.setData(responseJson.data);
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

          morphdom(componentRoot, dom, morphdomOptions);

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
      debounce(_sendMessage, 250, true)();
    } else {
      debounce(_sendMessage, debounceTime, false)();
    }
  }

  /*
  Traverse the DOM looking for child elements.
  */
  function walk(el, callback) {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_ELEMENT, null, false);

    while (walker.nextNode()) {
      // TODO: Handle sub-components
      callback(walker.currentNode);
    }
  }

  /*
  Sets the value of an element. Tries to deal with HTML weirdnesses.
  */
  function setValue(el, modelName) {
    const modelNamePieces = modelName.split(".");
    // Get local version of data in case have to traverse into a nested property
    let _data = data;

    for (let i = 0; i < modelNamePieces.length; i++) {
      const modelNamePiece = modelNamePieces[i];

      if (Object.prototype.hasOwnProperty.call(_data, modelNamePiece)) {
        if (i === modelNamePieces.length - 1) {
          if (el.type.toLowerCase() === "radio") {
            // Handle radio buttons
            if (el.value === _data[modelNamePiece]) {
              el.checked = true;
            }
          } else if (el.type.toLowerCase() === "checkbox") {
            // Handle checkboxes
            el.checked = _data[modelNamePiece];
          } else {
            el.value = _data[modelNamePiece];
          }
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
  function setModelValues(modelEls, elementToExclude) {
    if (typeof elementToExclude === "undefined" || !elementToExclude) {
      elementToExclude = {};
    }

    modelEls.forEach((modelEl) => {
      const modelKey = modelEl.getAttribute("unicorn:key");

      if (modelEl.id !== elementToExclude.id || modelKey !== elementToExclude.key) {
        const modelName = getModelName(modelEl);
        setValue(modelEl, modelName);
      }
    });
  }

  /*
  Calls the method for a particular component.
  */
  function callMethod(componentName, componentRoot, unicornId, methodName, modelEls, errCallback) {
    const action = { type: "callMethod", payload: { name: methodName, params: [] } };

    sendMessage(componentName, componentRoot, unicornId, action, -1, (err) => {
      if (err && typeof errCallback === "function") {
        errCallback(err);
      } else {
        setModelValues(modelEls);
      }
    });
  }

  /*
  Starts polling and handles stopping the polling if there is an error.
  */
  function startPolling(componentName, componentRoot, unicornId, methodName, modelEls, pollTiming) {
    let timer;

    function handleError(err) {
      if (err && timer) {
        clearInterval(timer);
      }
    }

    // Call the method before the timer kicks in
    callMethod(componentName, componentRoot, unicornId, methodName, modelEls, handleError);

    timer = setInterval(callMethod, pollTiming, componentName, componentRoot, unicornId, methodName, modelEls, handleError);
    return timer;
  }

  /*
  Initializes the component.
  */
  unicorn.componentInit = (args) => {
    const unicornId = args.id;
    const componentName = args.name;
    const componentRoot = $(`[unicorn\\:id="${unicornId}"]`);

    if (!componentRoot) {
      Error("No id found");
    }

    const modelEls = [];

    walk(componentRoot, (el) => {
      if (el.isSameNode(componentRoot)) {
        // Skip the component root element
        return;
      }

      for (let i = 0; i < el.attributes.length; i++) {
        const attribute = new Attribute(el.attributes[i]);

        if (attribute.isUnicorn) {
          if (attribute.isModel) {
            modelEls.push(el);

            const modelEventType = attribute.modifiers.lazy ? "blur" : "input";
            const debounceTime = attribute.modifiers.debounce ? parseInt(attribute.modifiers.debounce, 10) || -1 : -1;
            const modelName = attribute.value;

            el.addEventListener(modelEventType, () => {
              const value = getValue(el);
              const { id } = el;
              const key = el.getAttribute("unicorn:key");
              const action = { type: "syncInput", payload: { name: modelName, value } };

              sendMessage(componentName, componentRoot, unicornId, action, debounceTime, () => {
                setModelValues(modelEls, { id, key });
              });
            });
          } else if (attribute.isPoll) {
            const methodName = attribute.value ? attribute.value : "refresh";
            let timer;
            let pollTiming = 2000;

            if (attribute.modifiers) {
              pollTiming = parseInt(Object.keys(attribute.modifiers)[0], 10) || 2000;
            }

            // Only listen to visibility if browser supports it
            document.addEventListener("visibilitychange", () => {
              if (document.hidden) {
                if (timer) {
                  clearInterval(timer);
                }
              } else {
                timer = startPolling(componentName, componentRoot, unicornId, methodName, modelEls, pollTiming);
              }
            }, false);

            timer = startPolling(componentName, componentRoot, unicornId, methodName, modelEls, pollTiming);
          } else {
            el.addEventListener(attribute.eventType, () => {
              callMethod(componentName, componentRoot, unicornId, attribute.value, modelEls);
            });
          }
        }
      }
    });

    setModelValues(modelEls);
  };

  /*
  Sets the data on the Unicorn object.
  */
  unicorn.setData = (_data) => {
    data = _data;
  };

  /*
  Call an action on the specified component.
  */
  unicorn.call = (componentName, methodName) => {
    const componentRoot = $(`[unicorn\\:name="${componentName}"]`);
    const modelEls = [];

    if (!componentRoot) {
      Error("No component found for: ", componentName);
    }

    const unicornId = componentRoot.getAttribute("unicorn:id");

    if (!unicornId) {
      Error("No id found");
    }

    walk(componentRoot, (el) => {
      if (el.isSameNode(componentRoot)) {
        // Skip the component root element
        return;
      }

      if (getModelName(el)) {
        modelEls.push(el);
      }
    });

    callMethod(componentName, componentRoot, unicornId, methodName, modelEls);
  };

  return unicorn;
})();
