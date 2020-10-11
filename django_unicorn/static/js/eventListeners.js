import { isEmpty, toKebabCase, walk } from "./utils.js";
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

        // Use isSameNode (not isEqualNode) because we want to check the nodes reference the same object
        if (targetElement.el.isSameNode(element.el)) {
          // Add the value of any child element of the target that is a lazy model to the action queue
          // Handles situations similar to https://github.com/livewire/livewire/issues/528
          walk(element.el, (childEl) => {
            const modelElsInTargetScope = component.modelEls.filter((e) =>
              e.el.isSameNode(childEl)
            );

            modelElsInTargetScope.forEach((modelElement) => {
              if (!isEmpty(modelElement.model) && modelElement.model.isLazy) {
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
              if (!isEmpty(dbElement.model) && dbElement.model.isLazy) {
                const actionForQueue = {
                  type: "dbInput",
                  payload: {
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
 * @param {Element} element Element that will get the event attached to.
 * @param {string} eventType Event type to listen for.
 */
export function addModelEventListener(component, element, eventType) {
  element.el.addEventListener(eventType, () => {
    const action = {
      type: "syncInput",
      payload: {
        name: element.model.name,
        value: element.getValue(),
      },
    };

    if (
      !component.lastTriggeringElements.some((e) => e.el.isSameNode(element.el))
    ) {
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
      (triggeringElements, _, err) => {
        if (err) {
          console.error(err);
        } else {
          component.setModelValues(triggeringElements);
          component.setDbModelValues(triggeringElements);
        }
      }
    );
  });
}

/**
 * Adds a db event listener to the element.
 * @param {Component} component Component that contains the element.
 * @param {Element} element Element that will get the event attached to.
 * @param {string} eventType Event type to listen for.
 */
export function addDbEventListener(component, element, eventType) {
  element.el.addEventListener(eventType, () => {
    if (
      !element.db.name ||
      typeof element.db.pk === "undefined" ||
      element.db.pk == null
    ) {
      return;
    }

    if (
      !component.lastTriggeringElements.some((e) => e.el.isSameNode(element.el))
    ) {
      component.lastTriggeringElements.push(element);
    }

    const action = {
      type: "dbInput",
      payload: {
        db: element.db.name,
        pk: element.db.pk,
        fields: {},
      },
    };

    action.payload.fields[element.field.name] = element.getValue();

    if (element.field.isDefer) {
      let foundAction = false;

      // Update the existing action with the current value
      component.actionQueue.forEach((a) => {
        if (
          a.payload.db === element.db.name &&
          a.payload.pk === element.db.pk
        ) {
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

    component.queueMessage(
      element.model.debounceTime,
      (triggeringElements, dbUpdates, err) => {
        if (err) {
          console.error(err);
        } else {
          component.setDbModelValues(triggeringElements, dbUpdates);
        }
      }
    );
  });
}
