#!/usr/bin/env bash
set -euo pipefail

# Install the Landslide CLI binary.
#
# Downloads the correct binary for the current OS/architecture and places it
# on PATH. Used by the one-liner on the landing page and internal tooling.
#
# Usage:
#   install.sh [--version <version>] [--base-url <url>] [--install-dir <dir>]

BIN_NAME="landslide"
INSTALL_DIR_DEFAULT="/usr/local/bin"
BASE_URL_DEFAULT="${LANDSLIDE_DOWNLOADS_BASE_URL:-https://downloads.landslide.global}"

usage() {
  cat <<'EOF'
Usage:
  install.sh [--version <version>] [--base-url <url>] [--install-dir <dir>]

Options:
  --version      Release version to install (e.g. 1.0.0). Defaults to "latest".
  --base-url     Base URL hosting /cli releases (default: $LANDSLIDE_DOWNLOADS_BASE_URL or https://downloads.landslide.global)
  --install-dir  Install directory (default: /usr/local/bin)

Environment:
  LANDSLIDE_DOWNLOADS_BASE_URL  Overrides default base URL
EOF
}

VERSION="latest"
BASE_URL="$BASE_URL_DEFAULT"
INSTALL_DIR="$INSTALL_DIR_DEFAULT"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)
      VERSION="${2:-}"; shift 2 ;;
    --base-url)
      BASE_URL="${2:-}"; shift 2 ;;
    --install-dir)
      INSTALL_DIR="${2:-}"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

uname_s="$(uname -s | tr '[:upper:]' '[:lower:]')"
uname_m="$(uname -m)"

case "$uname_s" in
  darwin) os="darwin" ;;
  linux)  os="linux"  ;;
  *)
    echo "Unsupported OS: $uname_s" >&2
    exit 1
    ;;
esac

case "$uname_m" in
  x86_64|amd64) arch="x86_64" ;;
  arm64|aarch64) arch="arm64" ;;
  *)
    echo "Unsupported architecture: $uname_m" >&2
    exit 1
    ;;
esac

asset="${BIN_NAME}-${os}-${arch}"
# Canonical path: cli/releases/{version|latest}/ (ASSET_NAMING_STANDARDS)
url="${BASE_URL%/}/cli/releases/${VERSION}/${asset}"

echo "Installing Landslide CLI ${VERSION} (${os}/${arch})..."
echo "  Source: ${url}"
echo "  Target: ${INSTALL_DIR}/${BIN_NAME}"

if ! mkdir -p "$INSTALL_DIR" 2>/dev/null && [[ ! -w "$INSTALL_DIR" ]]; then
  echo "Cannot write to ${INSTALL_DIR} — re-running with sudo..."
  exec sudo "$0" "$@"
fi

tmp="$(mktemp)"
trap 'rm -f "$tmp" "$tmp.sums"' EXIT

if command -v curl &>/dev/null; then
  curl -fsSL "$url" -o "$tmp"
elif command -v wget &>/dev/null; then
  wget -qO "$tmp" "$url"
else
  echo "Error: curl or wget is required" >&2
  exit 1
fi

# Integrity: verify against SHA256SUMS in the release dir when present.
sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}'
  else echo ""; fi
}
sums_url="${url%/*}/SHA256SUMS"
if { command -v curl >/dev/null 2>&1 && curl -fsSL "$sums_url" -o "$tmp.sums" 2>/dev/null; } || \
   { command -v wget >/dev/null 2>&1 && wget -qO "$tmp.sums" "$sums_url" 2>/dev/null; }; then
  expected="$(awk -v f="$asset" '$2==f || $2=="*"f {print $1; exit}' "$tmp.sums")"
  actual="$(sha256_of "$tmp")"
  rm -f "$tmp.sums"
  if [[ -z "$expected" ]]; then
    echo "ERROR: SHA256SUMS at $sums_url has no entry for $asset; cannot verify this download. Refusing to install." >&2
    exit 4
  fi
  if [[ -z "$actual" ]]; then
    echo "ERROR: no sha256 tool (sha256sum or shasum) available to verify $asset. Refusing to install." >&2
    exit 4
  fi
  if [[ "$actual" != "$expected" ]]; then
    echo "ERROR: checksum mismatch for $asset (expected $expected, got $actual)" >&2
    exit 4
  fi
  echo "Verified: sha256 OK"
else
  echo "ERROR: could not fetch SHA256SUMS at $sums_url; cannot verify this download. Refusing to install." >&2
  exit 4
fi

chmod +x "$tmp"
mv "$tmp" "${INSTALL_DIR}/${BIN_NAME}"

# Verify installation
if ! "${INSTALL_DIR}/${BIN_NAME}" --version &>/dev/null; then
  echo "Warning: installed binary did not respond to --version" >&2
fi

echo "✅ Landslide CLI installed to ${INSTALL_DIR}/${BIN_NAME}"

# Suggest PATH addition if install dir is not on PATH
if ! echo "$PATH" | grep -q "$INSTALL_DIR"; then
  echo ""
  echo "Add ${INSTALL_DIR} to your PATH:"
  echo "  echo 'export PATH=\"\$PATH:${INSTALL_DIR}\"' >> ~/.bashrc"
  echo "  echo 'export PATH=\"\$PATH:${INSTALL_DIR}\"' >> ~/.zshrc"
fi
