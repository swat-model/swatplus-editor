from flask import Blueprint, request, abort
from playhouse.shortcuts import model_to_dict

from .defaults import DefaultRestMethods, RestHelpers
from .config import RequestHeaders as rh
from database.project import gwflow, config
from database import lib

bp = Blueprint('gwflow', __name__, url_prefix='/gwflow')

@bp.route('/enabled', methods=['GET'])
def enabled():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	pc = config.Project_config.get()

	can_enable = False
	conn = lib.open_db(project_db)
	if lib.exists_table(conn, 'gwflow_base'):
		can_enable = True
	rh.close()
	return {
		'use_gwflow': pc.use_gwflow == 1,
		'can_enable': can_enable
	}		

@bp.route('/base', methods=['GET', 'PUT'])
def base():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	table = gwflow.Gwflow_base
	item_description = 'Groundwater flow initialization'
	m = table.get_or_none()
	pc = config.Project_config.get()

	if request.method == 'GET':
		if m is None:
			rh.close()
			abort(400, '{} does not exist'.format(item_description))

		d = model_to_dict(m, recurse=False)

		rh.close()
		return {
			'use_gwflow': pc.use_gwflow == 1,
			'base': d,
		}
	elif request.method == 'PUT':
		try:
			result = RestHelpers.save_args(table, request.json['base'], id=0)

			pc.use_gwflow = request.json['use_gwflow']
			pc.save()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update {item}.'.format(item=item_description.lower()))
		except table.DoesNotExist:
			rh.close()
			abort(404, '{item} does not exist'.format(item=item_description))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')
