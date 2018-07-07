import user
from time import time
from uuid import uuid4
from spannerorm import BaseModel, StringField, BoolField, TimeStampField, OneToMany


class Role(BaseModel):
    # Db Fields
    _id = StringField(db_column='id', null=False)
    _name = StringField(db_column='name', null=False)
    _is_deleted = BoolField(db_column='is_deleted', default=False)
    _created_at = TimeStampField(db_column='created_at', null=False, default=time())
    _created_by = StringField(db_column='created_by', null=False)
    _updated_at = TimeStampField(db_column='updated_at')
    _updated_by = StringField(db_column='updated_by')

    # Db Relational Field
    _users = OneToMany(join_on='id', reference_module=user, refer_to='role_id')

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
        db_table = 'roles'
        primary_key = 'id'

        @classmethod
        def generate_pk(cls):
            return uuid4()
