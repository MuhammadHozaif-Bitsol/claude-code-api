# Claude API Course

My work from the Anthropic Claude API course: Python scripts that call Claude through the official `anthropic` SDK, one folder per topic.

## Folders

| Folder | What it does |
|---|---|
| `basics/` | Multi-turn conversations, an interactive chat loop with a system prompt, and getting clean JSON back by prefilling the reply and using a stop sequence. |
| `prompt_eval/` | A first prompt-evaluation pipeline: generates a test dataset, runs a prompt on each case, and grades the output with a model grader plus a code grader (JSON / Python / regex syntax checks). |
| `prompt_evaluator/` | A reusable `PromptEvaluator` class that generates test cases, runs them concurrently, grades them against extra criteria, and writes an HTML report. Used to improve an athlete meal-plan prompt with prompt-engineering techniques (XML tags, specific guidelines, a one-shot example). |
| `tools/` | Tool use: Claude calls Python functions (get the current date and time, add a duration to a date, set a reminder). A conversation loop runs each requested tool, sends the results back, and repeats until Claude gives a final answer. |

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

Create a `.env` file in the project root with your API key (it is git-ignored):

```
ANTHROPIC_API_KEY=your-key-here
```

## Running

Run each script from its own folder, because the modules import each other by name:

```bash
cd tools
uv run python main.py
```

The same goes for `basics/`, `prompt_eval/`, and `prompt_evaluator/`.

## Linting

```bash
uvx ruff check .
uvx ruff format .
```
