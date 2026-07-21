# Contributing to PixelForge Studio

Thank you for your interest in contributing to **PixelForge Studio**! We welcome bug reports, feature enhancements, documentation improvements, and new workflow suggestions.

---

## Code of Conduct

Please maintain a respectful, welcoming, and collaborative environment.

---

## Development Setup

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/pixelforge-studio.git
   cd pixelforge-studio
   ```
3. Create a feature branch following semantic versioning or conventional naming (`feat/new-palette-extractor`, `fix/atlas-packer-alignment`).
4. Install development dependencies:
   ```bash
   pip install -r skills/pixelforge-studio/requirements.txt
   ```

---

## Pull Request Guidelines

- Ensure all Python scripts pass syntax compilation:
  ```bash
  python3 -m py_compile skills/pixelforge-studio/scripts/*.py
  ```
- Run CLI `--help` tests across all tools.
- Update `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/).
- Submit your pull request targeting the `main` or release branch.
