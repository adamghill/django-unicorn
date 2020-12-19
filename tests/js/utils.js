import { JSDOM } from "jsdom";
import fetchMock from "fetch-mock";
import { Element } from "../../django_unicorn/static/js/element.js";
import { Component } from "../../django_unicorn/static/js/component.js";

/**
 * Gets a fake DOM document based on the passed-in HTML fragement.
 * @param {String} html HTML fragment.
 */
export function getDocument(html) {
  const dom = new JSDOM(html);

  return dom.window.document;
}

/**
 * Gets a HTMLElement based on the passed-in HTML fragement.
 * @param {String} html HTML fragment.
 * @param {String} querySelector Selector to use to get the element. Uses the `firstElementChild` if undefined.
 */
export function getEl(html, querySelector) {
  const document = getDocument(html);

  if (typeof querySelector === "undefined") {
    return document.body.firstElementChild;
  }

  return document.querySelector(querySelector);
}

/**
 * Gets a constructed `Element` based on the passed-in HTML fragement.
 * @param {String} html HTML fragment.
 * @param {String} querySelector Selector to use to get the element. Uses the `firstElementChild` if undefined.
 */
export function getElement(html, querySelector) {
  const el = getEl(html, querySelector);

  return new Element(el);
}

/**
 * Re-implements Treewalker which is not available in JSDOM.
 * Replaces the `walk` function that gets used by `Component` for unit tests.
 * @param {HTMLElement} el The first element to start at
 * @param {Function} callback Fired for each element that is found
 */
export function walkDOM(el, callback) {
  do {
    callback(el);

    if (el.hasChildNodes()) {
      walkDOM(el.firstChild, callback);
    }
    // eslint-disable-next-line no-cond-assign
  } while ((el = el.nextSibling));
}

/**
 * Gets a constructed `Component` based on the passed-in HTML fragement.
 * @param {String} html THe HTML fragment for the component.
 */
export function getComponent(html, id, name, data) {
  if (typeof html === "undefined") {
    html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <input unicorn:model='name'></input>
  <button unicorn:click='name="world"'></button>
</div>
    `;
  }

  html = `
<input type="hidden" name="csrfmiddlewaretoken" value="asdf">${html}
  `;

  if (typeof id === "undefined") {
    id = "5jypjiyb";
  }

  if (typeof name === "undefined") {
    name = "text-inputs";
  }

  if (typeof data === "undefined") {
    data = { name: "World" };
  }

  const document = getDocument(html);

  const mockHistory = { urls: [] };
  mockHistory.pushState = (state, title, url) => {
    mockHistory.urls.push(url);
  };
  mockHistory.get = () => {
    return mockHistory.urls[0];
  };

  const component = new Component({
    id,
    name,
    data,
    document,
    messageUrl: "test",
    walker: walkDOM,
    window: {
      document: { title: "" },
      history: mockHistory,
      location: { href: "" },
    },
  });

  const res = {
    id: "",
    dom: "",
    data: {},
    errors: {},
    redirect: {},
    return: {},
  };
  global.fetch = fetchMock.sandbox().mock().post("/test/text-inputs", res);

  return component;
}
