import { Component } from "./component.js";
import { isEmpty, hasValue } from "./utils.js";
import { components, lifecycleEvents } from "./store.js";

let messageUrl = "";
let reloadScriptElements = false;
let csrfTokenHeaderName = "X-CSRFToken";

/**
 * Initializes the Unicorn object.
 */
export function init(_messageUrl, _csrfTokenHeaderName, _reloadScriptElements) {
  messageUrl = _messageUrl;
  reloadScriptElements = _reloadScriptElements || false;

  if (hasValue(_csrfTokenHeaderName)) {
    csrfTokenHeaderName = _csrfTokenHeaderName;
  }

  return {
    messageUrl,
    csrfTokenHeaderName,
    reloadScriptElements,
  };
}

/**
 * Initializes the component.
 */
export function componentInit(args) {
  args.messageUrl = messageUrl;
  args.csrfTokenHeaderName = csrfTokenHeaderName;
  args.reloadScriptElements = reloadScriptElements;

  const component = new Component(args);
  components[component.id] = component;

  component.setModelValues();
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
export function call(componentNameOrKey, methodName, ...args) {
  const component = getComponent(componentNameOrKey);
  let argString = "";

  args.forEach((arg) => {
    if (typeof arg !== "undefined") {
      if (typeof arg === "string") {
        argString = `${argString}'${arg}', `;
      } else {
        argString = `${argString}${arg}, `;
      }
    }
  });

  if (argString) {
    argString = argString.slice(0, -2);
    methodName = `${methodName}(${argString})`;
  }

  component.callMethod(methodName, 0, null, (err) => {
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

/**
 * Adds an event listener for particular events.
 * @param {String} eventName The event to register under. Current events are: `updated`.
 * @param {Function} callback Function to call when the event gets fired.
 */
export function addEventListener(eventName, callback) {
  if (!(eventName in lifecycleEvents)) {
    lifecycleEvents[eventName] = [];
  }

  lifecycleEvents[eventName].push(callback);
}

/**
 * Trigger a component update by dispatching an event for a particular element.
 */
export function trigger(componentNameOrKey, elementKey) {
  const component = getComponent(componentNameOrKey);
  component.trigger(elementKey);
}
