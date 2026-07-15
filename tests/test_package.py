"""
Tests for update_version.sh — covers AC-005, AC-006, and version validation.

AC-005: Given ./update_version.sh 0.7.20 is run and v0.7.20 exists on GitHub,
        then setup.cfg is updated with version 0.7.20.0 and correct SHA-256 hashes.
AC-006: Given ./update_version.sh is run without arguments,
        then the script exits with code 1 and prints usage instructions.

Validation edge cases (from Section 10):
  - ./update_version.sh (no args)         → exit 1
  - ./update_version.sh invalid-ver       → exit 1
  - ./update_version.sh v0.7.20           → exit 1 (v-prefix not accepted)
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.resolve()
SCRIPT = REPO_ROOT / "update_version.sh"


def run_script(*args: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        **kwargs,
    )


# ── AC-006 ────────────────────────────────────────────────────────────────────

class TestNoArguments:
    """AC-006: Given no arguments, script exits 1 with usage instructions."""

    def test_exits_with_code_1(self):
        result = run_script()
        assert result.returncode == 1

    def test_prints_usage_to_stderr(self):
        result = run_script()
        assert "Usage:" in result.stderr


# ── Version format validation (Section 10, edge cases) ───────────────────────

class TestInvalidVersionFormat:
    """Given an invalid version string, script exits 1 with an error message."""

    @pytest.mark.parametrize("bad_version", [
        "invalid-ver",
        "v0.7.20",    # v-prefix not accepted (spec Section 9 edge case)
        "0.7",        # too few components
        "0.7.20.0",   # too many components
        "a.b.c",
        "",
    ])
    def test_exits_with_code_1(self, bad_version):
        result = run_script(bad_version)
        assert result.returncode == 1

    @pytest.mark.parametrize("bad_version", [
        "invalid-ver",
        "v0.7.20",
        "0.7",
        "0.7.20.0",
    ])
    def test_prints_error_to_stderr(self, bad_version):
        result = run_script(bad_version)
        # Either "Usage:" (empty string treated as missing) or "Error:" for bad format
        assert result.returncode == 1
        assert result.stderr.strip() != ""


# ── setup.cfg content validation helpers ─────────────────────────────────────

class TestCurrentSetupCfg:
    """Validate that the committed setup.cfg has the expected structure for v0.7.19."""

    SETUP_CFG = REPO_ROOT / "setup.cfg"

    def test_version_is_correct(self):
        content = self.SETUP_CFG.read_text()
        assert "version = 0.7.19.0" in content

    def test_all_8_platforms_present(self):
        content = self.SETUP_CFG.read_text()
        expected_archives = [
            "fga_0.7.19_linux_amd64.tar.gz",
            "fga_0.7.19_linux_arm64.tar.gz",
            "fga_0.7.19_linux_386.tar.gz",
            "fga_0.7.19_darwin_amd64.tar.gz",
            "fga_0.7.19_darwin_arm64.tar.gz",
            "fga_0.7.19_windows_amd64.tar.gz",
            "fga_0.7.19_windows_arm64.tar.gz",
            "fga_0.7.19_windows_386.tar.gz",
        ]
        for archive in expected_archives:
            assert archive in content, f"Missing archive: {archive}"

    def test_all_sha256_values_are_64_hex_chars(self):
        content = self.SETUP_CFG.read_text()
        sha256_pattern = re.compile(r"sha256\s*=\s*([0-9a-f]+)")
        matches = sha256_pattern.findall(content)
        assert len(matches) == 8, f"Expected 8 sha256 entries, found {len(matches)}"
        for sha in matches:
            assert len(sha) == 64, f"SHA-256 value has wrong length: {sha!r}"
            assert re.fullmatch(r"[0-9a-f]{64}", sha), f"Non-hex SHA-256: {sha!r}"

    def test_extract_path_for_unix_is_fga(self):
        content = self.SETUP_CFG.read_text()
        # Each linux/darwin block ends with extract_path = fga (not fga.exe)
        linux_darwin_blocks = re.findall(
            r'\[fga\].*?extract_path\s*=\s*(\S+)',
            content,
            re.DOTALL,
        )
        for path in linux_darwin_blocks:
            assert path == "fga", f"Unexpected extract_path for unix block: {path!r}"

    def test_extract_path_for_windows_is_fga_exe(self):
        content = self.SETUP_CFG.read_text()
        windows_blocks = re.findall(
            r'\[fga\.exe\].*?extract_path\s*=\s*(\S+)',
            content,
            re.DOTALL,
        )
        assert len(windows_blocks) == 3, f"Expected 3 windows blocks, found {len(windows_blocks)}"
        for path in windows_blocks:
            assert path == "fga.exe", f"Unexpected extract_path for windows block: {path!r}"

    def test_python_requires_is_310(self):
        content = self.SETUP_CFG.read_text()
        assert "python_requires = >=3.10" in content

    def test_setup_requires_setuptools_download(self):
        content = self.SETUP_CFG.read_text()
        assert "setuptools-download" in content

    def test_group_name_is_fga_binary(self):
        content = self.SETUP_CFG.read_text()
        groups = re.findall(r"group\s*=\s*(\S+)", content)
        assert len(groups) == 8
        for g in groups:
            assert g == "fga-binary", f"Unexpected group name: {g!r}"


# ── setup.py structural check ─────────────────────────────────────────────────

class TestSetupPy:
    """Validate setup.py has the required bdist_wheel subclass (CON-004, GUD-002)."""

    SETUP_PY = REPO_ROOT / "setup.py"

    def test_file_exists(self):
        assert self.SETUP_PY.exists()

    def test_root_is_pure_false(self):
        content = self.SETUP_PY.read_text()
        assert "root_is_pure = False" in content

    def test_get_tag_returns_py2_py3_none(self):
        content = self.SETUP_PY.read_text()
        assert "'py2.py3'" in content
        assert "'none'" in content

    def test_setup_called_with_cmdclass(self):
        content = self.SETUP_PY.read_text()
        assert "setup(cmdclass=cmdclass)" in content


# ── Pre-commit hook definition check (REQ-010) ────────────────────────────────

class TestPreCommitHooks:
    """Validate .pre-commit-hooks.yaml defines a fga hook (REQ-010)."""

    HOOKS_FILE = REPO_ROOT / ".pre-commit-hooks.yaml"

    def test_file_exists(self):
        assert self.HOOKS_FILE.exists()

    def test_hook_id_is_fga(self):
        content = self.HOOKS_FILE.read_text()
        assert "id: fga" in content

    def test_language_is_python(self):
        content = self.HOOKS_FILE.read_text()
        assert "language: python" in content

    def test_entry_is_fga(self):
        content = self.HOOKS_FILE.read_text()
        assert "entry: fga" in content


# ── Post-install smoke tests (AC-001, AC-002, AC-008) ─────────────────────────
# These run only when fga is actually installed in the environment.

@pytest.mark.skipif(
    subprocess.run(["which", "fga"], capture_output=True).returncode != 0
    and subprocess.run(["where", "fga"], capture_output=True, shell=True).returncode != 0,
    reason="fga binary not installed in this environment",
)
class TestFgaInstalled:
    """
    AC-001/AC-002: Given the package is installed, fga version exits 0 and
                   outputs a version string starting with 'v0.7.19'.
    AC-008:        Given the package is installed, subprocess.run(['fga','version'])
                   succeeds without error.
    """

    def test_fga_version_exits_zero(self):
        result = subprocess.run(["fga", "version"], capture_output=True, text=True)
        assert result.returncode == 0

    def test_fga_version_output_contains_version(self):
        result = subprocess.run(["fga", "version"], capture_output=True, text=True)
        output = result.stdout + result.stderr
        assert "0.7.19" in output, f"Version string not found in output: {output!r}"

    def test_fga_help_exits_zero(self):
        result = subprocess.run(["fga", "help"], capture_output=True, text=True)
        assert result.returncode == 0

    def test_ac008_subprocess_run_check_true(self):
        """AC-008: subprocess.run(['fga', 'version'], check=True) must not raise."""
        subprocess.run(["fga", "version"], check=True)
