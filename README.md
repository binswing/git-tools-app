# GTA (Git Tools App)

GTA is a Python command-line wrapper around Git. It forwards ordinary Git commands to your installed `git` executable and adds AI-assisted commit messages plus configurable addons that run before and after selected Git operations.

## Requirements

- Python 3.8 or newer
- Git available on `PATH`
- An AI provider only when using `gta commit`

## Installation

Install:
```bash
# Install from git
pip install git+https://github.com/binswing/git-tools-app.git

# Or from a local clone
git clone https://github.com/binswing/git-tools-app.git
pip install -e git-tools-app
```

<!-- The package installs the `gta` command:

```bash
gta --version
gta status
``` -->

To customize AI commit-message guidance for a project, create `.gta/templates/COMMITMSG.md` in that project's root after installation. GTA uses this project-local file before `~/.gta/templates/COMMITMSG.md` or its packaged default.

```text
your-project/
  .gta/
    templates/
      COMMITMSG.md
```

Commands GTA does not implement are passed through to Git, so `gta status`, `gta log`, and `gta rebase` behave like their `git` equivalents.

## Quick Start

1. Configure an AI provider and model:

   ```bash
   gta setting
   ```

2. Stage your changes:

   ```bash
   git add <files>
   ```

3. Generate and confirm a commit message:

   ```bash
   gta commit
   ```

`gta commit` reads the staged diff and up to five recent commits, asks the configured provider for a Conventional Commit-style subject, displays the proposed message, and commits only after you enter `y`.

## GTA Commands

| Command | Description |
| --- | --- |
| `gta setting` | Opens the interactive configuration interface. |
| `gta commit [--model MODEL] [--no-hooks] [GIT_ARGS...]` | Generates a commit message, then runs `git commit -m <message>` with any extra Git arguments. |
| `gta push [--no-hooks] [GIT_ARGS...]` | Runs configured pre/post push addons around `git push`. |
| `gta checkout [--no-hooks] [GIT_ARGS...]` | Runs configured pre/post checkout addons around `git checkout`. |
| `gta merge [--no-hooks] [GIT_ARGS...]` | Runs configured pre/post merge addons around `git merge`. |
| `gta help [GIT_HELP_ARGS...]` | Shows GTA help with no arguments; otherwise delegates to `git help`. |

Extra arguments are forwarded to Git. For example:

```bash
gta commit --no-verify
gta commit --allow-empty
gta push origin main
gta checkout feature/new-ui
```

Use `--no-hooks` on GTA-managed commands to skip GTA addons. This does not add Git's own `--no-verify` flag; pass that separately when Git supports it.

## Configuration

GTA loads configuration in this order, with later values replacing earlier top-level keys:

1. Built-in defaults
2. Global configuration: `~/.gta/config.json`
3. Local configuration: `.gta/config.json` in the current working directory

The default AI configuration is Ollama with the `llama3` model. Configuration is created or saved through `gta setting`; a representative file is:

```json
{
  "environment": "production",
  "debug": false,
  "ai_provider": "ollama",
  "model": "llama3",
  "addons": [
    {
      "id": "a-unique-id",
      "name": "Play notification",
      "hook_type": "audio",
      "events": ["post-push"],
      "options": {"file": "notification.wav"},
      "enabled": true
    }
  ]
}
```

The merge is shallow. In particular, a local `addons` array replaces the global one rather than extending it.

### Project Resources

GTA resolves `assets/` and `templates/` from a local `.gta` directory first, then `~/.gta`, then packaged fallback resources. The commit generator uses `templates/COMMITMSG.md` as its provider prompt guidance.

When settings import an addon asset or create a config, they use the local `.gta` directory when it already exists; otherwise they use `~/.gta`.

## AI Providers

Choose a provider and its available model from **AI** in `gta setting`. GTA loads variables from a `.env` file at startup as well as the process environment.

| Provider | Configuration | Notes |
| --- | --- | --- |
| `ollama` | No key required | Requires a local Ollama server at `http://localhost:11434`; this is the default. |
| `openai` | `GTA_OPENAI_API_KEY` or `OPENAI_API_KEY` | Uses the OpenAI API. |
| `gemini` | `GTA_GEMINI_API_KEY` or `GEMINI_API_KEY` | Uses the Google Generative Language API. |
| `claude` | `GTA_ANTHROPIC_API_KEY` or `ANTHROPIC_API_KEY` | Uses the Anthropic Messages API. |
| `hf_inference` | `GTA_HF_TOKEN` or `HF_TOKEN` | Uses Hugging Face serverless inference. |

You can temporarily select a model for one commit without saving it:

```bash
gta commit --model your-model-id
```

## Addons and Events

Addons run on these event names:

- `pre-commit`, `post-commit`
- `pre-push`, `post-push`
- `pre-checkout`, `post-checkout`
- `pre-merge`, `post-merge`
- `pre-pull`, `post-pull`

Use the **Addons** and **Events** screens in `gta setting` to create addons, choose events, reorder their execution, edit options, or enable and disable them. Addon failures are logged and do not stop the Git command.

Built-in addon types are:

| Type | Behavior |
| --- | --- |
| `audio` | Plays an audio file from GTA's resolved `assets/` directory. Playback completes before the command continues. |
| `ascii_animation` | Shows a terminal rocket or train animation. Its `speed` option is a string value. |
| `custom_python` | Runs a local Python script with optional arguments. |

`custom_python` runs the selected script with the active Python interpreter. Treat configuration files and scripts referenced by this addon as trusted code.

To add a built-in package hook, create an importable module under `git_tools_app.hooks` that defines `HOOK_SCHEMA` and `execute(addon_options, parsed_args, config_context)`.

## Current Limitations
- Provider and Git network/process failures can terminate the command, and provider requests do not set explicit timeouts.
- GTA appends JSONL diagnostic logs to `~/.gta/gta.log`.
- The repository does not currently include an automated test suite.

## Development

Run the package module directly while developing:

```bash
python -m git_tools_app.main setting
python -m git_tools_app.main commit
```

Runtime dependencies are declared in `pyproject.toml`: `requests`, `pygame`, `questionary`, and `python-dotenv`.
