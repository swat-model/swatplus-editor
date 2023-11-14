from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project import base as project_base
from database.project.config import Project_config
from database.project.climate import Weather_sta_cli, Weather_file, Weather_wgn_cli, Weather_wgn_cli_mon, Atmo_cli, Atmo_cli_sta, Atmo_cli_sta_value
from database import lib as db_lib
from helpers import utils
import sqlite3

bp = Blueprint('climate', __name__, url_prefix='/climate')

# Weather_sta_cli

@bp.route('/stations', methods=['GET', 'POST', 'DELETE'])
def stations():
	if request.method == 'GET':
		table = Weather_sta_cli
		filter_cols = [table.name, table.lat, table.lon, table.pcp, table.tmp, table.slr, table.hmd, table.wnd, table.wnd_dir, table.atmo_dep]
		table_lookups = {
			table.wgn: Weather_wgn_cli
		}
		return DefaultRestMethods.get_paged_list(table, filter_cols, False, table_lookups, True)
	elif request.method == 'POST':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Weather_sta_cli()
			m.name = args['name']
			m.pcp = args['pcp']
			m.tmp = args['tmp']
			m.slr = args['slr']
			m.hmd = args['hmd']
			m.wnd = args['wnd']
			m.wnd_dir = args['wnd_dir']
			m.atmo_dep = args['atmo_dep']
			m.lat = args['lat']
			m.lon = args['lon']
			if 'wgn_name' in args:
				m.wgn_id = RestHelpers.get_id_from_name(Weather_wgn_cli, args['wgn_name'])
			result = m.save()

			rh.close()
			if result > 0:
				return model_to_dict(m), 201

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except Weather_wgn_cli.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['wgn_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	elif request.method == 'DELETE':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)
		project_base.db.execute_sql("PRAGMA foreign_keys = ON")
		Weather_file.delete().execute()
		Weather_sta_cli.delete().execute()
		rh.close()
		return '', 200

	abort(405, 'HTTP Method not allowed.')

@bp.route('/stations/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def stationsId(id):
	if request.method == 'GET':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)
		try:
			m = Weather_sta_cli.get(Weather_sta_cli.id == id)
			d = model_to_dict(m, recurse=False)
			if m.wgn is not None:
				d["wgn_name"] = m.wgn.name
			rh.close()
			return d
		except Weather_sta_cli.DoesNotExist:
			rh.close()
			abort(404, 'Weather station {id} does not exist'.format(id=id))
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Weather_sta_cli, 'Weather station')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Weather_sta_cli.get(Weather_sta_cli.id == id)
			m.name = args['name']
			m.pcp = args['pcp']
			m.tmp = args['tmp']
			m.slr = args['slr']
			m.hmd = args['hmd']
			m.wnd = args['wnd']
			m.wnd_dir = args['wnd_dir']
			m.atmo_dep = args['atmo_dep']
			m.lat = args['lat']
			m.lon = args['lon']
			if 'wgn_name' in args:
				m.wgn_id = RestHelpers.get_id_from_name(Weather_wgn_cli, args['wgn_name'])

			result = m.save()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except Weather_wgn_cli.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['wgn_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/directory', methods=['GET', 'PUT'])
def directory():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	if request.method == 'GET':
		try:
			config = Project_config.get()
			rh.close()
			return {
				'weather_data_dir': utils.full_path(project_db, config.weather_data_dir)
			}
		except Project_config.DoesNotExist:
			rh.close()
			abort(400, 'Could not retrieve project configuration data.')
	elif request.method == 'PUT':
		try:
			m = Project_config.get()
			m.weather_data_dir = utils.rel_path(project_db, request.json['weather_data_dir'])
			result = m.save()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update project configuration.')
		except Project_config.DoesNotExist:
			rh.close()
			abort(404, 'Could not retrieve project configuration data.')
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/files/<type>/<partial_name>', methods=['GET'])
def files(type, partial_name):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	m = Weather_file.select().where((Weather_file.type == type) & (Weather_file.filename.startswith(partial_name)))

	rh.close()
	return [v.filename for v in m]

