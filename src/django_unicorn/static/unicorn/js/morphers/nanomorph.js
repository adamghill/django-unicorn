import nanomorph from "nanomorph";

export class NanomorphMorpher {
    constructor(options) {
        this.options = options;
    }

    morph(dom, htmlElement) {
        if (dom.nodeName === "SCRIPT" && htmlElement.nodeName === "SCRIPT") {
            const script = document.createElement("script");
            [...htmlElement.attributes].forEach((attr) => {
                script.setAttribute(attr.nodeName, attr.nodeValue);
            });

            script.innerHTML = htmlElement.innerHTML;
            dom.replaceWith(script);
        } else {
            return nanomorph(dom, htmlElement);
        }
    }
}
