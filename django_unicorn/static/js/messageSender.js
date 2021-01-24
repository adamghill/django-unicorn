import { $, getCsrfToken, hasValue, isFunction } from "./utils.js";
import { MORPHDOM_OPTIONS } from "./morphdom/2.6.1/options.js";

/**
 * Calls the message endpoint and merges the results into the document.
 */
export function send(component, callback) {
  // Prevent network call when there isn't an action
  if (component.actionQueue.length === 0) {
    return;
  }

  // Prevent network call when the action queue gets repeated
  if (component.currentActionQueue === component.actionQueue) {
    return;
  }

  // Since methods can change the data "behind the scenes", any queue with a callMethod
  // action forces model elements to always be updated
  const forceModelUpdate = component.actionQueue.some(
    (a) => a.type === "callMethod"
  );

  // Set the current action queue and clear the action queue in case another event happens
  component.currentActionQueue = component.actionQueue;
  component.actionQueue = [];

  const body = {
    id: component.id,
    data: component.data,
    checksum: component.checksum,
    actionQueue: component.currentActionQueue,
  };

  const headers = {
    Accept: "application/json",
    "X-Requested-With": "XMLHttpRequest",
  };
  headers[component.csrfTokenHeaderName] = getCsrfToken(component);

  fetch(component.syncUrl, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      }

      throw Error(
        `Error when getting response: ${response.statusText} (${response.status})`
      );
    })
    .then((responseJson) => {
      if (!responseJson) {
        return;
      }

      if (responseJson.error) {
        if (responseJson.error === "Checksum does not match") {
          // Reset the models if the checksum doesn't match
          if (isFunction(callback)) {
            callback([], true, null);
          }
        }

        throw Error(responseJson.error);
      }

      // Redirect to the specified url if it is set
      // TODO: For turbolinks support look at https://github.com/livewire/livewire/blob/f2ba1977d73429911f81b3f6363ee8f8fea5abff/js/component/index.js#L330-L336
      if (responseJson.redirect) {
        if (responseJson.redirect.url) {
          if (responseJson.redirect.refresh) {
            if (responseJson.redirect.title) {
              component.window.document.title = responseJson.redirect.title;
            }

            component.window.history.pushState(
              {},
              "",
              responseJson.redirect.url
            );
          } else {
            component.window.location.href = responseJson.redirect.url;
          }
        } else if (responseJson.redirect.hash) {
          component.window.location.hash = responseJson.redirect.hash;
        }
      }

      // Remove any unicorn validation messages before trying to merge with morphdom
      component.modelEls.forEach((element) => {
        // Re-initialize element to make sure it is up to date
        element.init();
        element.removeErrors();
        element.handleDirty(true);
      });

      // Get the data from the response
      component.data = responseJson.data || {};
      component.errors = responseJson.errors || {};
      component.return = responseJson.return || {};

      const parent = responseJson.parent || {};
      const rerenderedComponent = responseJson.dom || {};
      const partials = responseJson.partials || [];
      const { checksum } = responseJson;

      // Handle poll
      const poll = responseJson.poll || {};

      if (hasValue(poll)) {
        if (component.poll.timer) {
          clearInterval(component.poll.timer);
        }

        if (poll.timing) {
          component.poll.timing = poll.timing;
        }
        if (poll.method) {
          component.poll.method = poll.method;
        }

        component.poll.disable = poll.disable || false;
        component.startPolling();
      }

      // Refresh the parent component if there is one
      if (hasValue(parent) && hasValue(parent.id) && hasValue(parent.dom)) {
        const parentComponent = component.getParentComponent(parent.id);

        if (parentComponent && parentComponent.id === parent.id) {
          // TODO: Handle errors?
          parentComponent.data = parent.data || {};

          component.morphdom(
            parentComponent.root,
            parent.dom,
            MORPHDOM_OPTIONS
          );
          parentComponent.refreshChecksum();
          parentComponent.refreshEventListeners();

          parentComponent.getChildrenComponents().forEach((child) => {
            child.init();
            child.refreshEventListeners();
          });
        }
      }

      if (partials.length > 0) {
        for (let i = 0; i < partials.length; i++) {
          const partial = partials[i];
          let targetDom = null;

          if (partial.key) {
            targetDom = $(`[unicorn\\:key="${partial.key}"]`, component.root);
          } else if (partial.id) {
            targetDom = $(`#${partial.id}`, component.root);
          }

          if (targetDom) {
            component.morphdom(targetDom, partial.dom, MORPHDOM_OPTIONS);
          }
        }

        if (checksum) {
          component.root.setAttribute("unicorn:checksum", checksum);
          component.refreshChecksum();
        }
      } else {
        component.morphdom(
          component.root,
          rerenderedComponent,
          MORPHDOM_OPTIONS
        );
      }

      // Re-init to refresh the root and checksum based on the new data
      component.init();

      // Reset all event listeners
      component.refreshEventListeners();

      // Re-add unicorn validation messages from errors
      component.modelEls.forEach((element) => {
        Object.keys(component.errors).forEach((modelName) => {
          if (element.model.name === modelName) {
            const error = component.errors[modelName][0];
            element.addError(error);
          }
        });
      });

      const triggeringElements = component.lastTriggeringElements;
      component.lastTriggeringElements = [];

      // Clear the current action queue
      component.currentActionQueue = null;

      if (isFunction(callback)) {
        callback(triggeringElements, forceModelUpdate, null);
      }
    })
    .catch((err) => {
      // Make sure to clear the current queues in case of an error
      component.actionQueue = [];
      component.currentActionQueue = null;
      component.lastTriggeringElements = [];

      if (isFunction(callback)) {
        callback(null, null, err);
      }
    });
}
