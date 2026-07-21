# Contributing to PixelMatrix Engine

Thank you for your interest in contributing to **PixelMatrix Engine**!

## Development Guidelines

1. **Architecture & Standards**:
   - Python modules in `skills/pixelmatrix-engine/scripts/` must be strictly typed (`typing`, `dataclasses`, `pathlib`).
   - All scripts must expose a CLI interface with a `--json` output flag.
   - Specification JSONs in `specs/` must strictly conform to standard JSON schema validation.

2. **Branch & Release Workflow**:
   - Create semantic release branches (`v<MAJOR>.<MINOR>.<PATCH>`).
   - Update `CHANGELOG.md` and `index.html` (/changelog route view) for any feature additions or fixes.
   - Never push breaking changes directly to the `main` branch.

3. **Submitting Changes**:
   - Run tests and CLI scripts to verify zero regressions.
   - Create a Pull Request against the designated version branch.
