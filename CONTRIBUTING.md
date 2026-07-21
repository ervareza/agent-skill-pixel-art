# Contributing to ChromaMatrix Core

Thank you for contributing to **ChromaMatrix Core**!

## Development Guidelines

1. **Architecture & Terminology**:
   - Python micro-modules under `skills/chromamatrix-core/RenderOrchestrators/` must be strictly typed (`typing`, `pathlib`).
   - All modules must expose a CLI interface with a `--json` output flag.
   - Banned terms (`template`, `spec`, `reference`, `script`, `config`, `pipeline`, `preset`, `utils`, `helpers`) are strictly forbidden. Use `RasterBlueprints`, `ManifestVault`, `PixelProtocols`, `RenderOrchestrators`, `GridMatrices`, etc.
   - Manifest JSON files in `ManifestVault/` must strictly conform to JSON schema validation.

2. **Branch & Release Workflow**:
   - Create semantic release branches (`v<MAJOR>.<MINOR>.<PATCH>`).
   - Update `CHANGELOG.md` and `index.html` (/changelog route view) for any feature additions or fixes.
   - Never push directly to the `main` branch.

3. **Submitting Changes**:
   - Run tests and CLI modules to verify zero regressions.
   - Create a Pull Request against the designated version branch.
