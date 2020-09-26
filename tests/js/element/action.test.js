import test from "ava";
import { getElement } from "../utils.js";

test("click", (t) => {
  const html = "<button unicorn:click='test()'></button>";
  const element = getElement(html);

  const action = element.actions[0];
  t.is(action.name, "test()");
  t.is(action.eventType, "click");
});

test("keydown.enter", (t) => {
  const html = "<input unicorn:keydown.enter='test()'></input>";
  const element = getElement(html);

  const action = element.actions[0];
  t.is(action.name, "test()");
  t.is(action.eventType, "keydown");
  t.is(action.key, "enter");
});

test("click.prevent", (t) => {
  const html = "<a href='#' unicorn:click.prevent='test()'>Test()</a>";
  const element = getElement(html);

  const action = element.actions[0];
  t.true(action.isPrevent);
  t.is(action.eventType, "click");
  t.is(action.key, undefined);
});

test("click.stop", (t) => {
  const html = "<a href='#' unicorn:click.stop='test()'>Test()</a>";
  const element = getElement(html);

  const action = element.actions[0];
  t.true(action.isStop);
  t.is(action.eventType, "click");
  t.is(action.key, undefined);
});

test("multiple actions", (t) => {
  const html = "<input unicorn:keyup.enter='add' unicorn:keydown.escape='clear'></input>";
  const element = getElement(html);

  t.true(element.actions.length === 2);
  t.true(element.actions[0].eventType === "keyup");
  t.true(element.actions[1].eventType === "keydown");
});
