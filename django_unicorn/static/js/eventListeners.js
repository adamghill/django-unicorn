import {
  $,
  args,
  generateDbKey,
  hasValue,
  isEmpty,
  toKebabCase,
} from "./utils.js";
import { Element } from "./element.js";

/**
 * Handles loading elements in the component.
 * @param {Component} component Component.
 * @param {Element} targetElement Targetted element.
 */
function handleLoading(component, targetElement) {
  targetElement.handleLoading();

  // Look at all elements with a loading attribute
  component.loadingEls.forEach((loadingElement) => {
    if (loadingElement.target) {
      let targetedEl = $(`#${loadingElement.target}`, component.root);

      if (!targetedEl) {
        component.keyEls.forEach((keyElement) => {
          if (!targetedEl && keyElement.key === loadingElement.target) {
            targetedEl = keyElement.el;
          }
        });
      }

      if (targetedEl) {
        if (targetElement.el.isSameNode(targetedEl)) {
          if (loadingElement.loading.hide) {
            loadingElement.hide();
          } else if (loadingElement.loading.show) {
            loadingElement.show();
          }
        }
      }
    } else if (loadingElement.loading.hide) {
      loadingElement.hide();
    } else if (loadingElement.loading.show) {
      loadingElement.show();
    }
  });
}

/**
 * Parse arguments and deal with nested data.
 *
 * // <button u:click="test($returnValue.hello.trim())">Test</button>
 * let data = {hello: " world "};
 * let output = parseEventArg(data, "$returnValue.hello.trim()");
 * // output is 'world'
 *
 * @param {Object} data The data that should be parsed.
 * @param {String} arg The argument to the function.
 * @param {String} specialArgName The special argument (starts with a $).
 */
function parseEventArg(data, arg, specialArgName) {
  // Remove any extra whitespace, everything before and including "$event", and the ending paren
  arg = arg
    .trim()
    .slice(arg.indexOf(specialArgName) + specialArgName.length)
    .trim();

  arg.split(".").forEach((piece) => {
    piece = piece.trim();

    if (piece) {
      // TODO: Handle method calls with args
      if (piece.endsWith("()")) {
        // method call
        const methodName = piece.slice(0, piece.length - 2);
        data = data[methodName]();
      } else if (hasValue(data[piece])) {
        data = data[piece];
      } else {
        throw Error(`'${piece}' could not be retrieved`);
      }
    }
  });

  if (typeof data === "string") {
    // Wrap strings in quotes
    data = `"${data}"`;
  }

  return data;
}

/**
 * Adds an action event listener to the document for each type of event (e.g. click, keyup, etc).
 * Added at the document level because validation errors would sometimes remove the
 * events when attached directly to the element.
 * @param {Component} component Component that contains the element.
 * @param {string} eventType Event type to listen for.
 */
