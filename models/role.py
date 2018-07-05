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
    def is_deleted(self):
        return self._is_deleted.value

    @is_deleted.setter
    def is_deleted(self, is_deleted):
        self._is_deleted.value = is_deleted

    @property
    def created_at(self):
        return self._created_at.value

    @created_at.setter
    def created_at(self, created_at):
        self._created_at.value = created_at

    @property
    def created_by(self):
        return self._created_by.value

    @created_by.setter
    def created_by(self, created_by):
        self._created_by.value = created_by

    @property
    def updated_at(self):
        return self._updated_at.value

    @updated_at.setter
    def updated_at(self, updated_at):
        self._updated_at.value = updated_at

    @property
    def updated_by(self):
        return self._updated_by.value

    @updated_by.setter
    def updated_by(self, updated_by):
        self._updated_by.value = updated_by

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

        def get_user(self):
            return user.User

        @classmethod
        def generate_pk(cls):
            return uuid4()
