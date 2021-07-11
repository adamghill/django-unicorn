import test from "ava";
import { call } from "../../../django_unicorn/static/unicorn/js/unicorn.js";
import { components } from "../../../django_unicorn/static/unicorn/js/store.js";
import { getComponent } from "../utils.js";

test("call a method", (t) => {
  const component = getComponent();
  components[component.id] = component;

  component.callMethod = (methodName) => {
    t.true(methodName === "testMethod");
  };

  call("text-inputs", "testMethod");
});

test("call a method with string argument", (t) => {
  const component = getComponent();
  components[component.id] = component;

  component.callMethod = (methodName) => {
    t.true(methodName === "testMethod('test1')");
  };

  call("text-inputs", "testMethod", "test1");
});

test("call a method with string and int argument", (t) => {
  const component = getComponent();
  components[component.id] = component;

  component.callMethod = (methodName) => {
    t.true(methodName === "testMethod('test1', 2)");
  };

  call("text-inputs", "testMethod", "test1", 2);
});
