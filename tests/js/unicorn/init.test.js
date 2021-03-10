import test from "ava";
import { init } from "../../../django_unicorn/static/js/unicorn.js";

test("init unicorn", (t) => {
  const actual = init("unicorn/", "X-Unicorn");

  t.true(actual.messageUrl === "unicorn/");
  t.true(actual.csrfTokenHeaderName === "X-Unicorn");
});
