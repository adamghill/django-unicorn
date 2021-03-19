import test from "ava";
import { getComponent } from "../utils.js";

test("callCalls with function name", (t) => {
  const functionName = "someFunction";
  const component = getComponent();

  component.window[functionName] = () => {
    return true;
  };

  const actual = component.callCalls([{ fn: functionName }]);
  t.deepEqual(actual, [true]);
});

test("callCalls with function name and arg", (t) => {
  const functionName = "someFunction";
  const component = getComponent();

  component.window[functionName] = (argOne) => {
    return `${argOne}!!`;
  };

  const actual = component.callCalls([{ fn: functionName, args: ["great"] }]);
  t.deepEqual(actual, ["great!!"]);
});

test("callCalls with module and arg", (t) => {
  const component = getComponent();

  component.window.SomeModule = (() => {
    const self = {};

    self.someFunction = (name) => {
      return `${name}!`;
    };

    return self;
  })();

  const actual = component.callCalls([
    { fn: "SomeModule.someFunction", args: ["howdy"] },
  ]);
  t.deepEqual(actual, ["howdy!"]);
});
