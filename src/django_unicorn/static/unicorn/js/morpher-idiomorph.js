import { IdiomorphMorpher } from "./morphers/idiomorph.js";

export function getMorpher(morpherSettings) {
    return new IdiomorphMorpher(morpherSettings);
}
