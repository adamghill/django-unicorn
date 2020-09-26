import test from "ava";
import { getElement } from "../utils.js";

test("setValue()", (t) => {
  const html = "<input unicorn:model='name'></input>";
  const element = getElement(html);

  element.setValue("test");
  t.is(element.getValue(), "test");
});

test("setValue() radio with value", (t) => {
  const html = "<input unicorn:model='name' type='radio' value='test'></input>";
  const element = getElement(html);

  element.setValue(true);
  t.is(element.getValue(), "test");
});

test("setValue() radio no value", (t) => {
  const html = "<input unicorn:model='name' type='radio'></input>";
  const element = getElement(html);

  element.setValue(true);
  t.is(element.getValue(), "on");
});

test("setValue() checkbox", (t) => {
  const html = "<input unicorn:model='name' type='checkbox'></input>";
  const element = getElement(html);

  t.false(element.getValue());
  element.setValue(true);
  t.true(element.getValue());
});
