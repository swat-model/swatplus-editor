from .base import BaseFileModel, FileColumn as col
from peewee import *
from helpers import utils
import database.project.water_rights as db
from database.project import connect

obj_types = {
	"hru": connect.Hru_con,
	"aqu": connect.Aquifer_con,
	"res": connect.Reservoir_con,
	"cha": connect.Chandeg_con
}

class Water_allocation_wro(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None):
		self.file_name = file_name
		self.version = version
		self.swat_version = swat_version

	def read(self):
		raise NotImplementedError('Reading not implemented yet.')

	def write(self):
		tables = db.Water_allocation_wro.select().order_by(db.Water_allocation_wro.id)
		sources = db.Water_allocation_src_ob.select().order_by(db.Water_allocation_src_ob.id)
		demands = db.Water_allocation_dmd_ob.select().order_by(db.Water_allocation_dmd_ob.id)
		demand_sources = db.Water_allocation_dmd_ob_src.select().order_by(db.Water_allocation_dmd_ob_src.id)
		query = prefetch(tables, sources, demands, demand_sources)

		if tables.count() > 0:
			src_types = db.Water_allocation_src_ob.select(db.Water_allocation_src_ob.obj_typ).distinct()
			src_types_id_dict = {}
			for typ in src_types:
				obj_table = obj_types.get(typ.obj_typ, None)
				if obj_table is not None:
					src_types_id_dict[typ.obj_typ] = [o.id for o in obj_table.select(obj_table.id).order_by(obj_table.id)]

			dmd_types = db.Water_allocation_dmd_ob.select(db.Water_allocation_dmd_ob.obj_typ).distinct()
			dmd_types_id_dict = {}
			for typ in dmd_types:
				obj_table = obj_types.get(typ.obj_typ, None)
				if obj_table is not None:
					dmd_types_id_dict[typ.obj_typ] = [o.id for o in obj_table.select(obj_table.id).order_by(obj_table.id)]

			rcv_types = db.Water_allocation_dmd_ob.select(db.Water_allocation_dmd_ob.rcv_obj).distinct()
			rcv_types_id_dict = {}
			for typ in rcv_types:
				obj_table = obj_types.get(typ.rcv_obj, None)
				if obj_table is not None:
					rcv_types_id_dict[typ.rcv_obj] = [o.id for o in obj_table.select(obj_table.id).order_by(obj_table.id)]

			with open(self.file_name, 'w') as file:
				self.write_meta_line(file)
				file.write(str(tables.count()))
				file.write("\n")

				for row in query:
					header_cols = [col(db.Water_allocation_wro.name, direction="left", padding_override=25),
							   col(db.Water_allocation_wro.rule_typ),
							   col("src_obs", not_in_db=True, padding_override=utils.DEFAULT_INT_PAD),
							   col("dmd_obs", not_in_db=True, padding_override=utils.DEFAULT_INT_PAD),
							   col(db.Water_allocation_wro.cha_ob)]
					self.write_headers(file, header_cols)
					file.write("\n")

					row_cols = [col(row.name, direction="left", padding_override=25),
							col(row.rule_typ),
							col(len(row.src_obs)),
							col(len(row.dmd_obs)),
							col(row.cha_ob, force_bool_type=True)]
					self.write_row(file, row_cols)
					file.write("\n")

					src_header_cols = [col("src_num", not_in_db=True, padding_override=utils.DEFAULT_INT_PAD),
							   col(db.Water_allocation_src_ob.obj_typ),
							   col("obj_num", not_in_db=True, padding_override=utils.DEFAULT_INT_PAD),
							   col("monthly_limit", not_in_db=True, padding_override=utils.DEFAULT_INT_PAD)]
					self.write_headers(file, src_header_cols)
					file.write("\n")

					src_idx = 1
					src_id_to_idx = {}
					for src in row.src_obs:
						obj_table = obj_types.get(src.obj_typ, None)
						obj_id = src.obj_id
						if obj_table is not None:
							obj_id = src_types_id_dict[src.obj_typ].index(src.obj_id) + 1

						description = ''
						if src.description is not None and src.description != '':
							description = '! {}'.format(src.description)

						src_row_cols = [col(src_idx),
										  col(src.obj_typ),
										  col(obj_id),
										  col(src.limit_01),
										  col(src.limit_02),
										  col(src.limit_03),
										  col(src.limit_04),
										  col(src.limit_05),
										  col(src.limit_06),
										  col(src.limit_07),
										  col(src.limit_08),
										  col(src.limit_09),
										  col(src.limit_10),
										  col(src.limit_11),
										  col(src.limit_12),
										  col(description)]
						self.write_row(file, src_row_cols)
						file.write("\n")
						src_id_to_idx[src.id] = src_idx
						src_idx += 1

					dmd_header_cols = [col("dmd_num", not_in_db=True, padding_override=utils.DEFAULT_INT_PAD),
							   col(db.Water_allocation_dmd_ob.obj_typ),
							   col("obj_num", not_in_db=True, padding_override=utils.DEFAULT_INT_PAD),
							   col(db.Water_allocation_dmd_ob.withdr),
							   col(db.Water_allocation_dmd_ob.amount),
							   col(db.Water_allocation_dmd_ob.right),
							   col(db.Water_allocation_dmd_ob.treat_typ),
							   col(db.Water_allocation_dmd_ob.treatment),
							   col(db.Water_allocation_dmd_ob.rcv_obj),
							   col("rcv_num", not_in_db=True, padding_override=utils.DEFAULT_INT_PAD),
							   col(db.Water_allocation_dmd_ob.rcv_dtl),
							   col("num_srcs", not_in_db=True, padding_override=utils.DEFAULT_INT_PAD),
							   col("src", not_in_db=True, padding_override=utils.DEFAULT_INT_PAD),
							   col("frac", not_in_db=True, padding_override=utils.DEFAULT_INT_PAD),
							   col("comp", not_in_db=True, padding_override=utils.DEFAULT_INT_PAD)]

					self.write_headers(file, dmd_header_cols)
					file.write("\n")

					dmd_idx = 1
					for dmd in row.dmd_obs:
						obj_table = obj_types.get(dmd.obj_typ, None)
						obj_id = dmd.obj_id
						if obj_table is not None:
							obj_id = dmd_types_id_dict[dmd.obj_typ].index(dmd.obj_id) + 1

						rcv_table = obj_types.get(dmd.rcv_obj, None)
						rcv_id = dmd.rcv_obj_id
						if rcv_table is not None:
							rcv_id = rcv_types_id_dict[dmd.rcv_obj].index(dmd.rcv_obj_id) + 1

						description = ''
						if dmd.description is not None and dmd.description != '':
							description = '! {}'.format(dmd.description)

						dmd_row_cols = [col(dmd_idx),
										  col(dmd.obj_typ),
										  col(obj_id),
										  col(dmd.withdr),
										  col(dmd.amount),
										  col(dmd.right),
										  col(dmd.treat_typ),
										  col(dmd.treatment),
										  col(dmd.rcv_obj),
										  col(rcv_id),
										  col(dmd.rcv_dtl),
										  col(len(dmd.dmd_src_obs))]
						
						for dmd_src in dmd.dmd_src_obs:
							dmd_row_cols.append(col(src_id_to_idx[dmd_src.src_id]))
							dmd_row_cols.append(col(dmd_src.frac))
							dmd_row_cols.append(col(dmd_src.comp))

						dmd_row_cols.append(col(description))
						self.write_row(file, dmd_row_cols)
						file.write("\n")
						dmd_idx += 1
