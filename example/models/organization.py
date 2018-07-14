from . import user
from time import time
from uuid import uuid4
from spannerorm import BaseModel, StringField, BoolField, TimeStampField, OneToMany


class Organization(BaseModel):
    # Db Fields
    _id = StringField(db_column='id', null=False)
    _name = StringField(db_column='name', null=False)
    _sub_domain = StringField(db_column='sub_domain', null=False)
    _logo = StringField(db_column='logo')
    _state = StringField(db_column='state', null=False)
    _zip_code = StringField(db_column='zip_code', max_length=20, reg_exr='^(\d{5})([- ])?(\d{4})?$')
    _is_deleted = BoolField(db_column='is_deleted', default=False)
    _created_at = TimeStampField(db_column='created_at', null=False, default=time())
    _created_by = StringField(db_column='created_by', null=False)
    _updated_at = TimeStampField(db_column='updated_at')
    _updated_by = StringField(db_column='updated_by')

    # Db Relational Field
    _users = OneToMany(join_on='id', relation_name='users', refer_to='organization_id')

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
    def sub_domain(self):
        return self._sub_domain

    @sub_domain.setter
    @StringField.set
    def sub_domain(self, sub_domain):
        self._sub_domain = sub_domain

    @property
    @StringField.get
    def logo(self):
        return self._logo

    @logo.setter
    @StringField.set
    def logo(self, logo_url):
        self._logo = logo_url

    @property
    @StringField.get
    def state(self):
        return self._state

    @state.setter
    @StringField.set
    def state(self, state):
        self._state = state

    @property
    @StringField.get
    def zip_code(self):
        return self._zip_code

    @zip_code.setter
    @StringField.set
    def zip_code(self, zip_code):
        self.zip_code = zip_code

    @property
    @BoolField.get
    def is_deleted(self):
        return self._is_deleted

    @is_deleted.setter
    @BoolField.set
    def is_deleted(self, is_deleted):
        self._is_deleted = is_deleted

    @property
    @TimeStampField.get
    def created_at(self):
        return self._created_at

    @created_at.setter
    @TimeStampField.set
    def created_at(self, created_at):
        self._created_at = created_at

    @property
    @TimeStampField.get
    def created_by(self):
        return self._created_by

    @created_by.setter
    @StringField.set
    def created_by(self, created_by):
        self._created_by = created_by

    @property
    @TimeStampField.get
    def updated_at(self):
        return self._updated_at

    @updated_at.setter
    @TimeStampField.set
    def updated_at(self, updated_at):
        self._updated_at = updated_at

    @property
    @StringField.get
    def updated_by(self):
        return self._updated_by

    @updated_by.setter
    @StringField.set
    def updated_by(self, updated_by):
        self._updated_by = updated_by

    @property
    @OneToMany.get
    def users(self):
        return self._users

    @users.setter
    @OneToMany.set
    def users(self, data_list):
        self._users = data_list

    class Meta:
        db_table = 'organizations'
        primary_key = 'id'

        @classmethod
        def relations(cls):
            return {
                'users': user.User
            }

        @classmethod
        def generate_pk(cls):
            return str(uuid4())
