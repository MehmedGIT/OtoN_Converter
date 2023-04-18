#!/usr/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

NEXTFLOW_SCRIPT="$SCRIPT_DIR/tests/execution_tests/dummy_ws_docker_test/nextflow1_dockerized.nf"
WORKSPACE_PATH="$SCRIPT_DIR/tests/execution_tests/dummy_ws_docker_test/data"
METS_PATH="$WORKSPACE_PATH/mets.xml"

# NOTE: The required models are already downloaded/prepared:
# docker run --rm -v "/home/mm/ocrd_models/:/usr/local/share/" -- ocrd/all:maximum ocrd resmgr download '*'
# docker run --rm -v "/home/mm/ocrd_models/:/usr/local/share/" -- ocrd/all:maximum ocrd resmgr download ocrd-tesserocr-recognize '*'

nextflow run "$NEXTFLOW_SCRIPT" \
-ansi-log false \
-with-report \
--workspace_path "$WORKSPACE_PATH" \
--mets_path "$METS_PATH" \
--docker_pwd "$WORKSPACE_PATH" \
--docker_image "ocrd/all:maximum" \
--docker_models_dir "/usr/local/share" \
--models_path "/home/mm/ocrd_models" \
