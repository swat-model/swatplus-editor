from flask import Blueprint, request, abort
from playhouse.shortcuts import model_to_dict
from .defaults import DefaultRestMethods
from .config import RequestHeaders as rh
from database.project.basin import Parameters_bsn, Codes_bsn, Carbon_bsn, Carbon_lyr_bsn

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

@bp.route('/has-carbon', methods=['GET', 'PUT'])
def hasCarbon():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	if request.method == 'GET':
		has_carbon = False
		code_bsn = Codes_bsn.get()
		has_carbon = code_bsn.carbon == 2 and Carbon_bsn.get_or_none() is not None

		return {'has_carbon': has_carbon}
	elif request.method == 'PUT':
		code_bsn = Codes_bsn.get()
		code_bsn.carbon = 2
		code_bsn.save()

		if Carbon_bsn.get_or_none() is None:
			m = Carbon_bsn()
			m.save()
		if Carbon_lyr_bsn.get_or_none(layer=1) is None:
			Carbon_lyr_bsn.create_layer1()
		if Carbon_lyr_bsn.get_or_none(layer=2) is None:
			m = Carbon_lyr_bsn(layer=2, 
              hp_rate=1.2e-5, 
              hs_rate=1.81e-4, 
              microb_rate=0.02,
              meta_rate=0.0507,
              str_rate=0.0134,
              microb_top_rate=0.02,
              a1co2=0.55)
			m.save()
		return '', 200
	abort(405, 'HTTP Method not allowed.')	

@bp.route('/carbon', methods=['GET', 'PUT', 'DELETE'])
def carbon():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	if request.method == 'GET':
		if Carbon_bsn.get_or_none() is None:
			m = Carbon_bsn()
			return model_to_dict(m, recurse=False)
		else:
			return DefaultRestMethods.get(1, Carbon_bsn, 'Basin carbon')
	elif request.method == 'DELETE':
		code_bsn = Codes_bsn.get()
		code_bsn.carbon = 0
		code_bsn.save()
		return '', 204
	elif request.method == 'PUT':
		if Carbon_bsn.get_or_none() is None:
			return DefaultRestMethods.post(Carbon_bsn, 'Basin carbon')
		else:
			return DefaultRestMethods.put(1, Carbon_bsn, 'Basin carbon')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/carbon/lyrs', methods=['GET', 'POST'])
def carbon_lyrs():
	if request.method == 'GET':
		table = Carbon_lyr_bsn
		filter_cols = [table.layer]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(Carbon_lyr_bsn, 'Carbon layers')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/carbon/lyrs/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def carbon_lyrsId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Carbon_lyr_bsn, 'Carbon layers')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Carbon_lyr_bsn, 'Carbon layers')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, Carbon_lyr_bsn, 'Carbon layers')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/carbon/lyrs/many', methods=['GET', 'PUT'])
def carbon_lyrsMany():
	if request.method == 'GET':
		table = Carbon_lyr_bsn
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		m = table.select(table.id, table.layer).order_by(table.layer)
		rh.close()
		return [{'id': v.id, 'name': v.layer} for v in m]
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(Carbon_lyr_bsn, 'Carbon layers')
	
	abort(405, 'HTTP Method not allowed.')
