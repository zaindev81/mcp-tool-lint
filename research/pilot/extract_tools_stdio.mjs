#!/usr/bin/env node

// Dependency-free MCP stdio collector used by the pilot. It records the
// tools/list payload exactly as served, including omitted annotation fields.

import { spawn } from "node:child_process";
import { createInterface } from "node:readline";

const separator = process.argv.indexOf("--");
if (separator === -1 || separator === process.argv.length - 1) {
  console.error("usage: node extract_tools_stdio.mjs -- COMMAND [ARGS...]");
  process.exit(2);
}

const [command, ...args] = process.argv.slice(separator + 1);
const child = spawn(command, args, {
  cwd: process.env.PILOT_SERVER_CWD || process.cwd(),
  env: process.env,
  stdio: ["pipe", "pipe", "pipe"],
});

child.stderr.setEncoding("utf8");
child.stderr.on("data", chunk => process.stderr.write(chunk));

const pending = new Map();
let nextId = 1;

function send(message) {
  child.stdin.write(`${JSON.stringify(message)}\n`);
}

function request(method, params = {}) {
  const id = nextId++;
  send({ jsonrpc: "2.0", id, method, params });
  return new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
}

const lines = createInterface({ input: child.stdout });
lines.on("line", line => {
  let message;
  try {
    message = JSON.parse(line);
  } catch {
    console.error(`non-JSON stdout from server: ${line}`);
    return;
  }

  if (message.id !== undefined && (message.result !== undefined || message.error)) {
    const waiter = pending.get(message.id);
    if (!waiter) return;
    pending.delete(message.id);
    if (message.error) waiter.reject(new Error(JSON.stringify(message.error)));
    else waiter.resolve(message.result);
    return;
  }

  if (message.id !== undefined && message.method) {
    if (message.method === "roots/list") {
      send({ jsonrpc: "2.0", id: message.id, result: { roots: [] } });
    } else if (message.method === "ping") {
      send({ jsonrpc: "2.0", id: message.id, result: {} });
    } else {
      send({
        jsonrpc: "2.0",
        id: message.id,
        error: { code: -32601, message: "Pilot collector does not implement this request" },
      });
    }
  }
});

const timeout = setTimeout(() => {
  console.error("timed out collecting tools/list");
  child.kill("SIGTERM");
  process.exitCode = 1;
}, 30_000);

try {
  await request("initialize", {
    protocolVersion: "2025-11-25",
    capabilities: {
      roots: { listChanged: true },
      sampling: {},
      elicitation: { form: {}, url: {} },
      tasks: {
        requests: {
          sampling: { createMessage: {} },
          elicitation: { create: {} },
        },
      },
    },
    clientInfo: { name: "mcp-tool-lint-pilot", version: "1" },
  });
  send({ jsonrpc: "2.0", method: "notifications/initialized" });

  // Conditional registrations run from the initialized notification handler.
  await new Promise(resolve => setTimeout(resolve, 100));

  const tools = [];
  let cursor;
  do {
    const result = await request("tools/list", cursor ? { cursor } : {});
    tools.push(...result.tools);
    cursor = result.nextCursor;
  } while (cursor);

  const supportedHints = [
    "readOnlyHint",
    "destructiveHint",
    "idempotentHint",
    "openWorldHint",
  ];
  const extracted = tools.map(tool => ({
    name: tool.name,
    description: tool.description || "",
    annotations: Object.fromEntries(
      supportedHints
        .filter(hint => Object.hasOwn(tool.annotations || {}, hint))
        .map(hint => [hint, tool.annotations[hint]])
    ),
  }));
  process.stdout.write(`${JSON.stringify(extracted, null, 2)}\n`);
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  clearTimeout(timeout);
  child.kill("SIGTERM");
}
