#!/bin/bash

set -e -x

PROJECT_DIR=/vol/project/2010/271/g1027114
USERNAME=$1

if [ -z $USERNAME ]; then
    echo "USAGE: $0 <username>"
    exit 1
fi

ENTRY_SERVER=$2

if [ -z $ENTRY_SERVER ]; then
    ENTRY_SERVER=shell1.doc.ic.ac.uk
fi

echo -e "* \033[38;5;148mRemote deploy\033[39m"
scp scripts/deploy.sh $USERNAME@$ENTRY_SERVER:$PROJECT_DIR
ssh $USERNAME@$ENTRY_SERVER "$PROJECT_DIR/deploy.sh && rm $PROJECT_DIR/deploy.sh"

echo -e "* \033[38;5;148mFinished remote deployment\033[39m"
