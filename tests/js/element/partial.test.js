import test from "ava";
import { getElement } from "../utils.js";

test("partial target", (t) => {
  const html =
    "<button unicorn:click='test_click' unicorn:partial='test-id'>Click</button>";
  const element = getElement(html);

  t.is(element.partial.target, "test-id");
});

test("partial.id", (t) => {
  const html =
    "<button unicorn:click='test_click' unicorn:partial.id='test-id'>Click</button>";
  const element = getElement(html);

  t.is(element.partial.id, "test-id");
});

test("partial.key", (t) => {
  const html =
    "<button unicorn:click='test_click' unicorn:partial.key='test-id'>Click</button>";
  const element = getElement(html);

  t.is(element.partial.key, "test-id");
});
