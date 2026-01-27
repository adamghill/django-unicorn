import test from "ava";
import { getComponent } from "../../../src/django_unicorn/static/unicorn/js/unicorn.js";
import { components } from "../../../src/django_unicorn/static/unicorn/js/store.js";
import { getComponent as getComponentUtil } from "../utils.js";

test("getComponent by key with type mismatch (existing string key, int lookup)", (t) => {
    const component = getComponentUtil();
    component.key = "123";
    components[component.id] = component;

    // Should find it even if we pass an integer
    t.truthy(getComponent(123));
});

test("getComponent by key with type mismatch (existing int key, string lookup)", (t) => {
    const component = getComponentUtil();
    component.key = 456;
    components[component.id] = component;

    // Should find it even if we pass a string
    t.truthy(getComponent("456"));
});
