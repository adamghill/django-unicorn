import test from "ava";
import { call } from "../../../src/django_unicorn/static/unicorn/js/unicorn.js";
import { components } from "../../../src/django_unicorn/static/unicorn/js/store.js";
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

test("call a method with string containing single quotes", (t) => {
  const component = getComponent();
  components[component.id] = component;

  component.callMethod = (methodName) => {
    t.true(methodName === "testMethod('It\\'s a test')");
  };

  call("text-inputs", "testMethod", "It's a test");
});

test("call a method with string containing double quotes", (t) => {
  const component = getComponent();
  components[component.id] = component;

  component.callMethod = (methodName) => {
    t.true(methodName === 'testMethod(\'He said "hello"\')');
  };

  call("text-inputs", "testMethod", 'He said "hello"');
});

test("call a method with string containing backslashes", (t) => {
  const component = getComponent();
  components[component.id] = component;

  component.callMethod = (methodName) => {
    t.true(methodName === "testMethod('C:\\\\Users\\\\test')");
  };

  call("text-inputs", "testMethod", "C:\\Users\\test");
});

test("call a method with complex chemical name (issue #607)", (t) => {
  const component = getComponent();
  components[component.id] = component;

  const chemicalName = "Chloro(2-dicyclohexylphosphino-3,6-dimethoxy-2',4',6'-tri-i-propyl-1,1'-biphenyl)(2'-amino-1,1'-biphenyl-2-yl)palladium(II)";

  component.callMethod = (methodName) => {
    t.true(methodName === `testMethod('Chloro(2-dicyclohexylphosphino-3,6-dimethoxy-2\\',4\\',6\\'-tri-i-propyl-1,1\\'-biphenyl)(2\\'-amino-1,1\\'-biphenyl-2-yl)palladium(II)')`);
  };

  call("text-inputs", "testMethod", chemicalName);
});

test("call a method with string containing both quotes and parentheses", (t) => {
  const component = getComponent();
  components[component.id] = component;

  component.callMethod = (methodName) => {
    t.true(methodName === "testMethod('test(with \\'quotes\\' and \"double\")')");
  };

  call("text-inputs", "testMethod", "test(with 'quotes' and \"double\")");
});

