import test from "ava";
import { MORPHDOM_OPTIONS } from "../../../django_unicorn/static/js/component.js"
import morphdom from "../../../django_unicorn/static/js/morphdom/2.6.1/morphdom.js";
import { getEl } from "../utils.js";

test("contains", (t) => {
  const componentRootHtml = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <input unicorn:model="name" type="text" id="name"><br />
  Name: 
</div>
  `;
  const componentRoot = getEl(componentRootHtml);

  const rerenderedComponentHtml = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <input unicorn:model="name" type="text" id="name"><br />
  Name: Test
</div>
  `;
  const rerenderedComponent = getEl(rerenderedComponentHtml);

  t.true(componentRoot.outerHTML.indexOf("Name: Test") === -1);
  morphdom(componentRoot, rerenderedComponent, MORPHDOM_OPTIONS);
  t.true(componentRoot.outerHTML.indexOf("Name: Test") > -1);
});
