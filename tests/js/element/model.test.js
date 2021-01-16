import test from "ava";
import { getElement } from "../utils.js";

test("model", (t) => {
  const html = "<input unicorn:model='name'></input>";
  const element = getElement(html);

  t.is(element.model.name, "name");
  t.is(element.model.eventType, "input");
  t.false(element.model.isLazy);
  t.false(element.model.isDefer);
});

test("model.defer", (t) => {
  const html = "<input unicorn:model.defer='name'></input>";
  const element = getElement(html);

  t.true(element.model.isDefer);
});

test("model.lazy", (t) => {
  const html = "<input unicorn:model.lazy='name'></input>";
  const element = getElement(html);

  t.true(element.model.isLazy);
  t.is(element.model.eventType, "blur");
});

test("model.debounce", (t) => {
  const html = "<input unicorn:model.debounce='name'></input>";
  const element = getElement(html);

  t.is(element.model.debounceTime, -1);
});

test("model.debounce-1000", (t) => {
  const html = "<input unicorn:model.debounce-1000='name'></input>";
  const element = getElement(html);

  t.is(element.model.debounceTime, 1000);
});

test("model.lazy.debounce-500", (t) => {
  const html = "<input unicorn:model.lazy.debounce-500='name'></input>";
  const element = getElement(html);

  t.true(element.model.isLazy);
  t.is(element.model.debounceTime, 500);
});
