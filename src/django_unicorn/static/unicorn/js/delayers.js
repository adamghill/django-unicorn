/**
   * Returns a function, that, as long as it continues to be invoked, will not
   * be triggered. The function will be called after it stops being called for
   * N milliseconds. If `immediate` is passed, trigger the function on the
   * leading edge, instead of the trailing.

   * Derived from underscore.js's implementation in https://davidwalsh.name/javascript-debounce-function.
   */
export function debounce(func, wait, immediate) {
  let timeout;

  if (typeof immediate === "undefined") {
    immediate = true;
  }

  return (...args) => {
    const context = this;

    const later = () => {
      timeout = null;
      if (!immediate) {
        func.apply(context, args);
      }
    };

    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);

    if (callNow) {
      func.apply(context, args);
    }
  };
}

/**
 * The function is executed the number of times it is called,
 * but there is a fixed wait time before each execution.
 * From https://medium.com/ghostcoder/debounce-vs-throttle-vs-queue-execution-bcde259768.
 */
const funcQueue = [];
export function queue(func, waitTime) {
  let isWaiting;

  const play = () => {
    let params;
    isWaiting = false;

    if (funcQueue.length) {
      params = funcQueue.shift();
      executeFunc(params);
    }
  };

  const executeFunc = (params) => {
    isWaiting = true;
    func(params);
    setTimeout(play, waitTime);
  };

  return (params) => {
    if (isWaiting) {
      funcQueue.push(params);
    } else {
      executeFunc(params);
    }
  };
}
