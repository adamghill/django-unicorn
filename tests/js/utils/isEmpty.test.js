import test from "ava";
import { isEmpty } from "../../../django_unicorn/static/unicorn/js/utils";

test("undefined isEmpty", (t) => {
  t.true(isEmpty(undefined));
});

test("null isEmpty", (t) => {
  t.true(isEmpty(null));
});

test("{} isEmpty", (t) => {
  t.true(isEmpty({}));
});

test("object isEmpty", (t) => {
  t.false(isEmpty({ test: 123 }));
});

test("empty string isEmpty", (t) => {
  t.true(isEmpty(""));
});
