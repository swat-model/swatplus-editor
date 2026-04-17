from peewee import *

db = SqliteDatabase(None)


class BaseModel(Model):
	class Meta:
		database = db


class OutputBase(BaseModel):
	jday = IntegerField(null=True)
	mon = IntegerField(null=True)
	day = IntegerField(null=True)
	yr = IntegerField(null=True)
	unit = IntegerField(null=True)
	gis_id = IntegerField(null=True)
	name = CharField(null=True)


class Project_config(BaseModel):
	project_name = CharField(null=True)
	editor_version = CharField(null=True)
	swat_version = CharField(null=True)
	output_import_time = DateTimeField(null=True)


class Table_description(BaseModel):
	table_name = CharField(primary_key=True)
	description = CharField()


class Column_description(BaseModel):
	table_name = ForeignKeyField(Table_description, column_name='table_name', on_delete='CASCADE', backref='columns')
	column_name = CharField()
	units = CharField(null=True)
	description = CharField(null=True)


class Table_group(BaseModel):
	group_name = CharField(primary_key=True)
	tables = CharField()


class Definition(BaseModel):
	table_group = ForeignKeyField(Table_group, on_delete='CASCADE', related_name='definitions')
	column_name = CharField()
	units = CharField(null=True)
	description = CharField(null=True)


class Mgt_out(BaseModel):
	hru = IntegerField(null=True)
	year = IntegerField(null=True)
	mon = IntegerField(null=True)
	day = IntegerField(null=True)
	crop = CharField(null=True)
	operation = CharField(null=True)
	phubase = DoubleField(null=True)
	phuplant = DoubleField(null=True)
	soil_water = DoubleField(null=True)
	plant_bioms = DoubleField(null=True)
	surf_rsd = DoubleField(null=True)
	soil_no3 = DoubleField(null=True)
	soil_solp = DoubleField(null=True)
	op_var = DoubleField(null=True)
	var1 = DoubleField(null=True)
	var2 = DoubleField(null=True)
	var3 = DoubleField(null=True)
	var4 = DoubleField(null=True)
	var5 = DoubleField(null=True)
	var6 = DoubleField(null=True)
	var7 = DoubleField(null=True)
