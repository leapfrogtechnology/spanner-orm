from time import time
from uuid import uuid4
from spannerorm import BaseModel, IntegerField, StringField, BoolField, TimeStampField, DateField

class Sample(BaseModel):
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
    @StringField.get
    def id(self):
        return self._id

    @id.setter
    @StringField.set
    def id(self, id):
        self._id = id

    @property
    @StringField.get
    def name(self):
        return self._name

    @name.setter
    @StringField.set
    def name(self, name):
        self._name = name

    @property
    @StringField.get
    def address(self):
        return self._address

    @address.setter
    @StringField.set
    def address(self, sub_domain):
        self._address = sub_domain

    @property
    @IntegerField.get
    def points(self):
        return self._points

    @points.setter
    @IntegerField.set
    def points(self, points):
        self._points = points

    @property
    @BoolField.get
    def is_active(self):
        return self._is_active

    @is_active.setter
    @BoolField.set
    def is_active(self, active):
        self._is_active = active

    @property
    @DateField.get
    def join_date(self):
        return self._join_date

    @join_date.setter
    @DateField.set
    def join_date(self, created):
        self._join_date = created

    @property
    @TimeStampField.get
    def modified_at(self):
        return self._modified_at

    @modified_at.setter
    @TimeStampField.set
    def modified_at(self, created):
        self._modified_at = created

    class Meta:
        db_table = 'sample'
        primary_key = 'id'

        @classmethod
        def generate_pk(cls):
            return str(uuid4())
