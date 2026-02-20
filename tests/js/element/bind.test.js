import test from "ava";
import { getElement } from "../utils.js";

test("bind", (t) => {
    const html = "<input unicorn:bind='name'></input>";
    const element = getElement(html);

    t.is(element.model.name, "name");
    t.is(element.model.eventType, "input");
    t.false(element.model.isLazy);
    t.false(element.model.isDefer);
});

test("bind.defer", (t) => {
    const html = "<input unicorn:bind.defer='name'></input>";
    const element = getElement(html);

    t.true(element.model.isDefer);
});

test("bind.lazy", (t) => {
    const html = "<input unicorn:bind.lazy='name'></input>";
    const element = getElement(html);

    t.true(element.model.isLazy);
    t.is(element.model.eventType, "blur");
});

test("bind.debounce", (t) => {
    const html = "<input unicorn:bind.debounce='name'></input>";
    const element = getElement(html);

    t.is(element.model.debounceTime, -1);
});

test("bind.debounce-1000", (t) => {
    const html = "<input unicorn:bind.debounce-1000='name'></input>";
    const element = getElement(html);

    t.is(element.model.debounceTime, 1000);
});

test("bind.lazy.debounce-500", (t) => {
    const html = "<input unicorn:bind.lazy.debounce-500='name'></input>";
    const element = getElement(html);

    t.true(element.model.isLazy);
    t.is(element.model.debounceTime, 500);
});
