import test from "ava";
import fetchMock from "fetch-mock";
import { getComponent } from "../utils.js";
import { send } from "../../../src/django_unicorn/static/unicorn/js/messageSender.js";

// Needs to be serial because we are mocking global fetch
test.serial("queueMessage should debounce multiple calls", async (t) => {
    const html = `
  <div unicorn:id="5jypjiyb" unicorn:name="text-inputs" unicorn:checksum="GXzew3Km">
  </div>`;
    const component = getComponent(html);

    // Mock fetch
    global.fetch = fetchMock.sandbox().mock().post("/test/text-inputs", 200);

    // Queue two messages with 100ms debounce
    // We need to push something to actionQueue so send() actually attempts to fetch
    component.actionQueue.push({ type: "syncInput", payload: { name: "test", value: "1" } });
    component.queueMessage(100, () => { });

    // Simulate fast typing (second event before first debounce fires)
    await new Promise((r) => setTimeout(r, 10));

    component.actionQueue.push({ type: "syncInput", payload: { name: "test", value: "2" } });
    component.queueMessage(100, () => { });

    // Wait for debounce to expire (100ms from start + 10ms > 100ms)
    // We wait enough time for BOTH to fire if they were independent (e.g. 200ms)
    await new Promise((r) => setTimeout(r, 200));

    // Should satisfy debounce: only 1 call
    // Current bug: likely 2 calls?
    const calls = fetchMock.calls();

    // Clean up
    fetchMock.reset();

    // We expect 1 call if debounced correctly.
    // If bug exists, it might be 2 calls.
    // For reproduction, we ASSERT 1 call and expect it to FAIL if bug exists.
    t.is(calls.length, 1, `Expected 1 fetch call, but got ${calls.length}`);
});
