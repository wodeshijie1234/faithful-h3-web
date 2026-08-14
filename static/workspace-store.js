(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.FaithfulWorkspace = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const WORKSPACES = new Set(["h3", "enrich", "vision"]);

  function assertWorkspace(workspace) {
    if (!WORKSPACES.has(workspace)) throw new Error(`Unknown workspace: ${workspace}`);
  }

  function emptyState() {
    return { draft: {}, history: [], queue: [] };
  }

  function createId() {
    if (globalThis.crypto && typeof globalThis.crypto.randomUUID === "function") return globalThis.crypto.randomUUID();
    return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  class MemoryWorkspaceBackend {
    constructor() {
      this.records = new Map();
    }

    async read(workspace) {
      return structuredClone(this.records.get(workspace) || emptyState());
    }

    async write(workspace, state) {
      this.records.set(workspace, structuredClone(state));
    }
  }

  class IndexedDbWorkspaceBackend {
    constructor(indexedDb = globalThis.indexedDB, databaseName = "faithful-h3-workspaces") {
      if (!indexedDb) throw new Error("IndexedDB is not available in this browser.");
      this.indexedDb = indexedDb;
      this.databaseName = databaseName;
      this.databasePromise = null;
    }

    async database() {
      if (this.databasePromise) return this.databasePromise;
      this.databasePromise = new Promise((resolve, reject) => {
        const request = this.indexedDb.open(this.databaseName, 1);
        request.addEventListener("upgradeneeded", () => {
          if (!request.result.objectStoreNames.contains("workspaces")) {
            request.result.createObjectStore("workspaces", { keyPath: "workspace" });
          }
        });
        request.addEventListener("success", () => resolve(request.result));
        request.addEventListener("error", () => reject(request.error));
      });
      return this.databasePromise;
    }

    async read(workspace) {
      const record = await this.#request("readonly", store => store.get(workspace));
      return record ? { draft: record.draft || {}, history: record.history || [], queue: record.queue || [] } : emptyState();
    }

    async write(workspace, state) {
      await this.#request("readwrite", store => store.put({ workspace, ...state }));
    }

    async #request(mode, operation) {
      const database = await this.database();
      return new Promise((resolve, reject) => {
        const transaction = database.transaction("workspaces", mode);
        const request = operation(transaction.objectStore("workspaces"));
        request.addEventListener("success", () => resolve(request.result));
        request.addEventListener("error", () => reject(request.error));
        transaction.addEventListener("abort", () => reject(transaction.error));
      });
    }
  }

  class WorkspaceStore {
    constructor(backend) {
      this.backend = backend;
      this.pending = new Map();
    }

    async #read(workspace) {
      assertWorkspace(workspace);
      const pending = this.pending.get(workspace);
      if (pending) await pending.catch(() => {});
      return this.backend.read(workspace);
    }

    async #mutate(workspace, mutation) {
      assertWorkspace(workspace);
      const previous = this.pending.get(workspace) || Promise.resolve();
      const operation = previous.catch(() => {}).then(async () => {
        const state = await this.backend.read(workspace);
        const result = mutation(state);
        await this.backend.write(workspace, state);
        return result;
      });
      this.pending.set(workspace, operation);
      try {
        return await operation;
      } finally {
        if (this.pending.get(workspace) === operation) this.pending.delete(workspace);
      }
    }

    async getDraft(workspace) {
      return (await this.#read(workspace)).draft;
    }

    async saveDraft(workspace, draft) {
      return this.#mutate(workspace, state => {
        state.draft = structuredClone(draft);
        return state.draft;
      });
    }

    async getHistory(workspace) {
      return (await this.#read(workspace)).history;
    }

    async addHistory(workspace, entry) {
      return this.#mutate(workspace, state => {
        const record = { id: createId(), createdAt: Date.now(), ...structuredClone(entry) };
        state.history = [record, ...state.history].slice(0, 20);
        return record;
      });
    }

    async getQueue(workspace) {
      return (await this.#read(workspace)).queue;
    }

    async enqueue(workspace, payload) {
      return this.#mutate(workspace, state => {
        const record = { id: createId(), createdAt: Date.now(), status: "pending", payload: structuredClone(payload) };
        state.queue.push(record);
        return record;
      });
    }

    async reorderQueue(workspace, movedId, beforeId = null) {
      return this.#mutate(workspace, state => {
        const movedIndex = state.queue.findIndex(item => item.id === movedId);
        if (movedIndex < 0 || movedId === beforeId) return state.queue;
        const [moved] = state.queue.splice(movedIndex, 1);
        const targetIndex = beforeId === null ? state.queue.length : state.queue.findIndex(item => item.id === beforeId);
        state.queue.splice(targetIndex < 0 ? state.queue.length : targetIndex, 0, moved);
        return state.queue;
      });
    }

    async deleteQueue(workspace, ids) {
      return this.#deleteRecords(workspace, "queue", ids);
    }

    async deleteHistory(workspace, ids) {
      return this.#deleteRecords(workspace, "history", ids);
    }

    async #deleteRecords(workspace, collection, ids) {
      const selected = new Set(ids);
      return this.#mutate(workspace, state => {
        state[collection] = state[collection].filter(item => !selected.has(item.id));
        return state[collection];
      });
    }

    async completeQueueItem(workspace, itemId, historyEntry) {
      return this.#mutate(workspace, state => {
        state.queue = state.queue.filter(item => item.id !== itemId);
        const record = { id: createId(), createdAt: Date.now(), ...structuredClone(historyEntry) };
        state.history = [record, ...state.history].slice(0, 20);
        return record;
      });
    }

    async failQueueItem(workspace, itemId, message) {
      return this.#mutate(workspace, state => {
        const item = state.queue.find(entry => entry.id === itemId);
        if (item) {
          item.status = "failed";
          item.error = String(message || "Task failed");
        }
        return item || null;
      });
    }
  }

  return { WorkspaceStore, MemoryWorkspaceBackend, IndexedDbWorkspaceBackend };
});
