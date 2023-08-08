from flask import Flask, jsonify
from helpers.executable_api import Unbuffered
import sys
import argparse
import platform
import os

from rest import setup

app = Flask(__name__)
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

if __name__ == '__main__':
	sys.stdout = Unbuffered(sys.stdout)
	parser = argparse.ArgumentParser(description='SWAT+ Editor REST API')
	parser.add_argument('port', type=str, help='port number to run API', default=5000, nargs='?')
	args = parser.parse_args()
	app.run(port=int(args.port))
