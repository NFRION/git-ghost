# git-ghost

Summon the ghost of your past self from your oldest commits.

git-ghost reads the first and the latest commits of any git repository and lets
Gemma, an open-weight model running locally through Ollama, speak as the ghost of
the developer you used to be: what it remembers, what it sees now, and one piece
of advice before it fades.

100% local. No API key. Your code never leaves your machine.

## Install

1. Install [Ollama](https://ollama.com), then: `ollama pull gemma3:4b`
2. `git clone https://github.com/NFRION/git-ghost && cd git-ghost`
   (Python 3.8+, no dependencies)

## Run

```bash
python git_ghost.py /path/to/your/repo
python git_ghost.py . --model gemma3:12b --first 20 --last 20
```

## Test

```bash
python test_git_ghost.py
```

Uses a fake local Ollama server and a throwaway repo, so no model is needed.

## License

MIT
