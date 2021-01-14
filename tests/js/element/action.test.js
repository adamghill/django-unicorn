import test from "ava";
import { getComponent, getElement } from "../utils.js";

test("click", (t) => {
  const html = "<button unicorn:click='test()'></button>";
  const element = getElement(html);

  const action = element.actions[0];
  t.is(action.name, "test()");
  t.is(action.eventType, "click");
});

test("keydown.enter", (t) => {
  const html = "<input unicorn:keydown.enter='test()'></input>";
  const element = getElement(html);

  const action = element.actions[0];
  t.is(action.name, "test()");
  t.is(action.eventType, "keydown");
  t.is(action.key, "enter");
});

test("click.prevent", (t) => {
  const html = "<a href='#' unicorn:click.prevent='test()'>Test()</a>";
  const element = getElement(html);

  const action = element.actions[0];
  t.true(action.isPrevent);
  t.is(action.eventType, "click");
  t.is(action.key, undefined);
});

test("click.stop", (t) => {
  const html = "<a href='#' unicorn:click.stop='test()'>Test()</a>";
  const element = getElement(html);

  const action = element.actions[0];
  t.true(action.isStop);
  t.is(action.eventType, "click");
  t.is(action.key, undefined);
});

test("click.discard", (t) => {
  const html = "<a href='#' unicorn:click.discard='test()'>Test()</a>";
  const element = getElement(html);

  const action = element.actions[0];
  t.true(action.isDiscard);
  t.is(action.eventType, "click");
  t.is(action.key, undefined);
});

test("multiple actions", (t) => {
  const html =
    "<input unicorn:keyup.enter='add' unicorn:keydown.escape='clear'></input>";
  const element = getElement(html);

  t.true(element.actions.length === 2);
  t.true(element.actions[0].eventType === "keyup");
  t.true(element.actions[1].eventType === "keydown");
});

test("click on internal element", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <input unicorn:model='name'></input>
  <button unicorn:click='test()'><span id="clicker">Click</span></button>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.children[0].click();

  t.is(component.actionQueue.length, 1);
});

test("$returnValue", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <input unicorn:model='name'></input>
  <button unicorn:click='test($returnValue)'></button>
</div>`;
  const component = getComponent(html);
  component.return = { value: "123" };

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);
  const action = component.actionQueue[0];
  t.is(action.payload.name, 'test("123")');
});

test("$returnValue invalid property", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <input unicorn:model='name'></input>
  <button unicorn:click='test($returnValue.blob)'></button>
</div>`;
  const component = getComponent(html);
  component.return = { value: "123" };

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);
  const action = component.actionQueue[0];
  t.is(action.payload.name, "test()");
});

test("$returnValue nested property", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <input unicorn:model='name'></input>
  <button unicorn:click='test($returnValue.hello)'></button>
</div>`;
  const component = getComponent(html);
  component.return = { value: { hello: "world" } };

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);
  const action = component.actionQueue[0];
  t.is(action.payload.name, 'test("world")');
});

test("$returnValue with method", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <input unicorn:model='name'></input>
  <button unicorn:click='test($returnValue.trim())'></button>
</div>`;
  const component = getComponent(html);
  component.return = { value: " world " };

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);
  const action = component.actionQueue[0];
  t.is(action.payload.name, 'test("world")');
});

test("$event action variable invalid property", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <input unicorn:model='name'></input>
  <button unicorn:click='test($event.target.value)' value='1'></button>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);
  const action = component.actionQueue[0];
  t.is(action.payload.name, 'test("1")');
});

test("$event invalid variable", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <input unicorn:model='name'></input>
  <button unicorn:click='test($event.target.value.blob)' value='2'></button>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);
  const action = component.actionQueue[0];
  t.is(action.payload.name, "test()");
});

test("$event action variable with method", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <input unicorn:model='name'></input>
  <button unicorn:click='test($event.target.value.trim())' value=' 3 '></button>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);
  const action = component.actionQueue[0];
  t.is(action.payload.name, 'test("3")');
});

