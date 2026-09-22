#!/usr/bin/env python3

from pathlib import Path
import subprocess
import re
import sys

repo = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

def run(*args):
    try:
        return subprocess.check_output(
            args, cwd=repo, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return ""

findings = []
score = 100

def add(level, title, detail):
    global score
    score -= {"BLOCKER": 20, "IMPORTANT": 8, "POLISH": 3}[level]
    findings.append((level, title, detail))

if not (repo / ".git").exists():
    add("BLOCKER", "Not a Git repository", "No .git directory found.")

if run("git", "status", "--porcelain"):
    add("IMPORTANT", "Working tree is not clean",
        "Commit or review local changes before release.")

if not run("git", "remote", "get-url", "origin"):
    add("IMPORTANT", "No origin remote",
        "Add a GitHub remote before publishing.")

tracked = run("git", "ls-files").splitlines()

sensitive = re.compile(
    r"(^|/)(\.env|id_rsa|id_ed25519|credentials?|secrets?)(\.|$)", re.I
)

safe_env_files = {".env.example", ".env.template", ".env.sample"}

for f in tracked:
    name = Path(f).name
    if name in safe_env_files:
        continue
    if sensitive.search(f):
        add("BLOCKER", "Sensitive-looking file is tracked", f)

gitignore = repo / ".gitignore"
if not gitignore.exists():
    add("IMPORTANT", "Missing .gitignore",
        "Add exclusions for secrets and generated files.")
else:
    text = gitignore.read_text(errors="ignore")
    if ".env" not in text:
        add("BLOCKER", ".env is not ignored",
            "Add .env to .gitignore.")

secret_patterns = [
    re.compile(r"sk-or-v1-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{30,}"),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]

for rel in tracked:
    path = repo / rel
    try:
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        content = path.read_text(errors="ignore")
    except Exception:
        continue

    if any(p.search(content) for p in secret_patterns):
        add("BLOCKER", "Possible secret detected", rel)

if not any((repo / x).exists() for x in (".env.example", ".env.template")):
    add("IMPORTANT", "No safe environment example",
        "Add .env.example with placeholder values if configuration is required.")

readme = repo / "README.md"

if not readme.exists():
    add("BLOCKER", "Missing README",
        "Public repositories need a clear README.")
    readme_text = ""
else:
    readme_text = readme.read_text(errors="ignore").lower()

    if len(readme_text) < 500:
        add("IMPORTANT", "README is very short",
            "Explain value, setup, usage, and architecture.")

    if not any(x in readme_text for x in
               ("install", "setup", "quick start", "getting started")):
        add("IMPORTANT", "No obvious setup instructions",
            "Add an Installation or Quick Start section.")

    tech_markers = (
        "tech stack", "technology", "built with", "tech:", "**tech:**",
        "python", "fastapi", "next.js", "nextjs", "react", "typescript",
        "javascript", "docker", "kubernetes", "nginx"
    )
    if not any(x in readme_text for x in tech_markers):
        add("POLISH", "Tech stack is not obvious",
            "Make technologies easy to scan.")

    if not re.search(r"https?://", readme_text):
        add("POLISH", "README has no external links",
            "Add a demo or project link when applicable.")

    if not any(x in readme_text for x in
               ("![", "<img", "github.com/user-attachments")):
        add("POLISH", "No screenshot or demo media",
            "Add at least one screenshot or demo when applicable.")

if not any((repo / x).exists() for x in
           ("LICENSE", "LICENSE.md", "LICENSE.txt")):
    add("IMPORTANT", "No license",
        "Add a license if reuse is intended.")

has_tests = any(
    p.is_file() and (
        p.name.startswith("test_")
        or p.name.endswith(".test.ts")
        or p.name.endswith(".test.js")
    )
    for p in repo.rglob("*")
)

if not has_tests:
    add("POLISH", "No obvious tests detected",
        "Tests improve confidence in a public repo.")

if (repo / "package.json").exists():
    if not any((repo / x).exists() for x in
               ("package-lock.json", "pnpm-lock.yaml", "yarn.lock")):
        add("IMPORTANT", "JavaScript dependencies are not locked",
            "Commit a dependency lockfile.")

score = max(0, score)

if any(x[0] == "BLOCKER" for x in findings):
    verdict = "NOT READY"
elif any(x[0] == "IMPORTANT" for x in findings):
    verdict = "READY WITH FIXES"
else:
    verdict = "READY"

print("# Repo Doctor Report\n")
print(f"**Repository:** `{repo}`")
print(f"**Score:** {score}/100")
print(f"**Release verdict:** **{verdict}**\n")

for level in ("BLOCKER", "IMPORTANT", "POLISH"):
    rows = [x for x in findings if x[0] == level]
    print(f"## {level.title()}\n")
    if not rows:
        print("None.\n")
    else:
        for _, title, detail in rows:
            print(f"- **{title}** — {detail}")
        print()

print("## Recommended next actions\n")

ordered = (
    [x for x in findings if x[0] == "BLOCKER"]
    + [x for x in findings if x[0] == "IMPORTANT"]
    + [x for x in findings if x[0] == "POLISH"]
)

if not ordered:
    print("Repository looks ready for public release.")
else:
    for i, (_, title, _) in enumerate(ordered[:8], 1):
        print(f"{i}. {title}")
