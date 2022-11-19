#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

rm -rf $SCRIPT_DIR/ocrd-workspace
rm -rf $SCRIPT_DIR/work
rm -rf $SCRIPT_DIR/.nextflow
rm -f $SCRIPT_DIR/.nextflow.log*