# Weather_wgn_cli

@bp.route('/wgn', methods=['GET', 'POST', 'DELETE'])
def wgn():
	if request.method == 'GET':
		table = Weather_wgn_cli
		filter_cols = [table.name, table.lat, table.lon, table.elev, table.rain_yrs]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(Weather_wgn_cli, 'Weather generator')
	elif request.method == 'DELETE':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)
		project_base.db.execute_sql("PRAGMA foreign_keys = ON")
		Weather_wgn_cli_mon.delete().execute()
		Weather_wgn_cli.delete().execute()
		rh.close()
		return '', 200

	abort(405, 'HTTP Method not allowed.')

@bp.route('/wgn/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def wgnId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Weather_wgn_cli, 'Weather generator', back_refs=True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Weather_wgn_cli, 'Weather generator')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, Weather_wgn_cli, 'Weather generator')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/wgn/db', methods=['GET', 'PUT'])
def wgnDb():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	if request.method == 'GET':
		config = Project_config.get()
		wgn_db = None if config.wgn_db is None or config.wgn_db == '' else utils.full_path(project_db, config.wgn_db)
		rh.close()
		return {
			'wgn_db': wgn_db,
			'wgn_table_name': config.wgn_table_name
		}
	elif request.method == 'PUT':
		args = request.json
		if 'wgn_db' not in args or args['wgn_db'] is None or args['wgn_db'] == '':
			return '', 200
		
		try:
			conn = sqlite3.connect(args['wgn_db'])
			conn.row_factory = sqlite3.Row

			monthly_table = "{}_mon".format(args['wgn_table_name'])

			if not db_lib.exists_table(conn, args['wgn_table_name']):
				conn.close()
				rh.close()
				abort(400, 'Table {table} does not exist in {file}.'.format(table=args['wgn_table_name'], file=args['wgn_db']))

			if not db_lib.exists_table(conn, monthly_table):
				conn.close()
				rh.close()
				abort(400, 'Table {table} does not exist in {file}.'.format(table=monthly_table, file=args['wgn_db']))
				
			default_wgn_db = 'C:/SWAT/SWATPlus/Databases/swatplus_wgn.sqlite'
			wgn_db_path = default_wgn_db
			
			if not utils.are_paths_equal(default_wgn_db, args['wgn_db']):
				wgn_db_path = utils.rel_path(project_db, args['wgn_db'])

			m = Project_config.get()
			m.wgn_db = wgn_db_path
			m.wgn_table_name = args['wgn_table_name']
			result = m.save()

			conn.close()
			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update project configuration.')
		except Project_config.DoesNotExist:
			conn.close()
			rh.close()
			abort(404, 'Could not retrieve project configuration data.')
	
	abort(405, 'HTTP Method not allowed.')

# Weather_wgn_cli_mon

@bp.route('/wgn/mon-table/<int:wgn_id>', methods=['GET', 'POST'])
def wgnMon(wgn_id):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)
	
	if request.method == 'GET':
		m = Weather_wgn_cli_mon.select(Weather_wgn_cli_mon.weather_wgn_cli_id == wgn_id).order_by(Weather_wgn_cli_mon.month)
		rh.close()
		return [model_to_dict(v, recurse=False) for v in m]
	elif request.method == 'POST':
		args = request.json
		try:
			e = Weather_wgn_cli_mon.get((Weather_wgn_cli_mon.weather_wgn_cli_id == wgn_id) & (Weather_wgn_cli_mon.month == args['month']))
			rh.close()
			abort(400, 'Weather generator already has data for month {month}.'.format(month=args['month']))
		except Weather_wgn_cli_mon.DoesNotExist:
			m = Weather_wgn_cli_mon()
			m.weather_wgn_cli = wgn_id
			m.month = args['month']
			m.tmp_max_ave = args['tmp_max_ave']
			m.tmp_min_ave = args['tmp_min_ave']
			m.tmp_max_sd = args['tmp_max_sd']
			m.tmp_min_sd = args['tmp_min_sd']
			m.pcp_ave = args['pcp_ave']
			m.pcp_sd = args['pcp_sd']
			m.pcp_skew = args['pcp_skew']
			m.wet_dry = args['wet_dry']
			m.wet_wet = args['wet_wet']
			m.pcp_days = args['pcp_days']
			m.pcp_hhr = args['pcp_hhr']
			m.slr_ave = args['slr_ave']
			m.dew_ave = args['dew_ave']
			m.wnd_ave = args['wnd_ave']
			result = m.save()

			rh.close()
			if result > 0:
				return model_to_dict(m, recurse=False), 201

			abort(400, 'Unable to create weather generator monthly value.')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/wgn/mon-value/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def wgnMonId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Weather_wgn_cli_mon, 'Weather generator monthly value')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Weather_wgn_cli_mon, 'Weather generator monthly value')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, Weather_wgn_cli_mon, 'Weather generator monthly value')

	abort(405, 'HTTP Method not allowed.')

