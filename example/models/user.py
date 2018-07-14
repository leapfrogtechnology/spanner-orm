import hashlib
from . import role
from time import time
from uuid import uuid4
from . import organization
from spannerorm import BaseModel, StringField, BoolField, TimeStampField, ManyToOne


class User(BaseModel):
    # Db column Fields
    _id = StringField(db_column='id', null=False)
    _acl = StringField(db_column='acl')
    _name = StringField(db_column='name', null=False)
    _email = StringField(db_column='email', null=False, reg_exr='^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    _password = StringField(db_column='password')
    _phone_number = StringField(db_column='phone_number',
                                reg_exr='^[(]{0,1}[0-9]{3}[)]{0,1}[-\s\.]{0,1}[0-9]{3}[-\s\.]{0,1}[0-9]{4}$')
    _photo_url = StringField(db_column='photo_url')
    _is_deleted = BoolField(db_column='is_deleted', default=False)
    _organization_id = StringField(db_column='organization_id', null=False)
    _role_id = StringField(db_column='role_id', null=False)
    _created_at = TimeStampField(db_column='created_at', null=False, default=time())
    _created_by = StringField(db_column='created_by', null=False)
    _updated_at = TimeStampField(db_column='updated_at')
    _updated_by = StringField(db_column='updated_by')

    # Relational Fields
    _role = ManyToOne(join_on='role_id', relation_name='role', refer_to='id')
    _organization = ManyToOne(join_on='organization_id', relation_name='organization', refer_to='id')

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
    def email(self):
        return self._email

    @email.setter
    @StringField.set
    def email(self, sub_domain):
        self._email = sub_domain

    @property
    @StringField.get
    def password(self):
        return self._password

    @password.setter
    @StringField.set
    def password(self, password):
        hash_password = hashlib.md5(password.value)
        password.value = hash_password.hexdigest()
        self._password = password

    @property
    @StringField.get
    def phone_number(self):
        return self._phone_number

    @phone_number.setter
    @StringField.set
    def phone_number(self, phone_number):
        self._phone_number = phone_number

    @property
    @StringField.get
    def photo_url(self):
        return self._photo_url

    @photo_url.setter
    @StringField.set
    def photo_url(self, photo_url):
        self._photo_url = photo_url

    @property
    @BoolField.get
    def is_deleted(self):
        return self._is_deleted

    @is_deleted.setter
    @BoolField.set
    def is_deleted(self, is_deleted):
        self._is_deleted = is_deleted

    @property
    @StringField.get
    def organization_id(self):
        return self._organization_id

    @organization_id.setter
    @StringField.set
    def organization_id(self, organization_id):
        self._organization_id = organization_id

    @property
    @StringField.get
    def role_id(self):
        return self._role_id

    @role_id.setter
    @StringField.set
    def role_id(self, role_id):
        self._role_id = role_id

    @property
    @TimeStampField.get
    def created_at(self):
        return self._created_at

    @created_at.setter
    @TimeStampField.set
    def created_at(self, created_at):
        self._created_at = created_at

    @property
    @StringField.get
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
    @ManyToOne.get
    def role(self):
        return self._role

    @role.setter
    @ManyToOne.set
    def role(self, data):
        self._role = data

    @property
    @ManyToOne.get
    def organization(self):
        return self._organization

    @organization.setter
    @ManyToOne.set
    def organization(self, data):
        self._organization = data

    class Meta:
        db_table = 'users'
        primary_key = 'id'

        @classmethod
        def relations(cls):
            return {
                'role': role.Role,
                'organization': organization.Organization
            }

        @classmethod
        def generate_pk(cls):
            return str(uuid4())
