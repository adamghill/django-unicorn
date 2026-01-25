import { NanomorphMorpher } from "./morphers/nanomorph.js";

export function getMorpher(morpherSettings) {
    return new NanomorphMorpher(morpherSettings);
}
