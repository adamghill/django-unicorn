import test from "ava";
import { init } from "../../../django_unicorn/static/unicorn/js/unicorn.js";

test("init unicorn", (t) => {
  const actual = init("unicorn/", "X-Unicorn", "unicorn");

  t.true(actual.messageUrl === "unicorn/");
  t.true(actual.csrfTokenHeaderName === "X-Unicorn");
  t.true(actual.csrfTokenCookieName === "unicorn");
  t.false(actual.reloadScriptElements);
});

test("init unicorn with no reload", (t) => {
  const actual = init("unicorn/", "X-Unicorn", "unicorn", false);

  t.true(actual.messageUrl === "unicorn/");
  t.true(actual.csrfTokenHeaderName === "X-Unicorn");
  t.true(actual.csrfTokenCookieName === "unicorn");
  t.false(actual.reloadScriptElements);
});

test("init unicorn with reload", (t) => {
  const actual = init("unicorn/", "X-Unicorn", "unicorn", true);

  t.true(actual.messageUrl === "unicorn/");
  t.true(actual.csrfTokenHeaderName === "X-Unicorn");
  t.true(actual.csrfTokenCookieName === "unicorn");
  t.true(actual.reloadScriptElements);
});
