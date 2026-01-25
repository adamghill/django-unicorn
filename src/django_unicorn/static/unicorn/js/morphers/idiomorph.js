import { Idiomorph } from "idiomorph/dist/idiomorph.esm.js";

export class IdiomorphMorpher {
    constructor(options) {
        this.options = options;
    }

    morph(dom, htmlElement) {
        return Idiomorph.morph(dom, htmlElement, {
            morphStyle: 'innerHTML',
        });
    }
}
