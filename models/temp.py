from time import time
from uuid import uuid4
from spannerorm import BaseModel, IntegerField, StringField, BoolField, TimeStampField, DateField


class Temp(BaseModel):
    # Db Fields
    _id = StringField(db_column='id', null=False)
    _name = StringField(db_column='name', null=False, reg_exr='^[A-Z][ a-z]+')
    _address = StringField(db_column='address', null=True)
    _points = IntegerField(db_column='points', default=0, min_value=10, max_value=1000)
    _is_active = BoolField(db_column='is_active', default=True)
    _join_date = DateField(db_column='join_date', null=False)
    _modified_at = TimeStampField(db_column='modified_at', null=True, default=time())

    # Transient field
    _details = None

    @property
    def id(self):
        return self._id.value

    @id.setter
    def id(self, id):
        self._id.value = id

    @property
    def name(self):
        return self._name.value

    @name.setter
    def name(self, name):
        self._name.value = name

    @property
    def address(self):
        return self._address.value

    @address.setter
    def address(self, sub_domain):
        self._address.value = sub_domain

    @property
    def points(self):
        return self._points.value

    @points.setter
    def points(self, points):
        self._points.value = points

    @property
    def is_active(self):
        return self._is_active.value

    @is_active.setter
    def is_active(self, active):
        self._is_active.value = active

    @property
    def join_date(self):
        return self._join_date.value

    @join_date.setter
    def join_date(self, created):
        self._join_date.value = created

    @property
    def modified_at(self):
        return self._modified_at.value

    @modified_at.setter
    def modified_at(self, created):
        self._modified_at.value = created

    class Meta:
        db_table = 'temp'
        primary_key = 'id'

        @classmethod
        def generate_pk(cls):
            return uuid4()
