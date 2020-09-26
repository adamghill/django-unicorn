import test from "ava";
import { getElement } from "../utils.js";

test("isUnicorn", (t) => {
  const html = "<input unicorn:model='name'></input>";
  const element = getElement(html, "input");

  t.true(element.isUnicorn);
});

test("!isUnicorn", (t) => {
  const html = "<input></input>";
  const element = getElement(html, "input");

  t.false(element.isUnicorn);
});

test("key", (t) => {
  const html = "<input unicorn:model='name' unicorn:key='testKey'></input>";
  const element = getElement(html, "input");

  t.is(element.key, "testKey");
});
