# openfga-cli-py

A Python wrapper to provide a pip-installable [OpenFGA CLI (`fga`)](https://github.com/openfga/cli) binary.

[![CI](https://github.com/neeve-ai/openfga-cli-py/actions/workflows/main.yml/badge.svg)](https://github.com/neeve-ai/openfga-cli-py/actions/workflows/main.yml)
[![PyPI](https://img.shields.io/pypi/v/openfga-cli-py)](https://pypi.org/project/openfga-cli-py/)

## Installation

```bash
pip install openfga-cli-py
```

Or install a platform wheel directly from a GitHub Release (for air-gapped/offline use):

```bash
pip install https://github.com/neeve-ai/openfga-cli-py/releases/download/v0.7.19.0/openfga_cli_py-0.7.19.0-py2.py3-none-linux_x86_64.whl
```

## Usage

After installation, the `fga` binary is available in your environment:

```bash
fga version
fga store list
```

Or invoke it from Python:

```python
import subprocess
subprocess.run(["fga", "version"], check=True)
```

## Supported Platforms

| Platform | Architecture |
|----------|-------------|
| Linux    | x86_64, arm64, i686 |
| macOS    | x86_64 (Intel), arm64 (Apple Silicon) |
| Windows  | AMD64, ARM64, x86 |

> **Note**: If your platform is not listed above, installation will fail with an error from
> `setuptools-download`. Use a supported platform or build from source.

> **Note**: In air-gapped environments, download the pre-built wheel for your platform from
> the [GitHub Releases page](https://github.com/neeve-ai/openfga-cli-py/releases) and install
> it directly with `pip install <wheel-file>`.

## As a pre-commit hook

Add to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/neeve-ai/openfga-cli-py
  rev: v0.7.19.0
  hooks:
    - id: fga
      args: [model, validate, --file, openfga.json]
      pass_filenames: false
      always_run: true
```

The hook invokes `fga` directly. Pass any `fga` subcommands and flags via `args`.

## Updating to a new OpenFGA CLI version

Use the provided script to regenerate `setup.cfg` for a new upstream release:

```bash
chmod +x update_version.sh
./update_version.sh 0.7.20
```

This downloads the official `checksums.txt` for the new version and rewrites `setup.cfg`
with updated URLs and SHA-256 hashes for all 8 platforms.

## Development

```bash
make install   # installs the package and dependencies
make quality   # runs: fga version && fga help, pytest, and builds platform wheel
```

## License

Apache-2.0 — see [LICENSE](LICENSE).
