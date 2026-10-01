#!/usr/bin/env node
// PreToolUse hook: blocks Claude from touching any .env file (and from disabling this guard).
// Exit code 2 = block the tool call; stderr is shown to Claude as the reason.
// Fails CLOSED: any parse/runtime error also blocks.

const BLOCK = (reason) => {
  process.stderr.write(`BLOCKED by .claude/hooks/block-env.js: ${reason}\n`);
  process.exit(2);
};

// `.env` as a path component: start/separator before it, end/separator/suffix after it.
// Matches: .env  ./.env  src\.env  .env.local  .env.production  "*.env"  .ENV
// Does NOT match: process.env, os.environ, .venv, myenv
const ENV_PATH = /(^|[\s"'`=:;,(){}\[\]<>|&*\/\\@!$])\.env(?![\w-])(\.[\w.-]*)?/i;

// Files guarding this rule — Claude must not be able to edit/disable them.
const GUARD_FILES = /\.claude[\/\\](hooks[\/\\]block-env\.js|settings(\.local)?\.json)/i;

// Glob/wildcard tricks in shell commands, e.g. `cat .e*`, `type .en?`, `cat .[e]nv`, `cat ?env`
function globHitsEnv(cmd) {
  const tokens = cmd.split(/[\s"'`;|&()<>]+/).filter(Boolean);
  for (const tok of tokens) {
    const base = tok.split(/[\/\\]/).pop();
    if (!/[*?\[{]/.test(base)) continue;
    let re = "";
    for (const ch of base) {
      if (ch === "*") re += ".*";
      else if (ch === "?") re += ".";
      else if (ch === "[" || ch === "]" || ch === "-" || ch === "!" || ch === "^") re += ch === "!" ? "^" : ch;
      else if (ch === "{" ) re += "(";
      else if (ch === "}") re += ")";
      else if (ch === ",") re += "|";
      else re += ch.replace(/[.+^$()|\\]/g, "\\$&");
    }
    try {
      const r = new RegExp(`^${re}$`, "i");
      if ([".env", ".env.local", ".env.production", ".env.development"].some((n) => r.test(n))) return tok;
    } catch {
      return tok; // unparseable glob in a shell command — be safe
    }
  }
  return null;
}

let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (c) => (raw += c));
process.stdin.on("end", () => {
  try {
    const data = JSON.parse(raw || "{}");
    const tool = data.tool_name || "";
    const input = data.tool_input || {};
    const text = JSON.stringify(input).replace(/\\\\/g, "\\"); // un-double JSON backslashes

    if (ENV_PATH.test(text)) BLOCK(`${tool} references a .env file. Access to .env files is forbidden.`);

    // Collect any string field values (command, path, pattern, glob, etc.)
    const values = [];
    (function walk(v) {
      if (typeof v === "string") values.push(v);
      else if (v && typeof v === "object") Object.values(v).forEach(walk);
    })(input);

    // Shell tools: wildcard / encoding tricks
    if (/^(Bash|PowerShell)$/.test(tool)) {
      const cmd = values.join(" ");
      const hit = globHitsEnv(cmd);
      if (hit) BLOCK(`${tool} uses a wildcard (${hit}) that could match a .env file.`);
      if (/\b(dotenv|load_dotenv|python-dotenv)\b/i.test(cmd)) BLOCK(`${tool} tries to load a .env file via dotenv.`);
      if (/\\x2e|\\056|\[char\]\s*46|fromcharcode|base64\s+(-d|--decode)|frombase64string/i.test(cmd))
        BLOCK(`${tool} uses character/base64 encoding that could be used to reach a .env file.`);
    }

    // Glob/Grep tools: patterns that would match .env
    if (/^(Glob|Grep)$/.test(tool)) {
      const g = globHitsEnv(values.join(" "));
      if (g) BLOCK(`${tool} pattern (${g}) could match a .env file.`);
    }

    // Protect the guard itself from being edited or removed
    if (GUARD_FILES.test(text) && !/^(Read|Glob|Grep)$/.test(tool))
      BLOCK(`${tool} would modify the .env protection hook/settings. This is not allowed.`);

    process.exit(0);
  } catch (e) {
    BLOCK(`hook error (failing closed): ${e.message}`);
  }
});
