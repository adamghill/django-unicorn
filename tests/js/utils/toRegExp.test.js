import test from "ava";
import { toRegExp } from "../../../django_unicorn/static/unicorn/js/utils";

test("To regexp 'test-*'", (t) => {
  t.deepEqual(toRegExp("test-*"), /(test-)[a-zA-Z0-9_:.\-]*/);
});

test("To regexp '*-test'", (t) => {
  t.deepEqual(toRegExp("*-test"), /[a-zA-Z0-9_:.\-]*(-test)/);
});

test("To regexp 'test-*-final'", (t) => {
  t.deepEqual(toRegExp("test-*-final"), /(test-)[a-zA-Z0-9_:.\-]*(-final)/);
});

test("To regexp 'test-*-v*-final'", (t) => {
  t.deepEqual(
    toRegExp("test-*-v*-final"),
    /(test-)[a-zA-Z0-9_:.\-]*(-v)[a-zA-Z0-9_:.\-]*(-final)/
  );
});
