import test from "ava";
import { getComponent } from "../utils.js";

test("modelEls", (t) => {
  const component = getComponent();

  t.is(component.modelEls.length, 1);
});

test("abbreviated name", (t) => {
  const html = `
  <div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
    <input u:model='name'></input>
  </div>`;
  const component = getComponent(html);

  t.is(component.modelEls.length, 1);
});
