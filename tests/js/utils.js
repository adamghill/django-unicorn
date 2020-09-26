import { JSDOM } from "jsdom";
import { Element } from "../../django_unicorn/static/js/element.js";

export function getElement(fragment, querySelector) {
  const dom = new JSDOM(fragment);
  const el = dom.window.document.querySelector(querySelector);

  return new Element(el);
}
