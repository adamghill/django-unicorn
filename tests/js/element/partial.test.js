import test from "ava";
import { getElement } from "../utils.js";

test("partial target", (t) => {
  const html =
    "<button unicorn:click='test_click' unicorn:partial='test-target'>Click</button>";
  const element = getElement(html);

  t.is(element.partials[0].target, "test-target");
});

test("partial.id", (t) => {
  const html =
    "<button unicorn:click='test_click' unicorn:partial.id='test-id'>Click</button>";
  const element = getElement(html);

  t.is(element.partials[0].id, "test-id");
});

test("partial.key", (t) => {
  const html =
    "<button unicorn:click='test_click' unicorn:partial.key='test-key'>Click</button>";
  const element = getElement(html);

  t.is(element.partials[0].key, "test-key");
});

test("multiple partials", (t) => {
  const html =
    "<button unicorn:click='test_click' unicorn:partial.id='test-id' unicorn:partial.key='test-key'>Click</button>";
  const element = getElement(html);

  t.is(element.partials[0].id, "test-id");
  t.is(element.partials[1].key, "test-key");
});
