import test from "ava";
import fetchMock from "fetch-mock";
import { getComponent } from "../utils.js";
import { send } from "../../../django_unicorn/static/js/messageSender.js";

test.cb("call_method redirect", (t) => {
  const html = `
<input type="hidden" name="csrfmiddlewaretoken" value="asdf">
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
    <input unicorn:model='name'></input>
    <button unicorn:click='test()'><span id="clicker">Click</span></button>
</div>
  `;

  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);

  // mock the fetch
  const res = {
    id: "aQzrrRoG",
    dom: "",
    data: {
      name: "World",
    },
    errors: {},
    redirect: { url: "http://www.google.com" },
    return: {},
  };
  global.fetch = fetchMock.sandbox().mock().post("/test/text-inputs", res);

  send(component, (a, b, err) => {
    t.true(err === null);
    t.is(component.window.location.href, "http://www.google.com");
    fetchMock.reset();
    t.end();
  });
});

test.cb("call_method refresh redirect", (t) => {
  const html = `
<input type="hidden" name="csrfmiddlewaretoken" value="asdf">
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
    <input unicorn:model='name'></input>
    <button unicorn:click='test()'><span id="clicker">Click</span></button>
</div>
  `;

  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);

  // mock the fetch
  const res = {
    id: "aQzrrRoG",
    dom: "",
    data: {
      name: "World",
    },
    errors: {},
    redirect: {
      url: "/test/text-inputs?some=query",
      refresh: true,
      title: "new title",
    },
    return: {},
  };
  global.fetch = fetchMock.sandbox().mock().post("/test/text-inputs", res);

  send(component, (a, b, err) => {
    t.true(err === null);
    t.is(component.window.history.get(), "/test/text-inputs?some=query");
    t.is(component.window.document.title, "new title");
    fetchMock.reset();
    t.end();
  });
});

test.cb("call_method hash", (t) => {
  const html = `
<input type="hidden" name="csrfmiddlewaretoken" value="asdf">
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
    <input unicorn:model='name'></input>
    <button unicorn:click='test()'><span id="clicker">Click</span></button>
</div>
  `;

  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);

  // mock the fetch
  const res = {
    id: "aQzrrRoG",
    dom: "",
    data: {
      name: "World",
    },
    errors: {},
    redirect: {
      hash: "#somehash",
    },
    return: {},
  };
  global.fetch = fetchMock.sandbox().mock().post("/test/text-inputs", res);

  send(component, (a, b, err) => {
    t.true(err === null);
    t.is(component.window.location.hash, "#somehash");
    fetchMock.reset();
    t.end();
  });
});

test.cb("call_method forceModelUpdate is true", (t) => {
  const html = `
<input type="hidden" name="csrfmiddlewaretoken" value="asdf">
<div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
    <input unicorn:model='name'></input>
    <button unicorn:click='test()'><span id="clicker">Click</span></button>
</div>
  `;

  const component = getComponent(html);

  t.is(component.attachedEventTypes.length, 1);
  t.is(component.actionEvents.click.length, 1);

  component.actionEvents.click[0].element.el.click();

  t.is(component.actionQueue.length, 1);

  // mock the fetch
  const res = {
    id: "aQzrrRoG",
    dom: "blob",
    data: {
      name: "World",
    },
    errors: {},
    redirect: {},
    return: {},
  };
  global.fetch = fetchMock.sandbox().mock().post("/test/text-inputs", res);

  send(component, (a, forceModelUpdates, err) => {
    t.true(err === null);
    t.true(forceModelUpdates);
    fetchMock.reset();
    t.end();
  });
});
