from flask import Flask, make_response, jsonify
from flask_cors import CORS
from helpers.executable_api import Unbuffered
import sys
import argparse
import platform
import os
import werkzeug

from rest import setup

app = Flask(__name__)
CORS(app)
exiting = False

app.register_blueprint(setup.bp)

@app.route('/', methods=['GET'])
def default():
	return jsonify({
		'editor': 'API call working',
		'pythonVersion': platform.python_version()
	})

@app.route('/shutdown', methods=['GET'])
def shutdown():
	global exiting
	exiting = True
	return jsonify({'SWATPlusEditor': 'Server shutting down...'})

@app.teardown_request
def teardown(exception):
	if exiting:
		os._exit(0)

@app.errorhandler(werkzeug.exceptions.HTTPException)
def handle_exception(e):
    return make_response(jsonify(message=e.description), e.code)


if __name__ == '__main__':
	sys.stdout = Unbuffered(sys.stdout)
	parser = argparse.ArgumentParser(description='SWAT+ Editor REST API')
	parser.add_argument('port', type=str, help='port number to run API', default=5000, nargs='?')
	args = parser.parse_args()
	app.run(port=int(args.port))
