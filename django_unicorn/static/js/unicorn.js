import { Component } from "./component.js";
import { isEmpty } from "./utils.js";

let messageUrl = "";
const csrfTokenHeaderName = "X-CSRFToken";
const components = {};

/**
 * Initializes the Unicorn object.
 */
export function init(_messageUrl) {
  messageUrl = _messageUrl;
}

/**
 * Initializes the component.
 */
export function componentInit(args) {
  args.messageUrl = messageUrl;
  args.csrfTokenHeaderName = csrfTokenHeaderName;

  const component = new Component(args);
  component.init();
  components[component.id] = component;

  component.setModelValues();
  component.setDbModelValues();
}

/**
 * Call an action on the specified component.
 */
export function call(componentName, methodName) {
  let component;

  Object.keys(components).forEach((id) => {
    if (isEmpty(component)) {
      const _component = components[id];

      if (_component.name === componentName) {
        component = _component;
      }
    }
  });

  if (!component) {
    throw Error("No component found for: ", componentName);
  }

  component.callMethod(methodName, (err) => {
    console.error(err);
  });
}
