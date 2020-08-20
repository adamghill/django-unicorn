var Unicorn = (function () {
    var unicorn = {};  // contains all methods exposed publicly in the Unicorn object
    var messageUrl = "";
    var csrfTokenHeaderName = 'X-CSRFToken';
    var data = {};

    unicorn.init = function (_messageUrl) {
        messageUrl = _messageUrl;
    }

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
                    if (attribute.name == "unicorn:model") {
                        modelEls.push(el);

                        el.addEventListener("input", event => {
                            var modelName = el.getAttribute("unicorn:model");
                            var value = getValue(el);
                            var id = el.id;
                            var key = el.getAttribute("unicorn:key");
                            var action = { type: "syncInput", payload: { name: modelName, value: value } };

                            eventListener(componentName, componentRoot, unicornId, action, function () {
                                setModelValues(modelEls, { id: id, key: key });
                            });
                        });
                    } else {
                        var eventType = attribute.name.replace("unicorn:", "");
                        var methodName = attribute.value;

                        el.addEventListener(eventType, event => {
                            var action = { type: "callMethod", payload: { name: methodName, params: [] } };

                            eventListener(componentName, componentRoot, unicornId, action, function () {
                                setModelValues(modelEls);
                            });
                        });
                    }
                }
            };
        });

        setModelValues(modelEls);
    };

    unicorn.setData = function (_data) {
        data = _data;
    }

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

    function setModelValues(modelEls, elementToExclude) {
        if (typeof elementToExclude === "undefined" || !elementToExclude) {
            elementToExclude = {};
        }

        modelEls.forEach(function (modelEl) {
            var modelKey = modelEl.getAttribute("unicorn:key");

            if (modelEl.id != elementToExclude.id || modelKey != elementToExclude.key) {
                var modelName = modelEl.getAttribute("unicorn:model");
                setValue(modelEl, modelName);
            }
        });
    }

    function setValue(el, modelName) {
        if (data.hasOwnProperty(modelName)) {
            if (el.type.toLowerCase() == "radio") {
                // Handle radio buttons
                if (el.value == data[modelName]) {
                    el.checked = true;
                }
            } else if (el.type.toLowerCase() == "checkbox") {
                // Handle checkboxes
                el.checked = data[modelName];
            } else {
                el.value = data[modelName];
            }
        }
    }

    function eventListener(componentName, componentRoot, unicornId, action, callback) {
        var debounceTime = 250;

        debounce(function () {
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
        }, debounceTime)();
    }

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

    return unicorn;
}());