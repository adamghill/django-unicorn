import test from "ava";
import { getElement } from "../utils.js";

test("getValue()", (t) => {
  const html = "<input unicorn:model='name' value='test'></input>";
  const element = getElement(html);

  t.is(element.getValue(), "test");
});

test("checkbox getValue() checked", (t) => {
  const html = "<input unicorn:model='name' type='checkbox' checked></input>";
  const element = getElement(html);

  t.true(element.getValue());
});

test("checkbox getValue() not checked", (t) => {
  const html = "<input unicorn:model='name' type='checkbox'></input>";
  const element = getElement(html);

  t.false(element.getValue());
});

test("checkbox getValue() select", (t) => {
  const html = `
<select unicorn:model="things">
  <option value="doggo" selected>🐶</option>
  <option value="octopus">🐙</option>
  <option value="alien">👾</option>
</select>
  `;
  const element = getElement(html);

  t.is(element.getValue(), "doggo");
});

test("checkbox getValue() select multiple", (t) => {
  const html = `
<select unicorn:model="things" multiple>
  <option value="doggo">🐶</option>
  <option value="octopus" selected>🐙</option>
  <option value="alien" selected>👾</option>
</select>
  `;
  const element = getElement(html);

  t.deepEqual(element.getValue(), ["octopus", "alien"]);
});
