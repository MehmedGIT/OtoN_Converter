#!/usr/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

rm -rf "$SCRIPT_DIR"/tests/execution_tests
rm -rf "$SCRIPT_DIR"/work
rm -rf "$SCRIPT_DIR"/.nextflow
rm "$SCRIPT_DIR"/.nextflow.*
rm "$SCRIPT_DIR"/*.html
