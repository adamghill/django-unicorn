import test from "ava";
import { getComponent } from "../utils.js";

test("modelEls", (t) => {
  const component = getComponent();

  t.is(component.modelEls.length, 1);
});
