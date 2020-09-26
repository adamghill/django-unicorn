import test from "ava";
import { getElement } from "../utils.js";

test("click", (t) => {
  const html = "<button unicorn:click='test()'></button>";
  const element = getElement(html);

  t.is(element.action.name, "test()");
  t.is(element.action.eventType, "click");
});

test("keydown.enter", (t) => {
  const html = "<input unicorn:keydown.enter='test()'></input>";
  const element = getElement(html);

  t.is(element.action.name, "test()");
  t.is(element.action.eventType, "keydown");
  t.is(element.action.key, "enter");
});

test("click.prevent", (t) => {
  const html = "<a href='#' unicorn:click.prevent='test()'>Test()</a>";
  const element = getElement(html);

  t.true(element.action.isPrevent);
  t.is(element.action.eventType, "click");
  t.is(element.action.key, undefined);
});

test("click.stop", (t) => {
  const html = "<a href='#' unicorn:click.stop='test()'>Test()</a>";
  const element = getElement(html);

  t.true(element.action.isStop);
  t.is(element.action.eventType, "click");
  t.is(element.action.key, undefined);
});
