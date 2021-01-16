import { Component } from "./component.js";
import { isEmpty } from "./utils.js";
import { components } from "./store.js";

let messageUrl = "";
const csrfTokenHeaderName = "X-CSRFToken";

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
  components[component.id] = component;

  component.setModelValues();
  component.setDbModelValues();
}

/**
 * Gets the component with the specified name or key.
 * Component keys are searched first, then names.
 *
 * @param {String} componentNameOrKey The name or key of the component to search for.
 */
export function getComponent(componentNameOrKey) {
  let component;

  Object.keys(components).forEach((id) => {
    if (isEmpty(component)) {
      const _component = components[id];

      if (_component.key === componentNameOrKey) {
        component = _component;
      }
    }
  });

  if (isEmpty(component)) {
    Object.keys(components).forEach((id) => {
      if (isEmpty(component)) {
        const _component = components[id];

        if (_component.name === componentNameOrKey) {
          component = _component;
        }
      }
    });
  }

  if (!component) {
    throw Error(`No component found for: ${componentNameOrKey}`);
  }

  return component;
}

/**
 * Call an action on the specified component.
 */
export function call(componentNameOrKey, methodName) {
  const component = getComponent(componentNameOrKey);

  component.callMethod(methodName, (err) => {
    console.error(err);
  });
}

/**
 * Gets the last return value.
 */
export function getReturnValue(componentNameOrKey) {
  const component = getComponent(componentNameOrKey);

  return component.return.value;
}
