#!/usr/bin/env python

import os

print 'Content-type: text/plain'
print
print 'Hello World!'

cwd = os.getcwd()
print 'CWD:', cwd

home = os.path.expanduser('~')
print 'HOME:', home

