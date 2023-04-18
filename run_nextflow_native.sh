#!/usr/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

NEXTFLOW_SCRIPT="$SCRIPT_DIR/tests/execution_tests/dummy_ws_native_test/nextflow1.nf"
METS_PATH="$SCRIPT_DIR/tests/execution_tests/dummy_ws_native_test/data/mets.xml"

nextflow run "$NEXTFLOW_SCRIPT" \
-ansi-log false \
-with-report \
--mets_path "$METS_PATH"
