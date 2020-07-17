function $(selector, scope) {
    if (scope == undefined) {
        scope = document;
    }

    return scope.querySelector(selector);
}

function $$(selector, scope) {
    if (scope == undefined) {
        scope = document;
    }

    return Array.from(scope.querySelectorAll(selector));
}

function listen(type, selector, callback) {
    document.addEventListener(type, function (event) {
        var target = event.target.closest(selector);

        if (target) {
            callback(event, target);
        }
    });
}