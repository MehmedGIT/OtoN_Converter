#!/bin/bash

SCRIPT_NAME=$(basename $0)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

METS_ID="PPN631277528.mets.xml"
METS_LINK="https://content.staatsbibliothek-berlin.de/dc/$METS_ID"
WS_PATH="$SCRIPT_DIR/ocrd-workspace"
METS_PATH="$WS_PATH/mets.xml"
FILE_GROUP="DEFAULT"

rm -rf $WS_PATH
mkdir $WS_PATH
wget $METS_LINK -P $WS_PATH
mv $WS_PATH/*mets.xml $WS_PATH/mets.xml

# ocrd software must be available, 
# otherwise the following lines will not execute
cd $WS_PATH
ocrd workspace find --file-grp $FILE_GROUP --download

chmod 777 $WS_PATH

