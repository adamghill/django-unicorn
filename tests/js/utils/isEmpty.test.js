import test from "ava";
import { isEmpty } from "../../../django_unicorn/static/js/utils";

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
