import test from "ava";
import { toKebabCase } from "../../../django_unicorn/static/unicorn/js/utils";

test("Enter to kebab case", (t) => {
  t.is(toKebabCase("Enter"), "enter");
});

test("Escape to kebab case", (t) => {
  t.is(toKebabCase("Escape"), "escape");
});

test("Null to empty string", (t) => {
  t.is(toKebabCase(null), "");
});

test("Empty string to empty string", (t) => {
  t.is(toKebabCase(""), "");
});

test("One space string to empty string", (t) => {
  t.is(toKebabCase(" "), " ");
});