export function addActionEventListener(component, eventType) {
  component.document.addEventListener(eventType, (event) => {
    let targetElement = new Element(event.target);

    // Make sure that the target element is a unicorn element.
    if (targetElement && !targetElement.isUnicorn) {
      targetElement = targetElement.getUnicornParent();
    }

    if (
      targetElement &&
      targetElement.isUnicorn &&
      targetElement.actions.length > 0
    ) {
      component.actionEvents[eventType].forEach((actionEvent) => {
        const { action } = actionEvent;
        const { element } = actionEvent;

        // TOD: Check why the targetElement needs to check isSameNode OR has the same
        // key/id since `isSameNode` won't always work
        if (targetElement.isSame(element) || targetElement.isSameId(element)) {
          // Add the value of any child element of the target that is a lazy model to the action queue
          // Handles situations similar to https://github.com/livewire/livewire/issues/528
          component.walker(element.el, (childEl) => {
            const modelElsInTargetScope = component.modelEls.filter((e) =>
              e.isSameEl(childEl)
            );

            modelElsInTargetScope.forEach((modelElement) => {
              if (hasValue(modelElement.model) && modelElement.model.isLazy) {
                const actionForQueue = {
                  type: "syncInput",
                  payload: {
                    name: modelElement.model.name,
                    value: modelElement.getValue(),
                  },
                };
                component.actionQueue.push(actionForQueue);
              }
            });

            const dbElsInTargetScope = component.dbEls.filter((e) =>
              e.el.isSameNode(childEl)
            );

            dbElsInTargetScope.forEach((dbElement) => {
              if (hasValue(dbElement.model) && dbElement.model.isLazy) {
                const actionForQueue = {
                  type: "dbInput",
                  payload: {
                    model: dbElement.model.name,
                    db: dbElement.db.name,
                    pk: dbElement.db.pk,
                    fields: {},
                  },
                };
                actionForQueue.payload.fields[
                  dbElement.field.name
                ] = dbElement.getValue();

                component.actionQueue.push(actionForQueue);
              }
            });
          });

          if (action.isPrevent) {
            event.preventDefault();
          }

          if (action.isStop) {
            event.stopPropagation();
          }

          if (action.isDiscard) {
            // Remove all existing action events in the queue
            component.actionQueue = [];
          }

          // Handle special arguments (e.g. $event)
          args(action.name).forEach((eventArg) => {
            if (eventArg.startsWith("$event")) {
              try {
                const data = parseEventArg(event, eventArg, "$event");
                action.name = action.name.replace(eventArg, data);
              } catch (err) {
                // console.error(err);
                action.name = action.name.replace(eventArg, "");
              }
            } else if (eventArg.startsWith("$returnValue")) {
              if (
                hasValue(component.return) &&
                hasValue(component.return.value)
              ) {
                try {
                  const data = parseEventArg(
                    component.return.value,
                    eventArg,
                    "$returnValue"
                  );
                  action.name = action.name.replace(eventArg, data);
                } catch (err) {
                  action.name = action.name.replace(eventArg, "");
                }
              } else {
                action.name = action.name.replace(eventArg, "");
              }
            } else if (eventArg === "$model") {
              const db = {};
              let elToCheck = targetElement;

              while (elToCheck.parent && (isEmpty(db.name) || isEmpty(db.pk))) {
                if (elToCheck.db.name) {
                  db.name = elToCheck.db.name;
                }

                if (elToCheck.db.pk) {
                  db.pk = elToCheck.db.pk;
                }

                if (elToCheck.isRoot()) {
                  break;
                }

                elToCheck = elToCheck.parent;
              }

              if (db.name && db.pk) {
                action.name = action.name.replace(
                  "$model",
                  JSON.stringify({
                    pk: db.pk,
                    name: db.name,
                  })
                );
              }
            }
          });

          if (action.key) {
            if (action.key === toKebabCase(event.key)) {
              handleLoading(component, targetElement);
              component.callMethod(action.name);
            }
          } else {
            handleLoading(component, targetElement);
            component.callMethod(action.name);
          }
        }
      });
    }
  });
}

/**
 * Adds a model event listener to the element.
 * @param {Component} component Component that contains the element.
 * @param {Element} Element that will get the event attached.
 * @param {string} eventType Event type to listen for. Optional; will use `model.eventType` by default.
 */
