# DeepTutor Reading Plugins

Working examples and a development guide for DeepTutor's Immersive Reading
extension protocol. Extensions are standalone Python packages that add
toolbar actions such as dictionary lookup, quizzes, or read-aloud to the
Immersive Reading workspace.

## How it works

DeepTutor discovers reading extensions through the
`deeptutor.reading_extensions` Python entry-point group. Your package
registers an entry point, provides a manifest, and implements a
`run_action(action, context)` method. DeepTutor validates the manifest,
loads your extension, and renders its results in the Reader toolbar.

Extensions run on the server, never in the browser. They receive a
server-verified reading context and return one of four validated result
types. A broken optional package is skipped without affecting the reader or
other extensions.

## Quick start

```bash
cd examples/dictionary
pip install -e .
deeptutor serve
```

Open the Immersive Reading workspace, select a word or phrase, and click the
"Look up word" toolbar button.

## Write your own

### 1. Declare the entry point

In your `pyproject.toml`:

```toml
[project.entry-points."deeptutor.reading_extensions"]
my_extension = "my_package:MyExtension"
```

The entry-point name must match the `manifest.id`.

### 2. Implement the extension

```python
from deeptutor.reading.extensions import (
    ReadingAction,
    ReadingExtensionManifest,
    ReadingExtensionResult,
)


class MyExtension:
    manifest = ReadingExtensionManifest(
        id="my_extension",
        version="1.0.0",
        name="My Extension",
        actions=[
            ReadingAction(id="run", label="Run", requires=["selection"]),
        ],
        result_types=["card"],
    )

    def run_action(self, action, context):
        if action != "run":
            raise ValueError(f"Unsupported action: {action}")
        return ReadingExtensionResult(
            type="card",
            title="My result",
            message=f"Selected: {context.selection[:200]}",
        )
```

### 3. Install and restart

```bash
pip install -e .
```

Restart DeepTutor. The extension appears in the Reader toolbar.

## Result types

| Type | Payload | Description |
|------|---------|-------------|
| `card` | Free-form up to 64 KB | Rendered as a text card |
| `quiz` | `questions` list with `prompt`, `choices`, `correct_choice_index` | Interactive multiple-choice quiz |
| `feedback` | Free-form up to 64 KB | Short feedback message |
| `browser_speech` | `text` string up to 60,000 chars | Browser text-to-speech |

## Security boundary

- The server resolves the material, locator, source anchor, and unit text.
  The browser cannot supply arbitrary values.
- A selection is forwarded only when it occurs verbatim in the stored unit.
- Results are rendered as React text; extensions cannot inject JavaScript or
  raw HTML.
- Units larger than 60,000 characters are rejected before extension
  invocation.
- Actions have a 30-second timeout; stuck extensions are circuit-broken.
- One broken package does not affect other extensions or document loading.

## Examples

| Example | Actions | LLM required |
|---------|---------|--------------|
| [Dictionary](examples/dictionary/) | Look up word | No |
| [Simple quiz](examples/quiz/) | Quiz me | No |

## License

MIT
