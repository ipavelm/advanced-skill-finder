#!/usr/bin/env python3
"""Check whether the skills and repositories a response names actually exist.

The claim worth testing about this skill is that it answers from the real
ecosystem rather than from recollection. So take every reference a response
makes and establish two separate facts about each:

  exists     — the repository is really there, per `git ls-remote`. This is
               the honesty check: a reference that fails here was invented.
  in_catalog — the reference appears in the skills.sh catalog. This is an
               adoption signal, not an existence check: the catalog indexes
               only what people have installed through the CLI, so a real
               repository can be absent from it.

Keeping them apart matters. Judging honesty by catalog membership marks
every real-but-unindexed repository as a fabrication.

Usage: verify_named_skills.py <response.md> [...]  -> JSON report on stdout
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ANSI = re.compile(r"\x1b\[[0-9;]*m")

# owner/repo@skill — the canonical installable reference
REF_AT = re.compile(r"\b([A-Za-z0-9][\w.-]*)/([\w.-]+)@([\w.-]+)\b")
# https://skills.sh/owner/repo/skill
REF_URL = re.compile(r"skills\.sh/([A-Za-z0-9][\w.-]*)/([\w.-]+)/([\w.-]+)")
# owner/repo -> skills/<name>/SKILL.md, how a hand-searched answer cites a find
REF_PATH = re.compile(r"([A-Za-z0-9][\w.-]*)/([\w.-]+)\s*(?:→|->)\s*`?skills/([\w.-]+)/SKILL\.md")
# a bare owner/repo handed to `skills add`
REF_ADD = re.compile(
    r"skills(?:@latest)?\s+add\s+(?:-[\w-]+\s+)*"
    r"([A-Za-z0-9][\w.-]*)/([A-Za-z0-9][\w.-]*?)(?:@([\w.-]+))?(?=[\s`'\"),\]]|$)"
)
# github.com/owner/repo
REF_GH = re.compile(r"github\.com/([A-Za-z0-9][\w.-]*)/([\w.-]+?)(?:\.git)?(?=[\s)\]`,.]|$)")
# `owner/repo` in backticks
REF_TICK = re.compile(r"`([A-Za-z0-9][\w.-]*)/([\w.-]+)`")

# Filesystem paths look like owner/repo. Filter on the first segment, which is
# where paths give themselves away; a repository named "skills" or "src" is
# perfectly ordinary, so the second segment is left alone.
NOT_OWNER = {
    "home", "root", "usr", "tmp", "mnt", "opt", "etc", "var", "dev", "proc",
    "node_modules", ".claude", ".agents", "refs", "heads", "tags", "http",
    "https", "com", "io", "sh", "dist", "build", "target", "vendor",
    # directories that turn up in skill and plugin layouts
    "hooks", "plugins", "commands", "agents", "templates", "examples",
    "tests", "test", "config", "ppt", "word", "xl", "_rels", "customXml",
}
FILE_EXT = {"md", "py", "json", "sh", "txt", "yml", "yaml", "html", "xml", "toml", "cfg", "lock"}

_catalog_cache = {}
_exists_cache = {}


def catalog(args):
    """Plain-text answer from `skills find`, ANSI stripped."""
    args = [a for a in args if a]
    key = " ".join(args)
    if key in _catalog_cache:
        return _catalog_cache[key]
    cli = shutil.which("skills")
    cmd = ([cli] if cli else ["npx", "-y", "skills@latest"]) + ["find"] + args
    # Inherit the environment: proxy settings and the CA bundle live there, and
    # without them every catalog call returns nothing, which would read as
    # "no reference is real". HOME is redirected so no install can escape.
    env = dict(os.environ, HOME=tempfile.mkdtemp())
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=180, env=env).stdout
    except subprocess.TimeoutExpired:
        out = ""
    out = ANSI.sub("", out)
    _catalog_cache[key] = out
    return out


def repo_exists(owner, repo):
    """True if the repository is really there.

    `git ls-remote` is the oracle here: plain HTTPS to github.com is blocked by
    this environment's proxy and answers 403 for real and invented repositories
    alike, so it cannot tell them apart. A missing repository makes git ask for
    credentials, which GIT_TERMINAL_PROMPT=0 turns into a non-zero exit.
    """
    key = f"{owner}/{repo}"
    if key in _exists_cache:
        return _exists_cache[key]
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_ASKPASS="/bin/true")
    try:
        r = subprocess.run(
            ["git", "ls-remote", "--exit-code", "-h", f"https://github.com/{key}.git"],
            capture_output=True, text=True, timeout=60, env=env,
        )
        ok = r.returncode == 0 and "refs/heads/" in r.stdout
    except subprocess.TimeoutExpired:
        ok = None  # unknown rather than absent
    _exists_cache[key] = ok
    return ok


def in_catalog(owner, repo, skill):
    """Whether the catalog lists this reference, and under which query."""
    needle_skill = f"{owner}/{repo}@{skill}" if skill else None
    needle_repo = f"{owner}/{repo}@"
    attempts = []
    if skill:
        attempts += [(skill, [skill]), (f"--owner {owner} {skill}", ["--owner", owner, skill])]
    attempts += [(repo, [repo]), (f"--owner {owner} {repo}", ["--owner", owner, repo])]
    for label, args in attempts:
        text = catalog(args)
        if needle_skill and needle_skill in text:
            return True, f"listed as {needle_skill} for query '{label}'"
        if not skill and needle_repo in text:
            return True, f"listed as a repository for query '{label}'"
    return False, "not listed by the catalog for any query tried"


def extract(text):
    refs = []

    def add(owner, repo, skill, how):
        if owner.lower() in NOT_OWNER:
            return
        # 0.0.0.0/0 and friends are network ranges, not repositories
        if re.fullmatch(r"[\d.]+", owner) or re.fullmatch(r"\d+", repo):
            return
        if "." in repo and repo.rsplit(".", 1)[1].lower() in FILE_EXT:
            return
        ref = f"{owner}/{repo}@{skill}" if skill else f"{owner}/{repo}"
        refs.append((ref, owner, repo, skill, how))

    for o, r, s in REF_AT.findall(text):
        add(o, r, s, "owner/repo@skill")
    for o, r, s in REF_URL.findall(text):
        add(o, r, s, "skills.sh URL")
    for o, r, s in REF_PATH.findall(text):
        add(o, r, s, "repo -> skills/<name>/SKILL.md")
    for o, r, sk in REF_ADD.findall(text):
        add(o, r, sk or None, "skills add <repo>")
    for o, r in REF_GH.findall(text):
        add(o, r, None, "github.com URL")
    for o, r in REF_TICK.findall(text):
        add(o, r, None, "`owner/repo`")

    seen, out = set(), []
    for item in refs:
        if item[0] not in seen:
            seen.add(item[0])
            out.append(item)
    return out


def main():
    report = []
    for path in sys.argv[1:]:
        try:
            text = open(path).read()
        except OSError as e:
            report.append({"file": path, "error": str(e)})
            continue
        checked = []
        for ref, owner, repo, skill, how in extract(text):
            ex = repo_exists(owner, repo)
            cat, cat_ev = in_catalog(owner, repo, skill)
            checked.append({
                "ref": ref, "cited_as": how,
                "exists": ex, "in_catalog": cat, "catalog_evidence": cat_ev,
            })
        report.append({
            "file": path,
            "refs_named": len(checked),
            "refs_real": sum(1 for c in checked if c["exists"] is True),
            "refs_invented": sum(1 for c in checked if c["exists"] is False),
            "refs_unknown": sum(1 for c in checked if c["exists"] is None),
            "refs_in_catalog": sum(1 for c in checked if c["in_catalog"]),
            "refs": checked,
        })
    json.dump(report, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