export function addModelEventListener(component, element, eventType) {
  eventType = eventType || element.model.eventType;
  element.events.push(eventType);
  const { el } = element;

  el.addEventListener(eventType, (event) => {
    let isDirty = false;

    if (component.data[element.model.name] !== element.getValue()) {
      isDirty = true;
      element.handleDirty();
    } else {
      element.handleDirty(true);
    }

    if (element.model.isLazy) {
      // Lazy models fire an input and blur so that the dirty check above works as expected.
      // This will prevent the input event from doing anything.
      if (eventType === "input") {
        return;
      }

      // Lazy non-dirty elements can bail
      if (!isDirty) {
        return;
      }
    }

    const action = {
      type: "syncInput",
      payload: {
        name: element.model.name,
        value: element.getValue(),
      },
    };

    if (!component.lastTriggeringElements.some((e) => e.isSame(element))) {
      component.lastTriggeringElements.push(element);
    }

    if (element.model.isDefer) {
      let foundActionIdx = -1;

      // Update the existing action with the current value
      component.actionQueue.forEach((a, idx) => {
        if (a.payload.name === element.model.name) {
          a.payload.value = element.getValue();
          foundActionIdx = idx;
        }
      });

      // Add a new action
      if (isDirty && foundActionIdx === -1) {
        component.actionQueue.push(action);
      }

      // Remove the found action that isn't dirty
      if (!isDirty && foundActionIdx > -1) {
        component.actionQueue.splice(foundActionIdx);
      }

      return;
    }

    component.actionQueue.push(action);

    component.queueMessage(
      element.model.debounceTime,
      (triggeringElements, forceModelUpdate, err) => {
        if (err) {
          console.error(err);
        } else {
          triggeringElements = triggeringElements || [];

          // Make sure that the current element is included in the triggeringElements
          // if for some reason it is missing
          if (!triggeringElements.some((e) => e.isSame(element))) {
            triggeringElements.push(element);
          }

          component.setModelValues(triggeringElements, forceModelUpdate);
          component.setDbModelValues();
        }
      }
    );
  });
}

/**
 * Adds a db event listener to the element.
 * @param {Component} component Component that contains the element.
 * @param {Element} Element that will get the event attached.
 * @param {string} eventType Event type to listen for. Optional; will use `field.eventType` by default.
 */
export function addDbEventListener(component, element, eventType) {
  eventType = eventType || element.field.eventType;
  element.events.push(eventType);
  const { el } = element;

  el.addEventListener(eventType, (event) => {
    if (
      (isEmpty(element.db.name) && isEmpty(element.model.name)) ||
      isEmpty(element.db.pk)
    ) {
      return;
    }

    let isDirty = false;

    for (let i = 0; i < component.data[element.model.name].length; i++) {
      const dbModel = component.data[element.model.name][i];

      if (dbModel.pk.toString() === element.db.pk) {
        if (dbModel[element.field.name] !== element.getValue()) {
          element.handleDirty();
          isDirty = true;
        } else {
          element.handleDirty(true);
        }
      }
    }

    if (element.field.isLazy) {
      // Lazy models fire an input and blur so that the dirty check above works as expected.
      // This will prevent the input event from doing anything.
      if (eventType === "input") {
        return;
      }
      // Lazy non-dirty elements can bail
      if (!isDirty) {
        return;
      }
    }

    if (!component.lastTriggeringElements.some((e) => e.isSame(element))) {
      component.lastTriggeringElements.push(element);
    }

    const action = {
      type: "dbInput",
      payload: {
        model: element.model.name,
        db: element.db,
        fields: {},
      },
    };

    action.payload.fields[element.field.name] = element.getValue();

    if (element.field.isDefer) {
      let foundActionIdx = -1;

      // Update the existing action with the current value
      component.actionQueue.forEach((a, idx) => {
        if (generateDbKey(a.payload) === element.dbKey()) {
          a.payload.fields[element.field.name] = element.getValue();
          foundActionIdx = idx;
        }
      });

      // Add a new action
      if (isDirty && foundActionIdx === -1) {
        component.actionQueue.push(action);
      }

      // Remove the found action that isn't dirty
      if (!isDirty && foundActionIdx > -1) {
        component.actionQueue.splice(foundActionIdx);
      }

      return;
    }

    component.actionQueue.push(action);

    component.queueMessage(element.model.debounceTime, (_, __, err) => {
      if (err) {
        console.error(err);
      } else {
        component.setDbModelValues();
      }
    });
  });
}
