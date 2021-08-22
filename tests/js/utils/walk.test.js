import test from "ava";
import {
  FilterAny,
  FilterSkipNested,
  walk,
} from "../../../django_unicorn/static/unicorn/js/utils";
import { getEl, setBrowserMocks } from "../utils.js";

// makes a document and NodeFilter available from a fake DOM
setBrowserMocks();

test("walk any", (t) => {
  const componentRootHtml = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <input unicorn:model="name" type="text" id="name">
  <div
    unicorn:id="5jypjiyb:nested.filter"
    unicorn:name="nested.filter"
    unicorn:key=""
    unicorn:checksum="KtgR7WTb"
  >
    <input type="text" unicorn:model="search" id="search" />
  </div>
  <input unicorn:model="name" type="text" id="name2">
</div>
  `;
  const componentRoot = getEl(componentRootHtml);
  const nodes = [];

  walk(componentRoot, (node) => nodes.push(node), FilterAny);

  t.is(nodes.length, 4);
  t.is(nodes[0].getAttribute("id"), "name");
  t.is(nodes[1].getAttribute("unicorn:id"), "5jypjiyb:nested.filter");
  t.is(nodes[2].getAttribute("id"), "search");
  t.is(nodes[3].getAttribute("id"), "name2");
});

test("walk skip nested", (t) => {
  const componentRootHtml = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <input unicorn:model="name" type="text" id="name">
  <div
    unicorn:id="5jypjiyb:nested.filter"
    unicorn:name="nested.filter"
    unicorn:key=""
    unicorn:checksum="KtgR7WTb"
  >
    <input type="text" unicorn:model="search" id="search" />
  </div>
  <input unicorn:model="name" type="text" id="name2">
</div>
  `;
  const componentRoot = getEl(componentRootHtml);
  const nodes = [];

  walk(componentRoot, (node) => nodes.push(node), FilterSkipNested);

  t.is(nodes.length, 2);
  t.is(nodes[0].getAttribute("id"), "name");
  t.is(nodes[1].getAttribute("id"), "name2");
});
