import { JSDOM } from "jsdom";
import { Element } from "../../django_unicorn/static/js/element.js";

export function getEl(fragment, querySelector) {
  const dom = new JSDOM(fragment);

  if (typeof querySelector === "undefined") {
    return dom.window.document.body.firstElementChild;
  }

  return dom.window.document.querySelector(querySelector);
}

export function getElement(fragment, querySelector) {
  const el = getEl(fragment, querySelector);

  return new Element(el);
}
