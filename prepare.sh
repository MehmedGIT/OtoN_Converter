#!/usr/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

EXEC_TESTS="$SCRIPT_DIR/tests/execution_tests"
rm -rf "$EXEC_TESTS"
mkdir -p "$EXEC_TESTS"

EXEC_DIR1="$EXEC_TESTS/dummy_ws_native_test"
EXEC_DIR2="$EXEC_TESTS/dummy_ws_docker_test"
mkdir -p "$EXEC_DIR1"
mkdir -p "$EXEC_DIR2"

DUMMY_WORKSPACE="$SCRIPT_DIR/oton/assets/dummy_ws/data/"
NEXTFLOW_SCRIPT1="$SCRIPT_DIR/oton/assets/nextflow1.nf"
NEXTFLOW_SCRIPT2="$SCRIPT_DIR/oton/assets/nextflow1_dockerized.nf"

cp -rf "$DUMMY_WORKSPACE" "$EXEC_DIR1/data"
cp -rf "$DUMMY_WORKSPACE" "$EXEC_DIR2/data"
cp "$NEXTFLOW_SCRIPT1" "$EXEC_DIR1"
cp "$NEXTFLOW_SCRIPT2" "$EXEC_DIR2"

chmod -R 755 "$EXEC_TESTS"
