import test from "ava";
import { init } from "../../../django_unicorn/static/unicorn/js/unicorn.js";

test("init unicorn", (t) => {
  const actual = init("unicorn/", "X-Unicorn");

  t.true(actual.messageUrl === "unicorn/");
  t.true(actual.csrfTokenHeaderName === "X-Unicorn");
  t.false(actual.reloadScriptElements);
});

test("init unicorn with no reload", (t) => {
  const actual = init("unicorn/", "X-Unicorn", false);

  t.true(actual.messageUrl === "unicorn/");
  t.true(actual.csrfTokenHeaderName === "X-Unicorn");
  t.false(actual.reloadScriptElements);
});

test("init unicorn with reload", (t) => {
  const actual = init("unicorn/", "X-Unicorn", true);

  t.true(actual.messageUrl === "unicorn/");
  t.true(actual.csrfTokenHeaderName === "X-Unicorn");
  t.true(actual.reloadScriptElements);
});
