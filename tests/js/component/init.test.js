import test from "ava";
import { getComponent } from "../utils.js";

test("unicorn:id", (t) => {
  const component = getComponent();

  t.true(component.root != null);
  t.is(component.id, "5jypjiyb");
});

test("unicorn:name", (t) => {
  const component = getComponent();

  t.is(component.name, "text-inputs");
});

test("unicorn:checksum", (t) => {
  const component = getComponent();

  t.is(component.checksum, "GXzew3Km");
});
