#!/bin/bash

set -e -x

PROJECT_DIR=/vol/project/2010/271/g1027114

echo -e "* \033[38;5;148mClean old deployment\033[39m"
cd $PROJECT_DIR
rm -rf booksexchange

echo -e "* \033[38;5;148mDeploy Pyramid\033[39m"
git clone booksexchange.git
chmod g+w booksexchange

echo -e "* \033[38;5;148mDeploy CGI runners\033[39m"
cp booksexchange/scripts/*cgi .
