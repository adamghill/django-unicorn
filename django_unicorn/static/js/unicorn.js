var Unicorn = (function () {
    var public = {};  // contains methods exposed in the Unicorn object
    var messageUrl = "";
    var csrfToken = getCsrfToken();
    var csrfTokenHeaderName = 'X-CSRFToken';
    var data = {};

    public.init = function (_messageUrl) {
        messageUrl = _messageUrl;
    }

    public.componentInit = function (args) {
        var unicornId = args.id;
        var componentName = args.name;
        var componentRoot = document.querySelector('[unicorn\\:id="' + unicornId + '"]');

        if (!componentRoot) {
            Error("No id found");
        }

        var modelEls = componentRoot.querySelectorAll('[unicorn\\:model]');

        modelEls.forEach(function (el) {
            var modelName = el.getAttribute("unicorn:model");

            if (data[modelName]) {
                if (el.type == "radio") {
                    if (el.value == data[modelName]) {
                        el.checked = true;
                    }
                } else if (el.type == "checkbox") {
                    el.checked = true;
                } else {
                    el.value = data[modelName];
                }
            }

            el.addEventListener("input", function (e) {
                eventListener(componentName, componentRoot, unicornId, el, modelName);
            });
        });
    };

    public.setData = function (_data) {
        data = _data;
    }

    function getCsrfToken() {
        var csrfElements = document.getElementsByName('csrfmiddlewaretoken');

        if (csrfElements.length > 0) {
            return csrfElements[0].getAttribute('value');
        }
    }

    function getValue(el) {
        var value = el.value;

        // Handle checkbox
        if (el.type.toLowerCase() == 'checkbox') {
            value = el.checked;
        }

        // Handle multiple select options
        if (el.type.toLowerCase() == 'select-multiple') {
            value = [];
            for (var i = 0; i < el.selectedOptions.length; i++) {
                value.push(el.selectedOptions[i].value);
            }
        }

        return value;
    }

    function eventListener(componentName, componentRoot, unicornId, el, modelName) {
        var debounceTime = 250;

        debounce(function () {
            var syncUrl = messageUrl + '/' + componentName;
            var value = getValue(el);
            var checksum = componentRoot.getAttribute("unicorn:checksum")

            actionQueue = [{ type: "syncInput", payload: { name: modelName, value: value } }]

            var body = {
                id: unicornId,
                data: data,
                checksum: checksum,
                actionQueue: actionQueue,
            };

            var headers = {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            }
            headers[csrfTokenHeaderName] = csrfToken

            fetch(syncUrl, {
                method: "POST",
                headers: headers,
                body: JSON.stringify(body),
            })
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    }
                })
                .then(responseJson => {
                    if (responseJson.error) {
                        console.error(responseJson.error);
                        return
                    }

                    public.setData(responseJson.data);
                    var dom = responseJson.dom;
                    var morphChanges = { changed: [], added: [], removed: [] };

                    var morphdomOptions = {
                        childrenOnly: false,

                        getNodeKey: node => {
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

                        onNodeDiscarded: node => {
                            morphChanges.removed.push(node)
                        },

                        onBeforeElUpdated: (from, to) => {
                            // Because morphdom also supports vDom nodes, it uses isSameNode to detect
                            // sameness. When dealing with DOM nodes, we want isEqualNode, otherwise
                            // isSameNode will ALWAYS return false.
                            if (from.isEqualNode(to)) {
                                return false;
                            }
                        },

                        onElUpdated: node => {
                            morphChanges.changed.push(node)
                        },

                        onNodeAdded: node => {
                            morphChanges.added.push(node)
                        }
                    }

                    morphdom(componentRoot, dom, morphdomOptions);
                });
        }, debounceTime)();
    }

    return public;
}());