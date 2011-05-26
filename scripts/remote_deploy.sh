#!/bin/bash

set -e -x

PROJECT_DIR=/vol/project/2010/271/g1027114
ENTRY_SERVER=shell1.doc.ic.ac.uk
USERNAME=$1

if [ -z $USERNAME ]; then
    echo "USAGE: $0 <username>"
    exit 1
fi

scp scripts/deploy.sh $USERNAME@$ENTRY_SERVER:$PROJECT_DIR
ssh $USERNAME@$ENTRY_SERVER "$PROJECT_DIR/deploy.sh"
