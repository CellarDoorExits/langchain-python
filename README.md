# cellar-door-langchain 𓉸

[![PyPI](https://img.shields.io/pypi/v/cellar-door-langchain)](https://pypi.org/project/cellar-door-langchain/)
[![tests](https://img.shields.io/badge/tests-11_passing-brightgreen)]()
[![Python](https://img.shields.io/pypi/pyversions/cellar-door-langchain)](https://pypi.org/project/cellar-door-langchain/)
[![license](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)

> **⚠️ Pre-release software -- no formal security audit has been conducted.** See [SECURITY.md](SECURITY.md).

LangChain callback handler for EXIT Protocol departure markers. Automatically creates signed departure records when chains or agents complete execution.

## Quick Start

```bash
pip install cellar-door-langchain
```

```python
from cellar_door_langchain import ExitCallbackHandler

handler = ExitCallbackHandler(origin="my-app")

# Use with any LangChain chain
chain.invoke({"input": "hello"}, config={"callbacks": [handler]})

# Markers are collected automatically
print(handler.markers[-1].id)  # urn:exit:abc123...
```

## Configuration

```python
from cellar_door_exit import ExitType

handler = ExitCallbackHandler(
    origin="my-platform",        # Platform name (default: "langchain")
    exit_type=ExitType.VOLUNTARY, # Exit type (default: VOLUNTARY)
    on_marker=my_callback,       # Called on each new marker
    max_markers=500,             # Memory limit (default: 1000)
)
```

## API

| Method | Description |
|--------|-------------|
| `handler.markers` | List of collected `ExitMarker` objects |
| `handler.markers_to_json()` | Export all markers as JSON array |
| `handler.clear()` | Remove all stored markers |

## How It Works

The handler hooks into LangChain's callback system:
- `on_chain_end` -- creates a marker when any chain completes
- `on_agent_finish` -- creates a marker when an agent finishes

Each marker is a cryptographically signed departure record with a content-addressed ID, verifiable offline by anyone.

## 🗺️ Ecosystem

| Package | Description |
|---------|-------------|
| [cellar-door-exit](https://github.com/CellarDoorExits/exit-python) (Python) | Core protocol -- departure markers |
| **[cellar-door-langchain](https://github.com/CellarDoorExits/langchain-python) (Python)** | **← you are here** |
| [cellar-door-exit](https://github.com/CellarDoorExits/exit-door) (TypeScript) | Core protocol (reference implementation) |
| [@cellar-door/langchain](https://github.com/CellarDoorExits/langchain) (TypeScript) | LangChain integration (TypeScript) |

**[Paper](https://cellar-door.dev/paper/) · [Website](https://cellar-door.dev)**

## License

MIT
