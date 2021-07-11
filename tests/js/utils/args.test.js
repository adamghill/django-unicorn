import test from "ava";
import { args } from "../../../django_unicorn/static/unicorn/js/utils.js";

test("one arg", (t) => {
  const functionArgs = args("test($event.target.value)");

  t.is(functionArgs.length, 1);
  t.is(functionArgs[0], "$event.target.value");
});

test("two args", (t) => {
  const functionArgs = args("test($event.target.value, 1)");

  t.is(functionArgs.length, 2);
  t.is(functionArgs[0], "$event.target.value");
  t.is(functionArgs[1], "1");
});

test("two args with array", (t) => {
  const functionArgs = args("test($event.target.value, [1, 2])");

  t.is(functionArgs.length, 2);
  t.is(functionArgs[0], "$event.target.value");
  t.is(functionArgs[1], "[1, 2]");
});

test("two args with object", (t) => {
  const functionArgs = args('test($event.target.value, {"1": 2})');

  t.is(functionArgs.length, 2);
  t.is(functionArgs[0], "$event.target.value");
  t.is(functionArgs[1], '{"1": 2}');
});

test("two args with comma in double quotes", (t) => {
  const functionArgs = args('test($event.target.value, "1,2")');

  t.is(functionArgs.length, 2);
  t.is(functionArgs[0], "$event.target.value");
  t.is(functionArgs[1], '"1,2"');
});

test("two args with comma in single quotes", (t) => {
  const functionArgs = args("test($event.target.value, '1,2')");

  t.is(functionArgs.length, 2);
  t.is(functionArgs[0], "$event.target.value");
  t.is(functionArgs[1], "'1,2'");
});

test("two args with missing parenthesis", (t) => {
  const functionArgs = args("test(4, $event.target.value");

  // Error condition returns an empty array of args
  t.is(functionArgs.length, 0);
});
