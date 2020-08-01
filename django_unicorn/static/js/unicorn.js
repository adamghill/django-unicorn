var Unicorn = (function () {
    var unicorn = {};  // contains methods exposed publicly in the Unicorn object
    var messageUrl = "";
    var csrfTokenHeaderName = 'X-CSRFToken';
    var data = {};

    unicorn.init = function (_messageUrl) {
        messageUrl = _messageUrl;
    }

    function setModelValues(modelEls, elementIdToExclude) {
        modelEls.forEach(function (modelEl) {
            if (typeof elementIdToExclude === 'undefined' || modelEl.id != elementIdToExclude) {
                var modelName = modelEl.getAttribute("unicorn:model");
                setValue(modelEl, modelName);
            }
        });
    }

    unicorn.componentInit = function (args) {
        var unicornId = args.id;
        var componentName = args.name;
        var componentRoot = document.querySelector('[unicorn\\:id="' + unicornId + '"]');
        var modelELs = componentRoot.querySelectorAll('[unicorn\\:model]');

        if (!componentRoot) {
            Error("No id found");
        }

        setModelValues(modelELs);

        listen("input", "[unicorn\\:model]", (event, el) => {
            var modelName = el.getAttribute("unicorn:model");
            var value = getValue(el);
            var id = el.id;
            var action = { type: "syncInput", payload: { name: modelName, value: value } };

            eventListener(componentName, componentRoot, unicornId, action, function () {
                setModelValues(modelELs, id);
            });
        });

        listen("click", "[unicorn\\:click]", function (event, el) {
            var methodName = el.getAttribute("unicorn:click");
            var action = { type: "callMethod", payload: { name: methodName, params: [] } };

            eventListener(componentName, componentRoot, unicornId, action, function () {
                setModelValues(modelELs);
            });
        });
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

    function setValue(el, modelName) {
        if (data[modelName]) {
            if (el.type.toLowerCase() == "radio") {
                // Handle radio buttons
                if (el.value == data[modelName]) {
                    el.checked = true;
                }
            } else if (el.type.toLowerCase() == "checkbox") {
                // Handle checkboxes
                el.checked = true;
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
                    var morphChanges = { changed: [], added: [], removed: [] };

                    var morphdomOptions = {
                        childrenOnly: false,
                        getNodeKey: function (node) {
                            if (node.attributes) {
                                var key = node.getAttribute("unicorn:key") || node.getAttribute("unicorn:id") || node.id;

                                if (key) {
                                    return node.getAttribute("unicorn:key") || node.getAttribute("unicorn:id") || node.id;
                                }
                            }

                            if (node.id) {
                                return node.id;
                            }
                        },
                        onNodeDiscarded: function (node) {
                            morphChanges.removed.push(node)
                        },
                        onBeforeElUpdated: function (fromEl, toEl) {
                            // Because morphdom also supports vDom nodes, it uses isSameNode to detect
                            // sameness. When dealing with DOM nodes, we want isEqualNode, otherwise
                            // isSameNode will ALWAYS return false.
                            if (fromEl.isEqualNode(toEl)) {
                                return false;
                            }
                        },
                        onElUpdated: function (node) {
                            morphChanges.changed.push(node)
                        },
                        onNodeAdded: function (node) {
                            morphChanges.added.push(node)
                        }
                    }

                    morphdom(componentRoot, dom, morphdomOptions);

                    if (callback && callback != undefined) {
                        callback();
                    }
                });
        }, debounceTime)();
    }

    return unicorn;
}());