# Atmo_cli

@bp.route('/atmo', methods=['GET', 'PUT', 'DELETE'])
def atmo():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)
	
	if request.method == 'GET':
		m = Atmo_cli.get_or_none()
		staCount = Weather_sta_cli.select().count()
		atmoCount = Atmo_cli.select().count()
		if m is None:
			m = Atmo_cli.create(filename='atmo.cli', timestep='aa', mo_init=0, yr_init=0, num_aa=0)
			
		m = model_to_dict(m, recurse=False)
		m['has_weather_stations'] = staCount > 0
		m['has_atmo_stations'] = atmoCount > 0
		rh.close()
		return m
	elif request.method == 'PUT':
		m = Atmo_cli.get_or_none()
		if m is None:
			m = Atmo_cli.create(filename='atmo.cli', timestep='aa', mo_init=0, yr_init=0, num_aa=0)
		
		args = request.json
		m.filename = args['filename']
		m.timestep = args['timestep']
		m.mo_init = args['mo_init']
		m.yr_init = args['yr_init']
		m.num_aa = args['num_aa']
		result = m.save()

		rh.close()
		if result > 0:
			return '', 200

		abort(400, 'Unable to update atmospheric deposition settings.')
	elif request.method == 'DELETE':
		project_base.db.execute_sql("PRAGMA foreign_keys = ON")
		Atmo_cli_sta_value.delete().execute()
		Atmo_cli_sta.delete().execute()
		Atmo_cli.delete().execute()
		Weather_sta_cli.update(atmo_dep=None).execute()
		rh.close()
		return '', 200
		
	abort(405, 'HTTP Method not allowed.')

# Atmo_cli_sta

@bp.route('/atmo/stations', methods=['GET', 'POST'])
def atmoStations():
	if request.method == 'GET':
		table = Atmo_cli_sta
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		return DefaultRestMethods.post(Atmo_cli_sta, 'Station')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/atmo/stations/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def atmoStationsId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Atmo_cli_sta, 'Station')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Atmo_cli_sta, 'Station')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, Atmo_cli_sta, 'Station')

	abort(405, 'HTTP Method not allowed.')

# Atmo_cli_sta_value

@bp.route('/atmo/stations/<int:sta_id>/values', methods=['GET'])
def atmoStationValues(sta_id):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)
	m = Atmo_cli_sta_value.select(Atmo_cli_sta_value.sta_id == sta_id).order_by(Atmo_cli_sta_value.timestep)
	rh.close()
	return [model_to_dict(v, recurse=False) for v in m]

@bp.route('/atmo/values', methods=['GET', 'POST'])
def atmoValues():
	return DefaultRestMethods.post(Atmo_cli_sta_value, 'Value')

@bp.route('/atmo/values/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def atmoValuesId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Atmo_cli_sta_value, 'Value')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Atmo_cli_sta_value, 'Value')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, Atmo_cli_sta_value, 'Value')

	abort(405, 'HTTP Method not allowed.')
