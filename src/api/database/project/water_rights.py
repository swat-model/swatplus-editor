from peewee import *
from . import base


class Water_allocation_wro(base.BaseModel):
	name = CharField(unique=True)
	rule_typ = CharField()
	cha_ob = BooleanField()


class Water_allocation_src_ob(base.BaseModel):
	water_allocation = ForeignKeyField(Water_allocation_wro, on_delete = 'CASCADE', related_name='src_obs')
	obj_typ = CharField(default='unl')
	obj_id = IntegerField(default=0)
	limit_01 = IntegerField(default=0)
	limit_02 = IntegerField(default=0)
	limit_03 = IntegerField(default=0)
	limit_04 = IntegerField(default=0)
	limit_05 = IntegerField(default=0)
	limit_06 = IntegerField(default=0)
	limit_07 = IntegerField(default=0)
	limit_08 = IntegerField(default=0)
	limit_09 = IntegerField(default=0)
	limit_10 = IntegerField(default=0)
	limit_11 = IntegerField(default=0)
	limit_12 = IntegerField(default=0)
	description = CharField(null=True)


class Water_allocation_dmd_ob(base.BaseModel):
	water_allocation = ForeignKeyField(Water_allocation_wro, on_delete = 'CASCADE', related_name='dmd_obs')
	obj_typ = CharField(default='hru')
	obj_id = IntegerField(default=0)
	withdr = CharField()
	amount = DoubleField()
	right = CharField()
	treat_typ = CharField(null=True)
	treatment = CharField(null=True)
	rcv_obj = CharField(null=True)
	rcv_obj_id = IntegerField(default=0)
	rcv_dtl = CharField(null=True)
	description = CharField(null=True)


class Water_allocation_dmd_ob_src(base.BaseModel):
	water_allocation_dmd_ob = ForeignKeyField(Water_allocation_dmd_ob, on_delete = 'CASCADE', related_name='dmd_src_obs')
	src = ForeignKeyField(Water_allocation_src_ob, null=True, on_delete='SET NULL')
	frac = DoubleField()
	comp = BooleanField()
