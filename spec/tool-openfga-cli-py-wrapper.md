---
title: OpenFGA CLI Python Wrapper Package (openfga-cli-py)
version: 1.3
date_created: 2026-07-15
last_updated: 2026-07-15
owner: oss-robin (https://pypi.org/user/oss-robin/)
tags: tool, infrastructure, process, python, packaging, openfga, cli
---

# Introduction

This specification defines the requirements and implementation details for `openfga-cli-py`, a Python package that wraps the pre-built [OpenFGA CLI (`fga`)](https://github.com/openfga/cli) binary and makes it pip-installable. The package follows the same pattern as [`shellcheck-py`](https://github.com/shellcheck-py/shellcheck-py), using `setuptools-download` to fetch and embed the correct platform-specific binary at install time.

## 1. Purpose & Scope

**Purpose**: Provide a `pip install openfga-cli-py` experience that downloads and installs the correct `fga` binary for the user's platform, making it available as a command-line tool in the active Python environment.

**Scope**:
- Repository layout and file contents for `openfga-cli-py`
- `setup.cfg` and `setup.py` configuration using `setuptools-download`
- Platform matrix for v0.7.19 of the OpenFGA CLI
- PyPI publishing workflow
- Shell script to regenerate `setup.cfg` when a new OpenFGA CLI version is released
- CI/CD via GitHub Actions
- Pre-commit hook support

**Audience**: Developers maintaining the `openfga-cli-py` package and AI agents implementing or updating the project.

**Assumptions**:
- The target PyPI account is `oss-robin` at `https://pypi.org/user/oss-robin/`.
- The package name on PyPI is `openfga-cli-py`.
- The internal Python package/module name uses underscores: `openfga_cli_py` (PyPI convention).
- The reference implementation to follow is `shellcheck-py` at `/Users/arul/Public/shellcheck-py`.

---

## 2. Definitions

| Term | Definition |
|------|------------|
| **OpenFGA CLI** | The `fga` binary released at https://github.com/openfga/cli |
| **fga** | The executable binary name for the OpenFGA CLI on Linux/macOS |
| **fga.exe** | The executable binary name for the OpenFGA CLI on Windows |
| **setuptools-download** | A setuptools plugin that downloads and installs external binaries during `pip install` |
| **PEP 508 marker** | Environment marker syntax (e.g., `sys_platform == "linux" and platform_machine == "x86_64"`) used to select platform-specific downloads |
| **Wheel** | A Python binary distribution format (`.whl`); platform-tagged wheels are produced per OS/arch |
| **sdist** | Source distribution (`.tar.gz`); platform-neutral, downloads binary at install time |
| **PyPI** | Python Package Index — the public package registry at https://pypi.org |
| **SLSA** | Supply-chain Levels for Software Artifacts — provenance metadata shipped with OpenFGA CLI releases |
| **SHA-256** | Cryptographic hash used to verify downloaded binary integrity |

---

## 3. Requirements, Constraints & Guidelines

### Requirements

- **REQ-001**: The package MUST install the `fga` binary (or `fga.exe` on Windows) into the Python environment's `bin/` (or `Scripts/`) directory upon `pip install openfga-cli-py`.
- **REQ-002**: The package MUST support all platform/architecture combinations listed in Section 4 (Platform Matrix).
- **REQ-003**: Each downloaded archive MUST be verified against its SHA-256 checksum before extraction.
- **REQ-004**: The package version MUST follow the scheme `<openfga-cli-version>.<packaging-revision>` (e.g., `0.7.19.0`).
- **REQ-005**: A shell script (`update_version.sh`) MUST be provided to regenerate `setup.cfg` for a new OpenFGA CLI release.
- **REQ-006**: The package MUST be publishable to PyPI under the `oss-robin` account using a PyPI API token stored as a GitHub Actions secret (`PYPI_API_TOKEN`) and the `pypa/gh-action-pypi-publish@release/v1` action.
- **REQ-007**: Platform-tagged wheels MUST be built and uploaded so that `pip install` does not need to recompile anything.
- **REQ-008**: The package MUST expose a `fga` console script entry point (or binary via `setuptools-download`) after installation.
- **REQ-009**: All platform-tagged `.whl` files produced during a release MUST be uploaded as GitHub Release assets on the corresponding tag, in addition to being published to PyPI.
- **REQ-010**: The package MUST be usable as a `pre-commit` hook, with a valid `.pre-commit-hooks.yaml` defining a hook id `fga` that invokes the installed binary.

### Security Requirements

- **SEC-001**: Downloaded binaries MUST be verified via SHA-256 checksums sourced from the official `checksums.txt` at the OpenFGA CLI release page.
- **SEC-002**: The PyPI publish workflow MUST authenticate using a scoped PyPI API token (scoped to the `openfga-cli-py` project) stored as the GitHub Actions secret `PYPI_API_TOKEN`. The token MUST NOT be printed in logs.
- **SEC-003**: GitHub Actions workflow steps MUST pin third-party actions to a specific commit SHA or version tag.
- **SEC-004**: The GitHub Release asset upload step MUST use the `GITHUB_TOKEN` provided by the Actions runtime (no additional secrets required for asset uploads).

### Constraints

- **CON-001**: The package uses `setuptools-download`; it MUST NOT bundle the binary in the source tree or sdist.
- **CON-002**: Windows assets use `.tar.gz` archives (same as Linux/macOS); the binary inside is named `fga.exe`.
- **CON-003**: Python `>= 3.10` is required (matching shellcheck-py precedent and modern toolchain needs).
- **CON-004**: The wheel produced is NOT a pure-Python wheel (`root_is_pure = False` in `bdist_wheel`); it is tagged `py2.py3-none-<platform>`.
- **CON-005**: PyPI rejects bare `linux_*` platform tags. Linux wheels MUST use the `manylinux` standard (minimum `manylinux_2_17`). The `_PYTHON_HOST_PLATFORM` environment variable MUST be set to `manylinux_2_17_x86_64` (or equivalent arch) before running `pip wheel`.
- **CON-006**: The macOS `_PYTHON_HOST_PLATFORM` value MUST use dashes in the format `macosx-X.Y-arch` (e.g., `macosx-10.9-x86_64`). Using underscores causes `wheel.macosx_libfile.calculate_macosx_platform_tag` to crash with `ValueError: not enough values to unpack`.

### Guidelines

- **GUD-001**: Follow the file and configuration layout of `shellcheck-py` exactly, substituting `shellcheck`→`fga`/`openfga_cli_py` and updating URLs/hashes accordingly.
- **GUD-002**: Keep `setup.py` minimal — only the `bdist_wheel` subclass overriding `root_is_pure` and `get_tag()`. Import `bdist_wheel` from `setuptools.command.bdist_wheel` first (canonical since setuptools ≥ 70.1), fall back to `wheel.bdist_wheel`, and handle the case where both imports fail by setting `cmdclass = {}`.
- **GUD-003**: Use `make quality` for local testing; it runs `fga version`, `fga help`, `pytest`, and builds the platform wheel.
- **GUD-004**: Provide a `README.md` documenting installation, usage, and pre-commit hook integration.
- **GUD-005**: Set `_PYTHON_HOST_PLATFORM` as an environment variable on the wheel-build step (not as a shell export) so it applies identically on Windows, macOS, and Linux runners.

### Patterns

- **PAT-001**: One `[fga]` / `[fga.exe]` section per platform in `[setuptools_download] download_scripts`.
- **PAT-002**: Group all platform entries under the same group name (`fga-binary`).
- **PAT-003**: The `extract_path` for all platforms is simply `fga` (Linux/macOS) or `fga.exe` (Windows) — the binary sits at the root of each archive.

---

## 4. Interfaces & Data Contracts

### 4.1 Repository File Structure

```
openfga-cli-py/
├── .github/
│   └── workflows/
│       ├── main.yml          # CI: build, test, publish
│       └── publish.yml       # Optional: separate publish workflow
├── spec/
│   └── tool-openfga-cli-py-wrapper.md  # This specification
├── .gitignore
├── .pre-commit-config.yaml
├── .pre-commit-hooks.yaml
├── LICENSE                   # Apache License Version 2.0
├── README.md
├── Makefile                  # Developer workflow: install, quality (test + build wheel)
├── setup.cfg                 # Primary configuration (version, metadata, download specs)
├── setup.py                  # Minimal: bdist_wheel subclass only
└── update_version.sh         # Script to regenerate setup.cfg for new releases
```

### 4.2 `setup.cfg` Structure

```ini
[metadata]
name = openfga-cli-py
version = 0.7.19.0
description = Python wrapper around invoking the OpenFGA CLI (https://github.com/openfga/cli)
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/<owner>/openfga-cli-py
author = oss-robin
author_email = <maintainer-email>
license = Apache License Version 2.0
license_files = LICENSE
classifiers =
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3 :: Only
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy

[options]
python_requires = >=3.10
setup_requires =
    setuptools-download

[setuptools_download]
download_scripts =
    [fga]
    group = fga-binary
    marker = sys_platform == "linux" and platform_machine == "x86_64"
    url = https://github.com/openfga/cli/releases/download/v0.7.19/fga_0.7.19_linux_amd64.tar.gz
    sha256 = 21da629e0f9d29e97d60a11c860e763915c57c354beda25b6e350168c86f67be
    extract = tar
    extract_path = fga
    [fga]
    group = fga-binary
    marker = sys_platform == "linux" and platform_machine == "aarch64"
    url = https://github.com/openfga/cli/releases/download/v0.7.19/fga_0.7.19_linux_arm64.tar.gz
    sha256 = 32196f0f45c046057caab854778c84f05cdef87bfa8c3df1cadee56e31fed85c
    extract = tar
    extract_path = fga
    [fga]
    group = fga-binary
    marker = sys_platform == "linux" and platform_machine == "i686"
    url = https://github.com/openfga/cli/releases/download/v0.7.19/fga_0.7.19_linux_386.tar.gz
    sha256 = 7a110e4693523b8e2205b8b7659fc381730ae295ae1421ed92ae05e2e9f04503
    extract = tar
    extract_path = fga
    [fga]
    group = fga-binary
    marker = sys_platform == "darwin" and platform_machine == "x86_64"
    url = https://github.com/openfga/cli/releases/download/v0.7.19/fga_0.7.19_darwin_amd64.tar.gz
    sha256 = 2240aa4f99beb53c252842069b0663515e5f3751f64bbe3f9aedae9b3270e3fc
    extract = tar
    extract_path = fga
    [fga]
    group = fga-binary
    marker = sys_platform == "darwin" and platform_machine == "arm64"
    url = https://github.com/openfga/cli/releases/download/v0.7.19/fga_0.7.19_darwin_arm64.tar.gz
    sha256 = fa5a24be5a77d7fbaf9e5aff5ea5e8dcab71b72e3351bc442df500ebf29d4130
    extract = tar
    extract_path = fga
    [fga.exe]
    group = fga-binary
    marker = sys_platform == "win32" and platform_machine == "AMD64"
    marker = sys_platform == "cygwin" and platform_machine == "x86_64"
    url = https://github.com/openfga/cli/releases/download/v0.7.19/fga_0.7.19_windows_amd64.tar.gz
    sha256 = c86b4c198ca8360e2076cb46b12dfe77396092f80504d5a32d553bc064c3138c
    extract = tar
    extract_path = fga.exe
    [fga.exe]
    group = fga-binary
    marker = sys_platform == "win32" and platform_machine == "ARM64"
    url = https://github.com/openfga/cli/releases/download/v0.7.19/fga_0.7.19_windows_arm64.tar.gz
    sha256 = 8a005731073657ec319e30099681f33cf327db69e77c2f4622d4e41bc98473f2
    extract = tar
    extract_path = fga.exe
    [fga.exe]
    group = fga-binary
    marker = sys_platform == "win32" and platform_machine == "x86"
    url = https://github.com/openfga/cli/releases/download/v0.7.19/fga_0.7.19_windows_386.tar.gz
    sha256 = 233d463b8aa8d3f1d1602a17c276c35ec33e939e78842d06cbf7058e47a979a0
    extract = tar
    extract_path = fga.exe
```

### 4.3 `setup.py` Structure

```python
from __future__ import annotations
from setuptools import setup

# setuptools >= 70.1 ships bdist_wheel natively; wheel package is the fallback
# for older environments where setuptools delegated to the wheel package.
try:
    from setuptools.command.bdist_wheel import bdist_wheel as orig_bdist_wheel
except ImportError:
    try:
        from wheel.bdist_wheel import bdist_wheel as orig_bdist_wheel
    except ImportError:
        orig_bdist_wheel = None

if orig_bdist_wheel is None:
    cmdclass = {}
else:
    class bdist_wheel(orig_bdist_wheel):
        def finalize_options(self):
            orig_bdist_wheel.finalize_options(self)
            self.root_is_pure = False  # not a pure-python package

        def get_tag(self):
            _, _, plat = orig_bdist_wheel.get_tag(self)
            # No Python source, no extensions — tag as py2.py3 none <platform>
            return 'py2.py3', 'none', plat

    cmdclass = {'bdist_wheel': bdist_wheel}

setup(cmdclass=cmdclass)
```

> **Rationale for import fallback chain**: `setuptools.command.bdist_wheel` is the canonical location since setuptools ≥ 70.1. In earlier versions setuptools delegated to the `wheel` package, so `wheel.bdist_wheel` is tried as a fallback. If both imports fail the wheel command is absent (`cmdclass = {}`), which would produce a `py3-none-any.whl` — this must be treated as a build error.

### 4.4 Platform Matrix (v0.7.19)

| Platform | `sys_platform` | `platform_machine` | Archive | SHA-256 |
|----------|---------------|-------------------|---------|---------|
| Linux x86_64 | `linux` | `x86_64` | `fga_0.7.19_linux_amd64.tar.gz` | `21da629e0f9d29e97d60a11c860e763915c57c354beda25b6e350168c86f67be` |
| Linux arm64 | `linux` | `aarch64` | `fga_0.7.19_linux_arm64.tar.gz` | `32196f0f45c046057caab854778c84f05cdef87bfa8c3df1cadee56e31fed85c` |
| Linux i686 | `linux` | `i686` | `fga_0.7.19_linux_386.tar.gz` | `7a110e4693523b8e2205b8b7659fc381730ae295ae1421ed92ae05e2e9f04503` |
| macOS x86_64 | `darwin` | `x86_64` | `fga_0.7.19_darwin_amd64.tar.gz` | `2240aa4f99beb53c252842069b0663515e5f3751f64bbe3f9aedae9b3270e3fc` |
| macOS arm64 | `darwin` | `arm64` | `fga_0.7.19_darwin_arm64.tar.gz` | `fa5a24be5a77d7fbaf9e5aff5ea5e8dcab71b72e3351bc442df500ebf29d4130` |
| Windows x64 | `win32` | `AMD64` | `fga_0.7.19_windows_amd64.tar.gz` | `c86b4c198ca8360e2076cb46b12dfe77396092f80504d5a32d553bc064c3138c` |
| Windows arm64 | `win32` | `ARM64` | `fga_0.7.19_windows_arm64.tar.gz` | `8a005731073657ec319e30099681f33cf327db69e77c2f4622d4e41bc98473f2` |
| Windows x86 | `win32` | `x86` | `fga_0.7.19_windows_386.tar.gz` | `233d463b8aa8d3f1d1602a17c276c35ec33e939e78842d06cbf7058e47a979a0` |

> **Note**: All archives contain the binary at the root level (`fga` or `fga.exe`). The `extract_path` in `setup.cfg` must match exactly.

### 4.5 `update_version.sh` Shell Script Contract

The script accepts one required argument: the new OpenFGA CLI version string (e.g., `0.7.20`).

**Behaviour**:
1. Validate that the version argument is provided and matches `^[0-9]+\.[0-9]+\.[0-9]+$`.
2. Download `checksums.txt` from `https://github.com/openfga/cli/releases/download/v<VERSION>/checksums.txt`.
3. Parse SHA-256 values for the 8 relevant `.tar.gz` assets.
4. Generate a new `setup.cfg` by substituting the old version, URLs, and SHA-256 values.
5. Write the updated `setup.cfg` to the repository root (overwriting the existing file).
6. Print a summary of changes made.

**Signature**:
```bash
./update_version.sh <NEW_VERSION>
# Example:
./update_version.sh 0.7.20
```

### 4.6 GitHub Actions Workflows

#### `main.yml` — CI + Publish + GitHub Release Asset Upload

The workflow has three jobs that run in sequence on a version tag push, and only the first job runs on PRs/branch pushes.

```yaml
# ──────────────────────────────────────────────────────────────────────────────
# Triggers:
#   push:
#     branches: [main, test-me-*]
#     tags: 'v*'          # e.g. v0.7.19.0
#   pull_request:
#
# Permissions (top-level, tightened per-job as needed):
#   contents: write       # required for GitHub Release asset upload
#   id-token: write       # NOT required (no OIDC); contents: write covers release uploads
# ──────────────────────────────────────────────────────────────────────────────

# Job 1: build-and-test
# Matrix (include-style, 7 entries — one per wheel platform):
#   - os: ubuntu-latest,    arch: '',   wheel-plat: manylinux_2_17_x86_64
#   - os: ubuntu-24.04-arm, arch: '',   wheel-plat: manylinux_2_17_aarch64
#   - os: macos-15-intel,   arch: '',   wheel-plat: macosx-10.9-x86_64     # dashes required
#   - os: macos-latest,     arch: '',   wheel-plat: macosx-11.0-arm64       # dashes required
#   - os: windows-latest,   arch: x64,  wheel-plat: win_amd64
#   - os: windows-latest,   arch: x86,  wheel-plat: win32
#   - os: windows-11-arm,   arch: '',   wheel-plat: win_arm64
#
# Steps:
#   - actions/checkout
#   - actions/setup-python (python-version: "3.10", architecture: ${{ matrix.arch }})
#       # arch is empty for Linux/macOS/WinARM — setup-python uses native arch
#       # arch is 'x64' for windows-latest amd64, 'x86' for windows-latest 32-bit
#   - pip install setuptools wheel setuptools-download
#   - pip install . --no-build-isolation
#   - fga version
#   - fga help
#   - pip wheel --no-deps --no-build-isolation --wheel-dir dist .
#       env:
#         _PYTHON_HOST_PLATFORM: ${{ matrix.wheel-plat }}
#       # Forces the correct PyPI-accepted platform tag:
#       #   Linux  → manylinux_2_17_*  (bare linux_* rejected by PyPI)
#       #   macOS  → macosx-X.Y-arch   (use dashes; avoids runner-specific OS version)
#       #   Windows→ win_amd64/win32/win_arm64
#   - actions/upload-artifact
#       name: wheels-${{ matrix.wheel-plat }}   # unique per entry; avoids collision
#       path: dist/*.whl

# Job 2: publish-pypi  (runs on: tag push only; needs: build-and-test)
# Steps:
#   - actions/download-artifact            # downloads all wheels-* artifacts into dist/
#   - pypa/gh-action-pypi-publish@release/v1
#     with:
#       packages-dir: dist/
#       password: ${{ secrets.PYPI_API_TOKEN }}
#       # PYPI_API_TOKEN must be a project-scoped PyPI API token stored in repo secrets

# Job 3: publish-github-release  (runs on: tag push only; needs: build-and-test)
# Steps:
#   - actions/download-artifact            # downloads all wheels-* artifacts
#                                          # merges into a single dist/ directory
#   - softprops/action-gh-release          # creates/updates GitHub Release for the tag
#     with:
#       files: dist/*.whl                  # attaches every platform wheel as a release asset
#       tag_name: ${{ github.ref_name }}   # e.g. v0.7.19.0
#       fail_on_unmatched_files: true
#     env:
#       GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Key constraint**: Jobs 2 and 3 both depend on `build-and-test` completing successfully across all matrix legs before any publishing begins. They run in parallel once the build job completes.

**Artifact naming convention**: Each build matrix leg uploads its wheel with `wheels-${{ matrix.wheel-plat }}` (e.g., `wheels-manylinux_2_17_x86_64`, `wheels-win32`). Using `wheel-plat` rather than `os` ensures the two `windows-latest` entries (amd64 and x86) produce distinct artifact names and do not overwrite each other.

**`_PYTHON_HOST_PLATFORM` values by entry**:

| Runner | `arch` | `wheel-plat` (= `_PYTHON_HOST_PLATFORM`) | Produced filename tag |
|--------|--------|-------------------------------------------|-----------------------|
| `ubuntu-latest` | — | `manylinux_2_17_x86_64` | `manylinux_2_17_x86_64` |
| `ubuntu-24.04-arm` | — | `manylinux_2_17_aarch64` | `manylinux_2_17_aarch64` |
| `macos-15-intel` | — | `macosx-10.9-x86_64` | `macosx_10_9_x86_64` |
| `macos-latest` (arm64) | — | `macosx-11.0-arm64` | `macosx_11_0_arm64` |
| `windows-latest` | `x64` | `win_amd64` | `win_amd64` |
| `windows-latest` | `x86` | `win32` | `win32` |
| `windows-11-arm` | — | `win_arm64` | `win_arm64` |

> **Note**: macOS `_PYTHON_HOST_PLATFORM` uses dashes (`macosx-10.9-x86_64`). The `wheel` library's `macosx_libfile.py` splits this value on `-` to extract the OS version and architecture; underscores cause a `ValueError`.

**GitHub Release asset naming**: Wheels follow the standard filename pattern set by `bdist_wheel`:
```
openfga_cli_py-0.7.19.0-py2.py3-none-manylinux_2_17_x86_64.whl
openfga_cli_py-0.7.19.0-py2.py3-none-manylinux_2_17_aarch64.whl
openfga_cli_py-0.7.19.0-py2.py3-none-macosx_10_9_x86_64.whl
openfga_cli_py-0.7.19.0-py2.py3-none-macosx_11_0_arm64.whl
openfga_cli_py-0.7.19.0-py2.py3-none-win_amd64.whl
openfga_cli_py-0.7.19.0-py2.py3-none-win32.whl
openfga_cli_py-0.7.19.0-py2.py3-none-win_arm64.whl
```

#### Pre-commit hooks (`.pre-commit-hooks.yaml`)

```yaml
- id: fga
  name: fga
  language: python
  entry: fga
  types: [file]
  # Install from PyPI: rev pinned to the wrapper package version (e.g., v0.7.19.0)
  # Or install directly from the GitHub Release wheel asset if offline use is needed
```

### 4.7 `Makefile`

```makefile
.PHONY: install quality

install:
	pip install setuptools wheel setuptools-download
	pip install . --no-build-isolation

quality: install
	fga version
	fga help
	pip install --quiet pytest
	pytest tests/
	pip wheel --no-deps --no-build-isolation --wheel-dir dist .
```

### 4.8 `README.md` Content Outline

```markdown
# openfga-cli-py

A Python wrapper to provide a pip-installable [OpenFGA CLI (`fga`)](https://github.com/openfga/cli) binary.

## Installation

    pip install openfga-cli-py

Or install a platform wheel directly from a GitHub Release (for air-gapped/offline use):

    pip install https://github.com/<owner>/openfga-cli-py/releases/download/v0.7.19.0/openfga_cli_py-0.7.19.0-py2.py3-none-linux_x86_64.whl

## Usage

After installation, the `fga` binary is available in your environment:

    fga version
    fga store list

## As a pre-commit hook

Add to your `.pre-commit-config.yaml`:

    - repo: https://github.com/<owner>/openfga-cli-py
      rev: v0.7.19.0
      hooks:
      - id: fga
        args: [model, validate, --file, openfga.json]

The hook invokes `fga` directly. Pass any `fga` subcommands and flags via `args`.
```

---

## 5. Acceptance Criteria

- **AC-001**: Given a Linux x86_64 environment, when `pip install openfga-cli-py` is run, then the `fga` binary is available in `PATH` and `fga version` outputs a version string starting with `v0.7.19`.
- **AC-002**: Given a macOS arm64 environment, when `pip install openfga-cli-py` is run, then `fga version` exits with code `0`.
- **AC-003**: Given a Windows AMD64 environment, when `pip install openfga-cli-py` is run, then `fga.exe` is available in the `Scripts/` directory and `fga version` succeeds.
- **AC-004**: Given any supported platform, when the downloaded archive SHA-256 does not match the value in `setup.cfg`, then installation MUST fail with a checksum error.
- **AC-005**: Given `./update_version.sh 0.7.20` is run, when v0.7.20 exists on GitHub releases, then `setup.cfg` is updated with the new version `0.7.20.0` and correct SHA-256 hashes for all 8 platforms.
- **AC-006**: Given `./update_version.sh` is run without arguments, then the script exits with code `1` and prints usage instructions.
- **AC-007**: Given a git tag `v0.7.19.0` is pushed, when the GitHub Actions `main.yml` workflow completes, then 7 platform-tagged wheels (manylinux x86_64, manylinux aarch64, macosx x86_64, macosx arm64, win_amd64, win32, win_arm64) are published to PyPI under the `oss-robin` account.
- **AC-008**: Given the package is installed, when `python -c "import subprocess; subprocess.run(['fga', 'version'], check=True)"` is executed, then it succeeds without error.
- **AC-009**: Given a git tag `v0.7.19.0` is pushed, when the `publish-github-release` job completes, then the GitHub Release for that tag contains 7 `.whl` assets (one per platform: manylinux_2_17_x86_64, manylinux_2_17_aarch64, macosx_10_9_x86_64, macosx_11_0_arm64, win_amd64, win32, win_arm64) downloadable via the GitHub Releases API.
- **AC-010**: Given a `.pre-commit-config.yaml` referencing `repo: https://github.com/<owner>/openfga-cli-py` at `rev: v0.7.19.0` with `id: fga`, when `pre-commit install && pre-commit run fga --all-files` is executed, then the hook runs `fga` successfully and exits with code `0`.
- **AC-011**: Given a `.pre-commit-config.yaml` with the `fga` hook and `args: [model, validate, --file, openfga.json]`, when the hook runs against a valid `openfga.json` model file, then it exits with code `0`; when run against an invalid model file, it exits with a non-zero code.
- **AC-012**: Given the GitHub Release for `v0.7.19.0` exists with wheel assets, when a wheel is installed directly with `pip install <wheel-url>`, then `fga version` succeeds without downloading from PyPI.
- **AC-013**: Given a Linux aarch64 environment, when `pip install openfga-cli-py` is run, then the `fga` binary for ARM64 is available in `PATH` and `fga version` succeeds.
- **AC-014**: Given a Windows x86 environment (32-bit Python), when `pip install openfga-cli-py` is run, then the 32-bit `fga.exe` is available in the `Scripts/` directory and `fga version` succeeds.
- **AC-015**: Given a Windows ARM64 environment, when `pip install openfga-cli-py` is run, then the ARM64 `fga.exe` is available in the `Scripts/` directory and `fga version` succeeds.
- **AC-016**: Given `pip wheel --no-deps --no-build-isolation --wheel-dir dist .` is run on an Ubuntu runner WITHOUT `_PYTHON_HOST_PLATFORM` set, then the produced wheel is named `*-linux_x86_64.whl`; PyPI MUST reject this wheel with HTTP 400. With `_PYTHON_HOST_PLATFORM=manylinux_2_17_x86_64` set, the produced wheel is named `*-manylinux_2_17_x86_64.whl` and PyPI MUST accept it.
- **AC-017**: Given `setup.py` is imported in an environment where both `setuptools.command.bdist_wheel` and `wheel.bdist_wheel` are unavailable, then `cmdclass` is `{}` and a warning or build error is raised — a `py3-none-any.whl` MUST NOT be published to PyPI.

---

## 6. Test Automation Strategy

- **Test Levels**:
  - *Smoke*: `fga version` and `fga help` run successfully post-install.
  - *Integration*: Full install on each platform via GitHub Actions matrix.
- **Frameworks**: `make` (quality target), `pip` (installation), `pytest` (tests), native shell for binary invocation.
- **Test Data Management**: No external test data required; tests rely solely on the installed binary.
- **CI/CD Integration**: GitHub Actions `main.yml` runs on every push/PR; on tag push it runs three jobs: build-and-test (7-platform matrix: manylinux x86_64, manylinux aarch64, macOS Intel, macOS arm64, Windows amd64, Windows x86, Windows arm64) → publish-pypi (parallel with) publish-github-release.
- **Coverage Requirements**: N/A — the package wraps a pre-built binary with no Python logic to measure.
- **Performance Testing**: Not required; binary download time is acceptable at install time only.

---

## 7. Rationale & Context

The `shellcheck-py` pattern solves the problem of distributing platform-specific CLI tools via pip. The `setuptools-download` plugin allows `setup.cfg` to declaratively specify per-platform binary downloads with integrity verification, producing native platform wheels that are self-contained after installation.

OpenFGA (`fga`) is a fine-grained authorization system CLI tool. Wrapping it in a Python package enables:
- Easy integration into Python-based CI/CD pipelines.
- Use as a pre-commit hook.
- Version-pinned installation via `requirements.txt` or `pyproject.toml`.

The version scheme `<upstream-version>.<packaging-revision>` (e.g., `0.7.19.0`) allows re-releasing the wrapper without changing the upstream tool version (e.g., packaging bug fixes become `0.7.19.1`).

---

## 8. Dependencies & External Integrations

### External Systems
- **EXT-001**: `https://github.com/openfga/cli` — Source of pre-built `fga` binaries, checksums, and release metadata.

### Third-Party Services
- **SVC-001**: PyPI (`https://pypi.org`) — Package registry for publishing and distribution. Account: `oss-robin`.
- **SVC-002**: GitHub Actions — CI/CD runtime for building wheels and publishing to PyPI.

### Infrastructure Dependencies
- **INF-001**: PyPI API token (`PYPI_API_TOKEN`) — A project-scoped PyPI API token for the `openfga-cli-py` project under the `oss-robin` account, stored as a GitHub Actions repository secret. Used by `pypa/gh-action-pypi-publish@release/v1`.
- **INF-002**: GitHub Release API (`GITHUB_TOKEN`) — For uploading `.whl` assets to the GitHub Release associated with the version tag. No additional secrets required; the default `GITHUB_TOKEN` with `contents: write` permission is sufficient.

### Data Dependencies
- **DAT-001**: `checksums.txt` at each OpenFGA CLI release — SHA-256 hashes for all release assets; fetched by `update_version.sh`.

### Technology Platform Dependencies
- **PLT-001**: Python >= 3.10 — Minimum runtime version.
- **PLT-002**: `setuptools-download` — Required `setup_requires` plugin enabling binary download at install time.
- **PLT-003**: `wheel` package — Required for building platform-tagged `.whl` distributions.

### Compliance Dependencies
- **COM-001**: Apache License Version 2.0 License — The wrapper package must be Apache License Version 2.0-licensed, consistent with the OpenFGA CLI license.

---

## 9. Examples & Edge Cases

### Example: Installing on Linux x86_64

```bash
pip install openfga-cli-py
fga version
# Expected output: v0.7.19
```

### Example: Running `update_version.sh`

```bash
chmod +x update_version.sh
./update_version.sh 0.7.20
# Output:
# Downloading checksums for v0.7.20...
# Updated setup.cfg with version 0.7.20.0
# SHA-256 hashes updated for 8 platforms.
```

### Edge Case: Unsupported Platform

If `setuptools-download` finds no matching marker for the current platform, the install should fail with a clear error message rather than silently installing without the binary. Document this limitation in `README.md`.

### Edge Case: Network Unavailable at Install Time

`setuptools-download` will raise an exception if the download URL is unreachable. Users in air-gapped environments should use the pre-built wheel for their specific platform (downloaded from PyPI separately).

### Edge Case: Version String in `update_version.sh`

```bash
./update_version.sh 0.7.20
# Version must match ^[0-9]+\.[0-9]+\.[0-9]+$ — no 'v' prefix accepted.
# The script prepends 'v' when constructing the GitHub release URL.
```

### `update_version.sh` Full Implementation Reference

```bash
#!/usr/bin/env bash
set -euo pipefail

# Usage: ./update_version.sh <VERSION>
# Example: ./update_version.sh 0.7.20

VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
    echo "Usage: $0 <VERSION>" >&2
    echo "Example: $0 0.7.20" >&2
    exit 1
fi

if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: VERSION must be in format X.Y.Z (e.g., 0.7.20)" >&2
    exit 1
fi

RELEASE_BASE="https://github.com/openfga/cli/releases/download/v${VERSION}"
CHECKSUMS_URL="${RELEASE_BASE}/checksums.txt"

echo "Downloading checksums from ${CHECKSUMS_URL}..."
CHECKSUMS=$(curl -fsSL "${CHECKSUMS_URL}")

get_sha() {
    echo "$CHECKSUMS" | grep "$1" | awk '{print $1}'
}

SHA_LINUX_AMD64=$(get_sha "fga_${VERSION}_linux_amd64.tar.gz")
SHA_LINUX_ARM64=$(get_sha "fga_${VERSION}_linux_arm64.tar.gz")
SHA_LINUX_386=$(get_sha "fga_${VERSION}_linux_386.tar.gz")
SHA_DARWIN_AMD64=$(get_sha "fga_${VERSION}_darwin_amd64.tar.gz")
SHA_DARWIN_ARM64=$(get_sha "fga_${VERSION}_darwin_arm64.tar.gz")
SHA_WINDOWS_AMD64=$(get_sha "fga_${VERSION}_windows_amd64.tar.gz")
SHA_WINDOWS_ARM64=$(get_sha "fga_${VERSION}_windows_arm64.tar.gz")
SHA_WINDOWS_386=$(get_sha "fga_${VERSION}_windows_386.tar.gz")

# Validate all checksums were found
for var in SHA_LINUX_AMD64 SHA_LINUX_ARM64 SHA_LINUX_386 \
           SHA_DARWIN_AMD64 SHA_DARWIN_ARM64 \
           SHA_WINDOWS_AMD64 SHA_WINDOWS_ARM64 SHA_WINDOWS_386; do
    if [[ -z "${!var}" ]]; then
        echo "Error: Could not find checksum for ${var}" >&2
        exit 1
    fi
done

# Generate setup.cfg
cat > setup.cfg << EOF
[metadata]
name = openfga-cli-py
version = ${VERSION}.0
description = Python wrapper around invoking the OpenFGA CLI (https://github.com/openfga/cli)
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/neeve-ai/openfga-cli-py
author = oss-robin
license = Apache License Version 2.0
license_files = LICENSE
classifiers =
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3 :: Only
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy

[options]
python_requires = >=3.10
setup_requires =
    setuptools-download

[setuptools_download]
download_scripts =
    [fga]
    group = fga-binary
    marker = sys_platform == "linux" and platform_machine == "x86_64"
    url = ${RELEASE_BASE}/fga_${VERSION}_linux_amd64.tar.gz
    sha256 = ${SHA_LINUX_AMD64}
    extract = tar
    extract_path = fga
    [fga]
    group = fga-binary
    marker = sys_platform == "linux" and platform_machine == "aarch64"
    url = ${RELEASE_BASE}/fga_${VERSION}_linux_arm64.tar.gz
    sha256 = ${SHA_LINUX_ARM64}
    extract = tar
    extract_path = fga
    [fga]
    group = fga-binary
    marker = sys_platform == "linux" and platform_machine == "i686"
    url = ${RELEASE_BASE}/fga_${VERSION}_linux_386.tar.gz
    sha256 = ${SHA_LINUX_386}
    extract = tar
    extract_path = fga
    [fga]
    group = fga-binary
    marker = sys_platform == "darwin" and platform_machine == "x86_64"
    url = ${RELEASE_BASE}/fga_${VERSION}_darwin_amd64.tar.gz
    sha256 = ${SHA_DARWIN_AMD64}
    extract = tar
    extract_path = fga
    [fga]
    group = fga-binary
    marker = sys_platform == "darwin" and platform_machine == "arm64"
    url = ${RELEASE_BASE}/fga_${VERSION}_darwin_arm64.tar.gz
    sha256 = ${SHA_DARWIN_ARM64}
    extract = tar
    extract_path = fga
    [fga.exe]
    group = fga-binary
    marker = sys_platform == "win32" and platform_machine == "AMD64"
    marker = sys_platform == "cygwin" and platform_machine == "x86_64"
    url = ${RELEASE_BASE}/fga_${VERSION}_windows_amd64.tar.gz
    sha256 = ${SHA_WINDOWS_AMD64}
    extract = tar
    extract_path = fga.exe
    [fga.exe]
    group = fga-binary
    marker = sys_platform == "win32" and platform_machine == "ARM64"
    url = ${RELEASE_BASE}/fga_${VERSION}_windows_arm64.tar.gz
    sha256 = ${SHA_WINDOWS_ARM64}
    extract = tar
    extract_path = fga.exe
    [fga.exe]
    group = fga-binary
    marker = sys_platform == "win32" and platform_machine == "x86"
    url = ${RELEASE_BASE}/fga_${VERSION}_windows_386.tar.gz
    sha256 = ${SHA_WINDOWS_386}
    extract = tar
    extract_path = fga.exe
EOF

echo "setup.cfg updated to version ${VERSION}.0"
echo "Updated SHA-256 hashes for 8 platforms."
```

---

## 10. Validation Criteria

1. `pip install openfga-cli-py` completes without errors on each of the 8 supported platform/arch combinations.
2. `fga version` exits with code `0` and prints a version string containing `0.7.19` after installation.
3. `fga help` exits with code `0`.
4. SHA-256 mismatch during install causes a non-zero exit code and an error message referencing checksum failure.
5. `./update_version.sh 0.7.20` produces a `setup.cfg` with `version = 0.7.20.0` and all 8 SHA-256 values matching the official `checksums.txt` for v0.7.20.
6. `./update_version.sh` (no args) exits with code `1`.
7. `./update_version.sh invalid-ver` exits with code `1`.
8. The GitHub Actions workflow successfully publishes to PyPI on tag push (verified by `pip install openfga-cli-py==0.7.19.0` resolving). PyPI upload MUST NOT receive any HTTP 400 error (which would indicate an unsupported platform tag such as bare `linux_x86_64`).
9. The produced wheel filenames follow the pattern `openfga_cli_py-0.7.19.0-py2.py3-none-<platform_tag>.whl` for each of the 7 supported platform tags: `manylinux_2_17_x86_64`, `manylinux_2_17_aarch64`, `macosx_10_9_x86_64`, `macosx_11_0_arm64`, `win_amd64`, `win32`, `win_arm64`. No `py3-none-any.whl` is present in the release.
10. The GitHub Release for tag `v0.7.19.0` contains exactly 7 `.whl` assets (verified via `gh release view v0.7.19.0 --repo <owner>/openfga-cli-py --json assets`).
11. `pip install <github-release-wheel-url>` installs the package and `fga version` succeeds without contacting PyPI.
12. `pre-commit run fga --all-files` succeeds in a repository that has `.pre-commit-config.yaml` referencing this package at `rev: v0.7.19.0`.
13. A `py3-none-any.whl` wheel MUST NOT appear in the `dist/` directory or GitHub Release assets. Its presence indicates that the `bdist_wheel` custom class was not loaded (import failure) and the build is invalid.

---

## 11. Related Specifications / Further Reading

- [shellcheck-py reference implementation](https://github.com/shellcheck-py/shellcheck-py) — Pattern this project follows exactly.
- [setuptools-download documentation](https://github.com/asottile/setuptools-download) — Plugin used for binary downloads.
- [OpenFGA CLI releases](https://github.com/openfga/cli/releases) — Upstream binary source.
- [OpenFGA CLI v0.7.19 release](https://github.com/openfga/cli/releases/tag/v0.7.19) — Specific version this spec targets.
- [pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish) — GitHub Action used to publish wheels to PyPI via API token (`@release/v1`).
- [PEP 508 — Environment Markers](https://peps.python.org/pep-0508/) — Syntax for `marker =` entries in `setup.cfg`.
- [PyPI user oss-robin](https://pypi.org/user/oss-robin/) — Target PyPI account for publishing.
