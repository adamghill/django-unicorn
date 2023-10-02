import test from "ava";
import { init } from "../../../django_unicorn/static/unicorn/js/unicorn.js";

test("init unicorn", (t) => {
  const actual = init("unicorn/", "X-Unicorn", "unicorn", { NAME: "morphdom" });

  t.true(actual.messageUrl === "unicorn/");
  t.true(actual.csrfTokenHeaderName === "X-Unicorn");
  t.true(actual.csrfTokenCookieName === "unicorn");
});
