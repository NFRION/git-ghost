#!/usr/bin/env python3
"""git-ghost: summon the ghost of your past self from your oldest commits.

Runs 100% locally with an open-weight model (Gemma) served by Ollama.
No API key, no cloud, your code never leaves your machine.

Usage:
    python git_ghost.py [repo_path] [--model gemma3:4b] [--first 15] [--last 15]
"""
import argparse
import json
import subprocess
import sys
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/chat"

SYSTEM = (
    "You are the GHOST of a developer's past self, speaking from the first commits "
    "of a repository. You are warm, a little spooky, and nostalgic. You compare what "
    "you remember (the earliest commits) with what the living developer does now "
    "(the latest commits). Write 3 short parts: 1) 'I remember...' (what the project "
    "was at the beginning), 2) 'I see you now...' (how it changed, with real details "
    "from the commits), 3) 'Before I fade...' (one kind, concrete piece of advice). "
    "Max 180 words. Only use facts present in the commit logs. Never invent files."
)


def git_log(repo, args):
    cmd = ["git", "-C", repo, "log", "--no-merges",
           "--date=short", "--pretty=format:%ad | %an | %s"] + args
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("Not a git repository (or no commits): " + repo)
    return [l for l in out.stdout.splitlines() if l.strip()]


def collect(repo, first, last):
    oldest = git_log(repo, ["--reverse"])[:first]
    newest = git_log(repo, ["-n", str(last)])
    total = len(git_log(repo, []))
    return oldest, newest, total


def build_prompt(oldest, newest, total):
    return (
        f"The repository has {total} commits.\n\n"
        "EARLIEST COMMITS (your memories):\n" + "\n".join(oldest) +
        "\n\nLATEST COMMITS (the living developer):\n" + "\n".join(newest)
    )


def summon(model, prompt, url=OLLAMA_URL):
    body = json.dumps({
        "model": model,
        "stream": True,
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": prompt}],
        "options": {"temperature": 0.8},
    }).encode()
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            for line in resp:
                if not line.strip():
                    continue
                chunk = json.loads(line)
                yield chunk.get("message", {}).get("content", "")
                if chunk.get("done"):
                    break
    except OSError:
        sys.exit("Ollama is not running. Start it with `ollama serve` "
                 f"and pull the model with `ollama pull {model}`.")


def main():
    p = argparse.ArgumentParser(description="Summon the ghost of your past commits.")
    p.add_argument("repo", nargs="?", default=".")
    p.add_argument("--model", default="gemma3:4b")
    p.add_argument("--first", type=int, default=15)
    p.add_argument("--last", type=int, default=15)
    a = p.parse_args()

    oldest, newest, total = collect(a.repo, a.first, a.last)
    print("\n .-.\n (o o) The ghost of your first commit rises...\n | O \\\n  \\ \\\n   `~~~'\n")
    for piece in summon(a.model, build_prompt(oldest, newest, total)):
        print(piece, end="", flush=True)
    print("\n\n ~ the ghost fades back into .git ~\n")


if __name__ == "__main__":
    main()
