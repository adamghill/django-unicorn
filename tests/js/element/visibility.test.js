import test from "ava";
import { getComponent, getElement } from "../utils.js";

test("visible", (t) => {
  const html = "<span unicorn:visible='test_function1'></span>";
  const element = getElement(html);

  const { visibility } = element;
  t.is(visibility.method, "test_function1");
  t.is(visibility.threshold, 0);
  t.is(visibility.debounceTime, 0);
});

test("visible threshold", (t) => {
  const html = "<span unicorn:visible.threshold-25='test_function2'></span>";
  const element = getElement(html);

  const { visibility } = element;
  t.is(visibility.method, "test_function2");
  t.is(visibility.threshold, 0.25);
  t.is(visibility.debounceTime, 0);
});

test("visible debounce", (t) => {
  const html = "<span unicorn:visible.debounce-1000='test_function3'></span>";
  const element = getElement(html);

  const { visibility } = element;
  t.is(visibility.method, "test_function3");
  t.is(visibility.threshold, 0);
  t.is(visibility.debounceTime, 1000);
});

test("visible chained", (t) => {
  const html =
    "<span unicorn:visible.threshold-50.debounce-2000='test_function4'></span>";
  const element = getElement(html);

  const { visibility } = element;
  t.is(visibility.method, "test_function4");
  t.is(visibility.threshold, 0.5);
  t.is(visibility.debounceTime, 2000);
});
