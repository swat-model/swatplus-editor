from flask import Blueprint, request, abort
from .defaults import DefaultRestMethods
from database.project.basin import Parameters_bsn, Codes_bsn

bp = Blueprint('basin', __name__, url_prefix='/basin')

@bp.route('/parms', methods=['GET', 'PUT'])
def parms():
	if request.method == 'GET':
		return DefaultRestMethods.get(1, Parameters_bsn, 'Basin parameters')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(1, Parameters_bsn, 'Basin parameters')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/codes', methods=['GET', 'PUT'])
def parameters():
	if request.method == 'GET':
		return DefaultRestMethods.get(1, Codes_bsn, 'Basin codes')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(1, Codes_bsn, 'Basin codes')

	abort(405, 'HTTP Method not allowed.')
