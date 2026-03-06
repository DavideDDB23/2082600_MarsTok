#!/usr/bin/env bash
# =============================================================================
# load-image.sh — Load the Mars IoT Simulator OCI image into Docker daemon
# =============================================================================
# Run this script ONCE before `docker compose up --build`.
# It finds the OCI image directory relative to this script's location,
# then uses skopeo (installed automatically via Homebrew if missing) to copy
# the multi-arch OCI layout into the local Docker daemon.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OCI_DIR="$(cd "${SCRIPT_DIR}/../March 2026/mars-iot-simulator-oci" && pwd)"
IMAGE_TAG="mars-iot-simulator:multiarch_v1"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Mars IoT Simulator — OCI Image Loader"
echo "  OCI source : ${OCI_DIR}"
echo "  Target tag : ${IMAGE_TAG}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── 1. Check Docker daemon ────────────────────────────────────────────────────
if ! docker info > /dev/null 2>&1; then
  echo "✗  Docker daemon is not running."
  echo "   Start Docker Desktop (or run 'dockerd') and try again."
  exit 1
fi
echo "✓  Docker daemon is running."

# ── 2. Check if image already loaded ─────────────────────────────────────────
if docker image inspect "${IMAGE_TAG}" > /dev/null 2>&1; then
  echo "✓  Image '${IMAGE_TAG}' already present. Nothing to do."
  exit 0
fi

# ── 3. Ensure skopeo is available ─────────────────────────────────────────────
if ! command -v skopeo > /dev/null 2>&1; then
  if command -v brew > /dev/null 2>&1; then
    echo "▶  skopeo not found — installing via Homebrew ..."
    brew install skopeo
  else
    echo "✗  skopeo not found and Homebrew is not available."
    echo "   Install skopeo manually: https://github.com/containers/skopeo"
    echo "   On macOS: brew install skopeo"
    exit 1
  fi
fi
echo "✓  skopeo is available: $(skopeo --version)"

# ── 4. Copy OCI → tar archive → Docker daemon ────────────────────────────────
# Using a tar intermediate is more reliable across Docker runtimes (Colima, etc.)
TMP_TAR="$(mktemp /tmp/mars-iot-simulator-XXXXXX.tar)"
echo "▶  Converting OCI image to tar archive: ${TMP_TAR}"
skopeo copy \
  --override-os linux \
  "oci:${OCI_DIR}" \
  "docker-archive:${TMP_TAR}:${IMAGE_TAG}"

echo "▶  Loading tar archive into Docker daemon ..."
docker load -i "${TMP_TAR}"
rm -f "${TMP_TAR}"

echo ""
echo "✓  Image '${IMAGE_TAG}' successfully loaded into Docker daemon."
echo "   You can now run: docker compose up --build"
