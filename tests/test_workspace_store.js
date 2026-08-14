const test = require("node:test");
const assert = require("node:assert/strict");

const { WorkspaceStore, MemoryWorkspaceBackend } = require("../static/workspace-store.js");

test("drafts are restored independently for all four workspaces", async () => {
  const store = new WorkspaceStore(new MemoryWorkspaceBackend());

  await store.saveDraft("h3", { source: "H3 draft" });
  await store.saveDraft("enrich", { source: "Enrich draft" });
  await store.saveDraft("vision", { imageDataUrl: "data:image/png;base64,AA==" });
  await store.saveDraft("storyboard", { taskType: "comic_panels", shots: [] });

  assert.deepEqual(await store.getDraft("h3"), { source: "H3 draft" });
  assert.deepEqual(await store.getDraft("enrich"), { source: "Enrich draft" });
  assert.deepEqual(await store.getDraft("vision"), { imageDataUrl: "data:image/png;base64,AA==" });
  assert.deepEqual(await store.getDraft("storyboard"), { taskType: "comic_panels", shots: [] });
});

test("history keeps the newest twenty successful results per workspace", async () => {
  const store = new WorkspaceStore(new MemoryWorkspaceBackend());

  for (let index = 1; index <= 21; index += 1) {
    await store.addHistory("h3", { input: `input-${index}`, output: `output-${index}` });
  }

  const history = await store.getHistory("h3");
  assert.equal(history.length, 20);
  assert.equal(history[0].input, "input-21");
  assert.equal(history.at(-1).input, "input-2");
  assert.deepEqual(await store.getHistory("enrich"), []);
});

test("queued work can be reordered without changing its payload", async () => {
  const store = new WorkspaceStore(new MemoryWorkspaceBackend());
  const first = await store.enqueue("enrich", { input: "first", strength: 30 });
  const second = await store.enqueue("enrich", { input: "second", strength: 80 });
  const third = await store.enqueue("enrich", { input: "third", strength: 100 });

  await store.reorderQueue("enrich", third.id, first.id);

  const queue = await store.getQueue("enrich");
  assert.deepEqual(queue.map(item => item.id), [third.id, first.id, second.id]);
  assert.deepEqual(queue[0].payload, { input: "third", strength: 100 });
});

test("single and multi-select deletion remove only selected records", async () => {
  const store = new WorkspaceStore(new MemoryWorkspaceBackend());
  const queueItems = [];
  const historyItems = [];
  for (const input of ["one", "two", "three"]) {
    queueItems.push(await store.enqueue("vision", { input }));
    historyItems.push(await store.addHistory("vision", { input, output: input.toUpperCase() }));
  }

  await store.deleteQueue("vision", [queueItems[1].id]);
  await store.deleteHistory("vision", [historyItems[0].id, historyItems[2].id]);

  assert.deepEqual((await store.getQueue("vision")).map(item => item.payload.input), ["one", "three"]);
  assert.deepEqual((await store.getHistory("vision")).map(item => item.input), ["two"]);
});

test("a successful queued task is consumed and recorded in history", async () => {
  const store = new WorkspaceStore(new MemoryWorkspaceBackend());
  const item = await store.enqueue("h3", { source: "source", mode: "ref2va" });

  await store.completeQueueItem("h3", item.id, { input: "source", output: "H3 output", mode: "ref2va" });

  assert.deepEqual(await store.getQueue("h3"), []);
  assert.equal((await store.getHistory("h3"))[0].output, "H3 output");
});

test("rapid queue writes are serialized without losing entries", async () => {
  const store = new WorkspaceStore(new MemoryWorkspaceBackend());

  await Promise.all(Array.from({ length: 12 }, (_, index) => store.enqueue("h3", { source: `prompt-${index}` })));

  assert.equal((await store.getQueue("h3")).length, 12);
});
