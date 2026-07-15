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