test("$event action variable in middle of args", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <input unicorn:model='name'></input>
  <button unicorn:click='test($event.target.value.trim(), 1)' value=' 4 '></button>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);
  const action = component.actionQueue[0];
  t.is(action.payload.name, 'test("4", 1)');
});

test("$model action variable", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <div u:db="example">
    <div u:pk="1">
      <button unicorn:click='test($model)'></button>
    </div>
  </div>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);
  const action = component.actionQueue[0];
  t.is(action.payload.name, 'test({"pk":"1","name":"example"})');
});

test("$model action variable missing pk", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <div u:db="example">
    <div>
      <button unicorn:click='test($model)'></button>
    </div>
  </div>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);
  const action = component.actionQueue[0];
  t.is(action.payload.name, "test($model)");
});

test("$model action variable missing db", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <div>
    <div u:pk="1">
      <button u:click='test($model)'></button>
    </div>
  </div>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);
  const action = component.actionQueue[0];
  t.is(action.payload.name, "test($model)");
});

test("$model action variable same element", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <button u:db="example" u:pk="1" u:click='test($model)'></button>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);
  const action = component.actionQueue[0];
  t.is(action.payload.name, 'test({"pk":"1","name":"example"})');
});

test("event action loading attr", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <button unicorn:click='test()' u:loading.attr="disabled"></button>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  const { el } = component.actionEvents.click[0].element;
  t.true(typeof el.attributes.disabled === "undefined");

  el.click();
  t.false(typeof el.attributes.disabled === "undefined");
});

test("event action loading class", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <button unicorn:click='test()' u:loading.class="loading"></button>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  const { el } = component.actionEvents.click[0].element;
  t.is(el.classList.length, 0);

  el.click();
  t.is(el.classList.length, 1);
  t.is(el.classList[0], "loading");
});

test("event action loading remove class", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <button unicorn:click='test()' u:loading.class.remove="unloading" class="unloading"></button>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  const { el } = component.actionEvents.click[0].element;
  t.is(el.classList.length, 1);
  t.is(el.classList[0], "unloading");

  el.click();
  t.is(el.classList.length, 0);
});

test("event action loading show", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <button unicorn:click='test()' id='testId' u:key='testKey'></button>
  <div u:loading>
  Loading
  </div>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);
  t.is(component.loadingEls.length, 1);

  const { el } = component.actionEvents.click[0].element;
  const loadingEl = component.loadingEls[0];
  t.true(loadingEl.el.hidden);

  el.click();
  t.false(loadingEl.el.hidden);
});

test("event action loading hide", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <button unicorn:click='test()' id='testId' u:key='testKey'></button>
  <div u:loading.remove>
  Loading
  </div>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);
  t.is(component.loadingEls.length, 1);

  const { el } = component.actionEvents.click[0].element;
  const loadingEl = component.loadingEls[0];
  t.false(loadingEl.el.hidden);

  el.click();
  t.true(loadingEl.el.hidden);
});

test("event action loading by id", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <button unicorn:click='test()' id='testId' u:key='testKey'></button>
  <div u:loading u:target='testId'>
  Loading
  </div>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);
  t.is(component.loadingEls.length, 1);

  const { el } = component.actionEvents.click[0].element;
  const loadingEl = component.loadingEls[0];
  t.true(loadingEl.el.hidden);

  el.click();
  t.false(loadingEl.el.hidden);
});

test("event action loading by key", (t) => {
  const html = `
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  <button unicorn:click='test()' id='testId' u:key='testKey'></button>
  <div u:loading u:target='testKey'>
  Loading
  </div>
</div>`;
  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);
  t.is(component.loadingEls.length, 1);

  const { el } = component.actionEvents.click[0].element;
  const loadingEl = component.loadingEls[0];
  t.true(loadingEl.el.hidden);

  el.click();
  t.false(loadingEl.el.hidden);
});
