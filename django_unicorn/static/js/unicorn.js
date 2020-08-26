var Unicorn = (function () {
    var unicorn = {};  // contains all methods exposed publicly in the Unicorn object
    var messageUrl = "";
    var csrfTokenHeaderName = 'X-CSRFToken';
    var data = {};

    /*
    Initializes the Unicorn object.
    */
    unicorn.init = function (_messageUrl) {
        messageUrl = _messageUrl;
    }

    /*
    Gets the value of the `unicorn:model` attribute from an element even if there are modifiers.
    */
    function getModelName(el) {
        for (var i = 0; i < el.attributes.length; i++) {
            var attribute = el.attributes[i];

            if (attribute.name.indexOf("unicorn:model") > -1) {
                return el.getAttribute(attribute.name);
            }
        }
    }

    /*
    Initializes the component.
    */
    unicorn.componentInit = function (args) {
        var unicornId = args.id;
        var componentName = args.name;
        var componentRoot = $('[unicorn\\:id="' + unicornId + '"]');

        if (!componentRoot) {
            Error("No id found");
        }

        var modelEls = [];

        walk(componentRoot, (el) => {
            if (el.isSameNode(componentRoot)) {
                // Skip the component root element
                return
            }

            for (var i = 0; i < el.attributes.length; i++) {
                var attribute = el.attributes[i];
                var unicornIdx = attribute.name.indexOf("unicorn:");

                if (unicornIdx > -1) {
                    if (attribute.name.indexOf("unicorn:model") > -1) {
                        modelEls.push(el);

                        var attributeName = attribute.name;
                        var modifiers = attributeName.replace("unicorn:model.", "").split(".");
                        var attributeModifiers = {};

                        modifiers.forEach(modifier => {
                            if (modifier != "unicorn:model") {
                                var modifierArgs = modifier.split("-");
                                attributeModifiers[modifierArgs[0]] = modifierArgs.length > 1 ? modifierArgs[1] : true;
                            }
                        })
                        var modelEventType = attributeModifiers.lazy ? "blur" : "input";
                        var debounceTime = attributeModifiers.debounce ? parseInt(attributeModifiers.debounce) : -1;

                        el.addEventListener(modelEventType, event => {
                            var modelName = el.getAttribute(attributeName);
                            var value = getValue(el);
                            var id = el.id;
                            var key = el.getAttribute("unicorn:key");
                            var action = { type: "syncInput", payload: { name: modelName, value: value } };

                            sendMessage(componentName, componentRoot, unicornId, action, debounceTime, function () {
                                setModelValues(modelEls, { id: id, key: key });
                            });
                        });
                    } else {
                        var eventType = attribute.name.replace("unicorn:", "");
                        var methodName = attribute.value;

                        el.addEventListener(eventType, event => {
                            var action = { type: "callMethod", payload: { name: methodName, params: [] } };

                            sendMessage(componentName, componentRoot, unicornId, action, 0, function () {
                                setModelValues(modelEls);
                            });
                        });
                    }
                }
            };
        });

        setModelValues(modelEls);
    };

    /*
    Sets the data on the Unicorn object.
    */
    unicorn.setData = function (_data) {
        data = _data;
    }

    /*
    Call an action on the specified component.
    */
    unicorn.call = function (componentName, methodName) {
        var componentRoot = $('[unicorn\\:name="' + componentName + '"]');

        if (!componentRoot) {
            Error("No component found for: ", componentName);
        }

        var unicornId = componentRoot.getAttribute('unicorn:id');

        if (!unicornId) {
            Error("No id found");
        }

        var action = { type: "callMethod", payload: { name: methodName, params: [] } };
        var modelEls = [];

        walk(componentRoot, (el) => {
            if (el.isSameNode(componentRoot)) {
                // Skip the component root element
                return
            }

            if (getModelName(el)) {
                modelEls.push(el);
            }
        });

        sendMessage(componentName, componentRoot, unicornId, action, 0, function () {
            setModelValues(modelEls);
        });
    }

    /*
    Get the CSRF token used by Django.
    */
    function getCsrfToken() {
        var csrfToken = "";
        var csrfElements = document.getElementsByName('csrfmiddlewaretoken');

        if (csrfElements.length > 0) {
            csrfToken = csrfElements[0].getAttribute('value');
        }

        if (!csrfToken) {
            console.error("CSRF token is missing. Do you need to add {% csrf_token %}?");
        }

        return csrfToken;
    }

    /*
    Traverse the DOM looking for child elements.
    */
    function walk(el, callback) {
        var walker = document.createTreeWalker(el, NodeFilter.SHOW_ELEMENT, null, false);

        while (walker.nextNode()) {
            // TODO: Handle sub-components
            callback(walker.currentNode);
        }
    }

    /*
    Get a value from an element. Tries to deal with HTML weirdnesses.
    */
    function getValue(el) {
        var value = el.value;

        // Handle checkbox
        if (el.type.toLowerCase() == "checkbox") {
            value = el.checked;
        }

        // Handle multiple select options
        if (el.type.toLowerCase() == "select-multiple") {
            value = [];
            for (var i = 0; i < el.selectedOptions.length; i++) {
                value.push(el.selectedOptions[i].value);
            }
        }

        return value;
    }

    /*
    Sets all model values.
    
    `elementToExclude`: Prevent a particular element from being updated. Object example: `{id: 'elementId', key: 'elementKey'}`.
    */
    function setModelValues(modelEls, elementToExclude) {
        if (typeof elementToExclude === "undefined" || !elementToExclude) {
            elementToExclude = {};
        }

        modelEls.forEach(function (modelEl) {
            var modelKey = modelEl.getAttribute("unicorn:key");

            if (modelEl.id != elementToExclude.id || modelKey != elementToExclude.key) {
                var modelName = getModelName(modelEl);
                setValue(modelEl, modelName);
            }
        });
    }

    /*
    Sets the value of an element. Tries to deal with HTML weirdnesses.
    */
    function setValue(el, modelName) {
        var modelNamePieces = modelName.split(".");
        // Get local version of data in case have to traverse into a nested property
        var _data = data;

        for (var i = 0; i < modelNamePieces.length; i++) {
            var modelNamePiece = modelNamePieces[i];

            if (_data.hasOwnProperty(modelNamePiece)) {
                if (i == modelNamePieces.length - 1) {
                    if (el.type.toLowerCase() === "radio") {
                        // Handle radio buttons
                        if (el.value == _data[modelNamePiece]) {
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
    Handles calling the message endpoint and merging the results into the document.
    */
    function sendMessage(componentName, componentRoot, unicornId, action, debounceTime, callback) {
        function _sendMessage() {
            var syncUrl = messageUrl + '/' + componentName;
            var checksum = componentRoot.getAttribute("unicorn:checksum");
            var actionQueue = [action];

            var body = {
                id: unicornId,
                data: data,
                checksum: checksum,
                actionQueue: actionQueue,
            };

            var headers = {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            };
            headers[csrfTokenHeaderName] = getCsrfToken();

            fetch(syncUrl, {
                method: "POST",
                headers: headers,
                body: JSON.stringify(body),
            })
                .then(function (response) {
                    if (response.ok) {
                        return response.json();
                    } else {
                        console.error("Error when getting response: " + response.statusText + " (" + response.status + ")");
                    }
                })
                .then(function (responseJson) {
                    if (!responseJson) {
                        return
                    }

                    if (responseJson.error) {
                        console.error(responseJson.error);
                        return
                    }

                    unicorn.setData(responseJson.data);
                    var dom = responseJson.dom;

                    var morphdomOptions = {
                        childrenOnly: false,
                        getNodeKey: function (node) {
                            // A node's unique identifier. Used to rearrange elements rather than
                            // creating and destroying an element that already exists. 
                            if (node.attributes) {
                                var key = node.getAttribute("unicorn:key") || node.id;

                                if (key) {
                                    return key;
                                }
                            }
                        },
                        onBeforeElUpdated: function (fromEl, toEl) {
                            // Because morphdom also supports vDom nodes, it uses isSameNode to detect
                            // sameness. When dealing with DOM nodes, we want isEqualNode, otherwise
                            // isSameNode will ALWAYS return false.
                            if (fromEl.isEqualNode(toEl)) {
                                return false;
                            }
                        },
                    }

                    morphdom(componentRoot, dom, morphdomOptions);

                    if (callback && typeof callback === "function") {
                        callback();
                    }
                });
        }

        if (debounceTime == -1) {
            queue(_sendMessage, 250)();
        } else {
            debounce(_sendMessage, debounceTime)();
        }
    }

    /*
    A simple shortcut for querySelector that everyone loves.
    */
    function $(selector, scope) {
        if (scope == undefined) {
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
        var timeout;

        if (typeof immediate == undefined) {
            immediate = true;
        }

        return function () {
            var context = this, args = arguments;
            var later = function () {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };

            var callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);

            if (callNow) func.apply(context, args);
        };
    };

    /*
    The function is executed the number of times it is called,
    but there is a fixed wait time before each execution.
    From https://medium.com/ghostcoder/debounce-vs-throttle-vs-queue-execution-bcde259768.
    */
    var funcQueue = [];
    function queue(func, waitTime) {
        var isWaiting;

        var executeFunc = function (params) {
            isWaiting = true;
            func(params);
            setTimeout(play, waitTime);
        };

        var play = function () {
            isWaiting = false;
            if (funcQueue.length) {
                var params = funcQueue.shift();
                executeFunc(params);
            }
        };

        return function (params) {
            if (isWaiting) {
                funcQueue.push(params);
            } else {
                executeFunc(params);
            }
        }
    };

    /*
    Stupid method because context switches are hard.
    */
    function print(msg) {
        var args = [].slice.apply(arguments).slice(1);
        console.log(msg, ...args);
    }

    return unicorn;
}());