function $(selector, scope = document) {
    return scope.querySelector(selector);
}

function $$(selector, scope = document) {
    return Array.from(scope.querySelectorAll(selector));
}

function listen(type, selector, callback) {
    document.addEventListener(type, event => {
        const target = event.target.closest(selector);

        if (target) {
            callback(event, target);
        }
    });
}