#!/usr/bin/env bash
# ReflexionOS — Quick start
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$SCRIPT_DIR/backend"

echo ""
echo "  ⚔  ReflexionOS"
echo "  Adversarial Document Intelligence"
echo ""

# Provider
PROVIDER="${REFLEXION_PROVIDER:-mock}"
echo "  Provider : $PROVIDER"
if [ "$PROVIDER" = "bedrock" ]; then
  echo "  Region   : ${AWS_DEFAULT_REGION:-us-east-1}"
fi

echo "  URL      : http://localhost:${PORT:-8000}"
echo ""

cd "$BACKEND"
exec uvicorn app:app --host 0.0.0.0 --port "${PORT:-8000}" --reload
