from flask import Flask, make_response, jsonify
from flask_cors import CORS
from helpers.executable_api import Unbuffered
import sys
import argparse
import platform
import os
import werkzeug
import traceback

from rest import setup, aquifer, auto_complete, basin, channel, climate, decision_table, definitions, hru, hru_lte, hru_parm_db, hydrology, lum, ops, recall, regions, reservoir, routing_unit, structural

app = Flask(__name__)
CORS(app)
app.debug = False
app.json.sort_keys = False
exiting = False

app.register_blueprint(setup.bp)
app.register_blueprint(aquifer.bp)
app.register_blueprint(auto_complete.bp)
app.register_blueprint(basin.bp)
app.register_blueprint(channel.bp)
app.register_blueprint(climate.bp)
app.register_blueprint(decision_table.bp)
app.register_blueprint(definitions.bp)
app.register_blueprint(hru.bp)
app.register_blueprint(hru_lte.bp)
app.register_blueprint(hru_parm_db.bp)
app.register_blueprint(hydrology.bp)
app.register_blueprint(lum.bp)
app.register_blueprint(ops.bp)
app.register_blueprint(recall.bp)
app.register_blueprint(regions.bp)
app.register_blueprint(reservoir.bp)
app.register_blueprint(routing_unit.bp)
app.register_blueprint(structural.bp)

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
    return make_response(jsonify(message=e.description, stacktrace=traceback.format_exc()), e.code)


if __name__ == '__main__':
	sys.stdout = Unbuffered(sys.stdout)
	parser = argparse.ArgumentParser(description='SWAT+ Editor REST API')
	parser.add_argument('port', type=str, help='port number to run API', default=5000, nargs='?')
	args = parser.parse_args()
	app.run(port=int(args.port), debug=True, use_reloader=False)
