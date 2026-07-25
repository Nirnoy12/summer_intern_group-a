#!/usr/bin/env node
/**
 * Frontend Environment Verification Script
 * =========================================
 * Run: npm run verify   (from the frontend/ directory)
 *
 * Checks:
 *  1. Node.js version is compatible
 *  2. Required environment variables are set
 *  3. Backend API is reachable
 *  4. Dependency integrity (node_modules exists)
 */

import { readFileSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");

// ─── ANSI Colors ──────────────────────────────────────────────────────────────
const GREEN  = "\x1b[32m";
const RED    = "\x1b[31m";
const YELLOW = "\x1b[33m";
const CYAN   = "\x1b[36m";
const RESET  = "\x1b[0m";
const BOLD   = "\x1b[1m";

let passed = 0;
let failed = 0;
let warned = 0;

function ok(label, detail = "") {
  console.log(`  ${GREEN}✔${RESET} ${label}${detail ? `  ${CYAN}(${detail})${RESET}` : ""}`);
  passed++;
}

function fail(label, hint = "") {
  console.log(`  ${RED}✘${RESET} ${BOLD}${label}${RESET}`);
  if (hint) console.log(`      ${YELLOW}→ ${hint}${RESET}`);
  failed++;
}

function warn(label, hint = "") {
  console.log(`  ${YELLOW}⚠${RESET} ${label}`);
  if (hint) console.log(`      ${CYAN}→ ${hint}${RESET}`);
  warned++;
}

function section(title) {
  console.log(`\n${BOLD}${CYAN}── ${title} ${"─".repeat(Math.max(0, 50 - title.length))}${RESET}`);
}

console.log(`\n${BOLD}${CYAN}╔══════════════════════════════════════════════════╗${RESET}`);
console.log(`${BOLD}${CYAN}║   LMS Frontend — Environment Verification        ║${RESET}`);
console.log(`${BOLD}${CYAN}╚══════════════════════════════════════════════════╝${RESET}\n`);

// ─── 1. Node.js Version ────────────────────────────────────────────────────────
section("Node.js Version");
const nodeVersion = process.version; // e.g. "v20.11.0"
const major = parseInt(nodeVersion.slice(1).split(".")[0], 10);
if (major >= 20 && major < 23) {
  ok(`Node.js ${nodeVersion}`, "compatible");
} else if (major >= 18) {
  warn(`Node.js ${nodeVersion} (recommended: v20.x or v22.x)`, "Consider using nvm to switch: nvm use 20");
} else {
  fail(`Node.js ${nodeVersion} is too old`, "Install Node.js v20 LTS from https://nodejs.org");
}

// npm version
try {
  const npmVersion = execSync("npm --version", { encoding: "utf8" }).trim();
  const npmMajor = parseInt(npmVersion.split(".")[0], 10);
  if (npmMajor >= 10) {
    ok(`npm v${npmVersion}`, "compatible");
  } else {
    warn(`npm v${npmVersion} (recommended: v10+)`, "Run: npm install -g npm@latest");
  }
} catch {
  fail("npm not found", "Install Node.js from https://nodejs.org (npm is bundled)");
}

// ─── 2. Dependencies ───────────────────────────────────────────────────────────
section("Dependencies");
if (existsSync(join(ROOT, "node_modules"))) {
  ok("node_modules exists");
  // Check key packages
  const keyPkgs = ["react", "react-router-dom", "axios", "framer-motion", "lucide-react"];
  for (const pkg of keyPkgs) {
    if (existsSync(join(ROOT, "node_modules", pkg))) {
      ok(`  ${pkg}`, "installed");
    } else {
      fail(`  ${pkg} is missing`, "Run: npm install");
    }
  }
} else {
  fail("node_modules not found", "Run: npm install  (from the frontend/ directory)");
}

// ─── 3. Required Config Files ─────────────────────────────────────────────────
section("Configuration Files");
const requiredFiles = [
  ["vite.config.ts", "Vite configuration"],
  ["tsconfig.json", "TypeScript configuration"],
  ["tailwind.config.js", "Tailwind CSS configuration"],
  ["index.html", "HTML entry point"],
  ["src/main.tsx", "React entry point"],
  ["src/App.tsx", "Root App component"],
];

for (const [file, label] of requiredFiles) {
  if (existsSync(join(ROOT, file))) {
    ok(`${file}`, label);
  } else {
    fail(`${file} is missing`, `${label} file not found — was it deleted?`);
  }
}

// ─── 4. Source Directory Structure ────────────────────────────────────────────
section("Source Directory Structure");
const requiredDirs = [
  "src/auth",
  "src/dashboard",
  "src/course-player",
  "src/landing",
  "src/ui",
  "src/theme",
  "src/types",
];

for (const dir of requiredDirs) {
  if (existsSync(join(ROOT, dir))) {
    ok(dir);
  } else {
    fail(`${dir} directory is missing`, "Feature directories should not be deleted");
  }
}

// ─── 5. Backend Connectivity ──────────────────────────────────────────────────
section("Backend API Connectivity");
const BACKEND_URL = "http://localhost:8000";

try {
  // Use built-in fetch (Node 18+)
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 3000);

  const response = await fetch(`${BACKEND_URL}/`, { signal: controller.signal });
  clearTimeout(timeout);

  if (response.ok) {
    const data = await response.json();
    ok(`Backend reachable at ${BACKEND_URL}`, data.message || "OK");
  } else {
    warn(`Backend returned ${response.status}`, "Backend is running but returned an error");
  }
} catch (err) {
  if (err.name === "AbortError") {
    warn("Backend timed out (3s)", "Start it with: cd backend && uvicorn main:app --reload");
  } else {
    warn(`Backend not reachable at ${BACKEND_URL}`, "Start it with: cd backend && uvicorn main:app --reload");
  }
}

// ─── 6. TypeScript Compilation Check ─────────────────────────────────────────
section("TypeScript Compilation");
try {
  execSync("npx tsc --noEmit", { cwd: ROOT, stdio: "pipe", encoding: "utf8" });
  ok("TypeScript compiles without errors");
} catch (err) {
  const output = err.stdout || err.stderr || "";
  const errorCount = (output.match(/error TS/g) || []).length;
  fail(
    `TypeScript has ${errorCount} error(s)`,
    "Run: npm run typecheck  for full error output"
  );
}

// ─── Summary ──────────────────────────────────────────────────────────────────
console.log(`\n${BOLD}${"═".repeat(52)}${RESET}`);
console.log(`  ${GREEN}${BOLD}Passed:  ${passed}${RESET}  |  ${YELLOW}${BOLD}Warnings: ${warned}${RESET}  |  ${RED}${BOLD}Failed: ${failed}${RESET}`);
console.log(`${"═".repeat(52)}\n`);

if (failed > 0) {
  console.log(`${RED}${BOLD}✘ Verification failed. Fix the issues above before continuing.${RESET}\n`);
  process.exit(1);
} else if (warned > 0) {
  console.log(`${YELLOW}${BOLD}⚠ Verification passed with warnings. Review them above.${RESET}\n`);
  process.exit(0);
} else {
  console.log(`${GREEN}${BOLD}✔ All checks passed! You're ready to develop.${RESET}`);
  console.log(`  ${CYAN}Start the dev server: npm run dev${RESET}\n`);
  process.exit(0);
}
