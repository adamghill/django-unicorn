import test from "ava";
import { contains } from "../../../django_unicorn/static/unicorn/js/utils";

test("contains", (t) => {
  t.true(contains("abcdefg", "cde"));
});

test("not contains", (t) => {
  t.false(contains("abcdefg", "xyz"));
});

test("undefined contains", (t) => {
  t.false(contains(undefined, "xyz"));
});

test("null contains", (t) => {
  t.false(contains(null, "xyz"));
});
