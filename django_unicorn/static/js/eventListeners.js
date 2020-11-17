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
 * Adds an action event listener to the document for each type of event (e.g. click, keyup, etc).
 * Added at the document level because validation errors would sometimes remove the
 * events when attached directly to the element.
 * @param {Component} component Component that contains the element.
 * @param {string} eventType Event type to listen for.
 */
export function addActionEventListener(component, eventType) {
  component.document.addEventListener(eventType, (event) => {
    const targetElement = new Element(event.target);

    if (
      targetElement &&
      targetElement.isUnicorn &&
      targetElement.actions.length > 0
    ) {
      component.actionEvents[eventType].forEach((actionEvent) => {
        const { action } = actionEvent;
        const { element } = actionEvent;

        if (targetElement.isSame(element)) {
          // Add the value of any child element of the target that is a lazy model to the action queue
          // Handles situations similar to https://github.com/livewire/livewire/issues/528

          component.walker(element.el, (childEl) => {
            const modelElsInTargetScope = component.modelEls.filter((e) =>
              e.el.isSameNode(childEl)
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

          // Handle special arguments (e.g. $event)
          args(action.name).forEach((eventArg) => {
            if (eventArg.startsWith("$event")) {
              // Remove any extra whitespace, everything before and including "$event", and the ending paren
              // let eventArg = action.name.trim();
              eventArg = eventArg
                .trim()
                .slice(eventArg.indexOf("$event") + 6)
                .trim();

              const originalSpecialVariable = `$event${eventArg}`;
              let data = event;
              let invalidPiece = false;

              eventArg.split(".").forEach((piece) => {
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
                    invalidPiece = true;
                  }
                }
              });

              if (invalidPiece) {
                console.error(
                  `'${originalSpecialVariable}' could not be retrieved`
                );
                action.name = action.name.replace(originalSpecialVariable, "");
              } else if (data) {
                if (typeof data === "string") {
                  // Wrap strings in quotes
                  data = `"${data}"`;
                }

                action.name = action.name.replace(
                  originalSpecialVariable,
                  data
                );
              }
            }
          });

          if (targetElement.loading) {
            if (targetElement.loading.attr) {
              targetElement.el[targetElement.loading.attr] =
                targetElement.loading.attr;
            } else if (targetElement.loading.class) {
              targetElement.el.classList.add(targetElement.loading.class);
            } else if (targetElement.loading.removeClass) {
              targetElement.el.classList.remove(
                targetElement.loading.removeClass
              );
            }
          }

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

          if (action.key) {
            if (action.key === toKebabCase(event.key)) {
              component.callMethod(action.name);
            }
          } else {
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
 * @param {DOM Element} el DOM Element that will get the event attached.
 * @param {string} eventType Event type to listen for.
 */
export function addModelEventListener(component, el, eventType) {
  el.addEventListener(eventType, (event) => {
    const element = new Element(event.target);

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
      let foundAction = false;

      // Update the existing action with the current value
      component.actionQueue.forEach((a) => {
        if (a.payload.name === element.model.name) {
          a.payload.value = element.getValue();
          foundAction = true;
        }
      });

      // Add a new action
      if (!foundAction) {
        component.actionQueue.push(action);
      }

      return;
    }

    component.actionQueue.push(action);

    component.queueMessage(
      element.model.debounceTime,
      (triggeringElements, err) => {
        if (err) {
          console.error(err);
        } else {
          component.setModelValues(triggeringElements);
          component.setDbModelValues();
        }
      }
    );
  });
}

/**
 * Adds a db event listener to the element.
 * @param {Component} component Component that contains the element.
 * @param {DOM Element} el DOM `Element` that will get the event attached.
 * @param {string} eventType Event type to listen for.
 */
export function addDbEventListener(component, el, eventType) {
  el.addEventListener(eventType, (event) => {
    const element = new Element(event.target);

    if (
      (isEmpty(element.db.name) && isEmpty(element.model.name)) ||
      isEmpty(element.db.pk)
    ) {
      return;
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
      let foundAction = false;

      // Update the existing action with the current value
      component.actionQueue.forEach((a) => {
        if (generateDbKey(a.payload) === element.dbKey()) {
          a.payload.fields[element.field.name] = element.getValue();
          foundAction = true;
        }
      });

      // Add a new action
      if (!foundAction) {
        component.actionQueue.push(action);
      }

      return;
    }

    component.actionQueue.push(action);

    component.queueMessage(element.model.debounceTime, (_, err) => {
      if (err) {
        console.error(err);
      } else {
        component.setDbModelValues();
      }
    });
  });
}
