import test from "ava";
import { getComponent } from "../../../django_unicorn/static/unicorn/js/unicorn.js";
import { components } from "../../../django_unicorn/static/unicorn/js/store.js";
import { getComponent as getComponentUtil } from "../utils.js";

test("getComponent by name", (t) => {
  const component = getComponentUtil();
  component.name = "text-inputs-name";
  components[component.id] = component;

  t.truthy(getComponent("text-inputs-name"));
});

test("getComponent by key", (t) => {
  const component = getComponentUtil();
  component.key = "text-inputs-key";
  components[component.id] = component;

  t.truthy(getComponent("text-inputs-key"));
});

test("getComponent missing", (t) => {
  const component = getComponentUtil();
  component.name = "text-inputs-name";
  components[component.id] = component;

  const error = t.throws(
    () => {
      getComponent("text-inputs-missing");
    },
    { instanceOf: Error }
  );
  t.is(error.message, "No component found for: text-inputs-missing");
});
