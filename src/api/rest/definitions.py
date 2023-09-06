from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict

from database.vardefs import Var_range, Var_code, SetupVardefsDatabase
import os

vardef_db = 'swatplus_vardefs.sqlite'

bp = Blueprint('definitions', __name__, url_prefix='/definitions')

@bp.route('/vars/<table>/<path:appPath>', methods=['GET'])
def getVars(table, appPath):
	SetupVardefsDatabase.init(os.path.join(appPath, vardef_db))
	m = Var_range.select().where((Var_range.table == table) & (Var_range.disabled == False))
	
	values = {}
	for v in m:
		options = []
		for o in v.options:
			if o.text_only:
				val = None if o.text == 'null' else o.text
				options.append({'value': val, 'text': o.text})
			elif o.text_value is not None:
				val = None if o.text_value == 'null' else o.text_value
				options.append({'value': val, 'text': o.text})
			else:
				val = None if o.value == 'null' else o.value
				options.append({'value': val, 'text': o.text})

		values[v.variable] = {
			'name': v.variable,
			'type': v.type,
			'min_value': v.min_value,
			'max_value': v.max_value,
			'default_value': v.default_value,
			'default_text': v.default_text,
			'units': v.units,
			'description': v.description,
			'options': options 
		}
		
	SetupVardefsDatabase.close()
	return values

@bp.route('/codes/<table>/<variable>/<path:appPath>', methods=['GET'])
def getCodes(table, variable, appPath):
	SetupVardefsDatabase.init(os.path.join(appPath, vardef_db))
	m = Var_code.select().where((Var_code.table == table) & (Var_code.variable == variable))
	
	values = []
	for v in m:
		values.append({
			'value': v.code,
			'text': '{code} - {description}'.format(code=v.code, description=v.description)
		})
	
	SetupVardefsDatabase.close()
	return values