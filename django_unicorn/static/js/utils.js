/**
 * Checks if an object is empty. Useful to check if a dictionary has a value.
 */
export function isEmpty(obj) {
  return (
    typeof obj === "undefined" ||
    obj === null ||
    (Object.keys(obj).length === 0 && obj.constructor === Object)
  );
}

/**
 * Checks if an object has a value.
 */
export function hasValue(obj) {
  return !isEmpty(obj);
}

/**
 * Checks if a string has the search text.
 */
export function contains(str, search) {
  if (!str) {
    return false;
  }

  return str.indexOf(search) > -1;
}

/**
 * A simple shortcut for querySelector that everyone loves.
 */
export function $(selector, scope) {
  if (scope === undefined) {
    scope = document;
  }

  return scope.querySelector(selector);
}

/**
 * Get the CSRF token used by Django.
 */
export function getCsrfToken() {
  // Default to looking for the CSRF in the cookie
  const cookieKey = "csrftoken=";
  const csrfTokenCookie = document.cookie
    .split(";")
    .filter((item) => item.trim().startsWith(cookieKey));

  if (csrfTokenCookie.length > 0) {
    return csrfTokenCookie[0].replace(cookieKey, "");
  }

  // Fall back to check for the CSRF hidden input
  const csrfElements = document.getElementsByName("csrfmiddlewaretoken");

  if (csrfElements && csrfElements.length > 0) {
    return csrfElements[0].getAttribute("value");
  }

  throw Error("CSRF token is missing. Do you need to add {% csrf_token %}?");
}

/**
 * Converts a string to "kebab-case", aka lower-cased with hyphens.
 * @param {string} str The string to be converted.
 */
export function toKebabCase(str) {
  if (!str) {
    return "";
  }

  return str
    .match(/[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g)
    .map((x) => x.toLowerCase())
    .join("-");
}

/**
 * Traverses the DOM looking for child elements.
 */
export function walk(el, callback) {
  const walker = document.createTreeWalker(
    el,
    NodeFilter.SHOW_ELEMENT,
    null,
    false
  );

  while (walker.nextNode()) {
    // TODO: Handle sub-components?
    callback(walker.currentNode);
  }
}
