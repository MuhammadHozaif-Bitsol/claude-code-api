// PreToolUse hook: keeps Claude away from .env files and stops it disabling this guard.
// Exit 2 = block the call (stderr is shown to Claude). Errors fail closed.
const path = require("path");

const norm = (p) => path.resolve(p).replace(/\\/g, "/").toLowerCase();
const PROJECT = norm(process.env.CLAUDE_PROJECT_DIR || process.cwd());
const GUARDS = [
  ".claude/settings.json",
  ".claude/settings.local.json",
  ".claude/hooks/block-env.js",
].map((p) => PROJECT + "/" + p);
// relative mention of this project's guard files in a shell command (not ~/.claude/...)
const GUARD_IN_SHELL =
  /(^|[\s"'=])(\.\/)?\.claude[\/\\](settings(\.local)?\.json|hooks[\/\\]block-env\.js)|block-env\.js/i;

const ENV_PATH =
  /(^|[\s"'`=:;,(){}\[\]<>|&*\/\\@!$])\.env(?![\w-])(\.[\w.-]*)?/i;
const ENV_NAMES = [".env", ".env.local", ".env.production", ".env.development"];

function block(reason) {
  process.stderr.write("BLOCKED by block-env hook: " + reason + "\n");
  process.exit(2);
}

// Would this wildcard token match a .env file?
// leadingDot: in bash, * ? [..] never match a leading dot, so only globs starting with "." count.
function globHitsEnv(token, leadingDot) {
  const base = token.split(/[\/\\]/).pop();
  if (!/[*?\[{]/.test(base)) return false;
  if (leadingDot && !base.startsWith(".")) return false;
  let re = "";
  for (const ch of base) {
    if (ch === "*") re += ".*";
    else if (ch === "?") re += ".";
    else if (ch === "[" || ch === "]" || ch === "-") re += ch;
    else if (ch === "!") re += "^";
    else if (ch === "{") re += "(";
    else if (ch === "}") re += ")";
    else if (ch === ",") re += "|";
    else re += ch.replace(/[.+^$()|\\]/g, "\\$&");
  }
  try {
    const r = new RegExp("^(" + re + ")$", "i");
    return ENV_NAMES.some((n) => r.test(n));
  } catch {
    return false; // not a real glob (e.g. f"{x}" or arr[0) - don't block
  }
}

let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (c) => (raw += c));
process.stdin.on("end", () => {
  try {
    const data = JSON.parse(raw || "{}");
    const tool = data.tool_name || "";
    const input = data.tool_input || {};
    const isShell = tool === "Bash" || tool === "PowerShell";
    const isWrite = ["Edit", "Write", "NotebookEdit"].includes(tool);

    // For file-writing tools only the TARGET PATH matters, so writing code
    // or a .gitignore that merely mentions .env is fine.
    let fields = [];
    if (isWrite) fields = [input.file_path, input.notebook_path];
    else
      (function walk(v) {
        if (typeof v === "string") fields.push(v);
        else if (v && typeof v === "object") Object.values(v).forEach(walk);
      })(input);
    fields = fields.filter((f) => typeof f === "string");

    // Check raw values (not JSON text), so a newline before .env can't slip through.
    for (const f of fields) {
      if (ENV_PATH.test(f)) block(tool + " references a .env file.");
      if (isShell && ENV_PATH.test(f.replace(/["'`\\]/g, "")))
        block(tool + " references a .env file (quoting trick).");
    }

    if (isShell) {
      const cmd = fields.join(" ");
      for (const tok of cmd.split(/[\s"'`;|&()<>]+/))
        if (tok && globHitsEnv(tok, tool === "Bash"))
          block(tool + " wildcard (" + tok + ") could match a .env file.");
      if (
        /load_dotenv|dotenv_values|dotenv\/config|\bdotenv\s+(get|list|run)\b/i.test(
          cmd,
        )
      )
        block(tool + " tries to load a .env file via dotenv.");
      if (
        /\\x2e|\\056|\[char\]\s*46|fromcharcode|base64\s+(-d|--decode)|frombase64string/i.test(
          cmd,
        )
      )
        block(tool + " uses encoding tricks that could reach a .env file.");
      if (GUARD_IN_SHELL.test(cmd))
        block(tool + " would touch the .env guard's settings or script.");
    }

    if (tool === "Glob")
      for (const seg of String(input.pattern || "").split(/[\/\\]/))
        if (globHitsEnv(seg, true))
          block("Glob pattern could match a .env file.");
    if (tool === "Grep" && input.glob && globHitsEnv(String(input.glob), true))
      block("Grep glob could match a .env file.");

    if (isWrite && fields[0] && GUARDS.includes(norm(fields[0])))
      block(tool + " would modify the .env guard.");

    process.exit(0);
  } catch (e) {
    block("hook error, failing closed: " + e.message);
  }
});
