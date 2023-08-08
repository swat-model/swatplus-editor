from peewee import *
from .base import BaseModel

"""
Ignore reading these files for now. Structure is too variable.
"""
class Water_allo(BaseModel):
	jday = IntegerField(null=True)
	mon = IntegerField(null=True)
	day = IntegerField(null=True)
	yr = IntegerField(null=True)
	unit = IntegerField(null=True)
	dmd_typ = CharField(null=True)
	dmd_num = IntegerField(null=True)
	src1_obj = IntegerField(null=True)
	src1_typ = CharField(null=True)
	src1_num = IntegerField(null=True)
	src1_demand = DoubleField(null=True)
	src1_withdraw = DoubleField(null=True)
	src1_unmet = DoubleField(null=True)


class Water_allo_day(Water_allo):
	pass


class Water_allo_mon(Water_allo):
	pass


class Water_allo_yr(Water_allo):
	pass


class Water_allo_aa(Water_allo):
	pass