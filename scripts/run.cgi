#!/usr/bin/env python

import wsgiref.handlers
import os, sys

# Run this instead of the booksexchange application to test WSGI via CGI
def tester(env, start_response):
	start_response('200 OK', [('Content-Type', 'text/plain')])
	return ["\n".join([sys.version] + sys.path)]

if __name__ == "__main__":
	# Some common variables
	cwd = os.getcwd()

	# Activate virtualenv
	activater = os.path.join(cwd, "bxchg/bin/activate_this.py")
	execfile(activater, dict(__file__=activater))

        # Set up *bookexchange* paths
	sys.path.append(os.path.join(cwd, 'booksexchange'))
	path_to_config = os.path.join(cwd, 'booksexchange/development.ini')

        # WSGI appears to break down if this is missing
	os.environ['SERVER_NAME'] = "www.doc.ic.ac.uk"
	os.environ['SERVER_PORT'] = "80"
        os.environ['PYTHON_EGG_CACHE'] = "/tmp"

        # Load booksexchange application
	from paste.deploy import loadapp
	app = loadapp('config:' + path_to_config, relative_to = cwd) 

        # And run it
	wsgiref.handlers.CGIHandler().run(app)

