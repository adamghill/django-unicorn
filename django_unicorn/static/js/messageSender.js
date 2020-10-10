import { getCsrfToken } from "./utils.js";
import morphdom from "./morphdom/2.6.1/morphdom.js";
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
  headers[component.csrfTokenHeaderName] = getCsrfToken();

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
        // TODO: Check for "Checksum does not match" error and try to fix it
        throw Error(responseJson.error);
      }

      // Remove any unicorn validation messages before trying to merge with morphdom
      component.modelEls.forEach((element) => {
        // Re-initialize element to make sure it is up to date
        element.init();
        element.removeErrors();
      });

      // Get the data from the response
      component.data = responseJson.data || {};
      component.errors = responseJson.errors || {};
      const rerenderedComponent = responseJson.dom;

      morphdom(component.root, rerenderedComponent, MORPHDOM_OPTIONS);

      // Refresh the checksum based on the new data
      component.refreshChecksum();

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

      const dbUpdates = responseJson.db || {};

      if (callback && typeof callback === "function") {
        callback(triggeringElements, dbUpdates, null);
      }
    })
    .catch((err) => {
      // Make sure to clear the current queues in case of an error
      component.actionQueue = [];
      component.currentActionQueue = null;
      component.lastTriggeringElements = [];

      if (callback && typeof callback === "function") {
        callback(null, null, err);
      }
    });
}
