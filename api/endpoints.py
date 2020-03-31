
from flask_apispec import doc
from flask_apispec import use_kwargs
from flask_apispec import doc
from flask_apispec.extension import FlaskApiSpec
from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_refresh_token_required
from flask_jwt_extended import jwt_required
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from webargs import fields


from utils import create_user
from utils import confirm
from utils import login
from utils import login_refresh
from utils import user_patch
from utils import create_doctor
from utils import password_recovery
from utils import reset_password
from utils import create_registrys
from utils import get_registrys
from utils import registrys_print

from flask import Blueprint
from flask import jsonify


api = Blueprint('api', __name__)


@api.route('/')
def hello():
    return 'This Compose/Flask demo'

@doc(description='Create new user', tags=['users'])
@api.route('/users/', methods=['POST'])
@use_kwargs({
    'email': fields.Email(required=True),
    'type_user': fields.Str(required=True),
    'phone': fields.Str(required=True),
    'identification': fields.Str(required=True),
    'password': fields.Str(required=True)
})
def route_create_users(
    email,
    type_user,
    phone,
    identification,
    password,
):
    return create_user(
        email=email,
        type_user=type_user,
        phone=phone,
        identification=identification,
        password=password,
    )


@doc(description='Confirmation', tags=['user'])
@api.route('/users/confirmation/<_id>/', methods=['GET'])
def route_confirmation(_id):
    return confirm(_id=_id)


@api.route('/login/access/', methods=['POST'])
@use_kwargs({
    'identification': fields.Str(required=True),
    'password': fields.Str(required=True)
})
def route_access_token(identification, password):
    return login(identification, password)


@api.route('/login/refresh/', methods=['POST'])
@jwt_refresh_token_required
def route_refresh_token():
    return login_refresh()


@api.route('/users/me/', methods=['PATCH'])
@use_kwargs({
    'update_fields': fields.Nested({
        'name': fields.Str(),
        'address': fields.Str(),
        'medical_services': fields.List(fields.Str()),
        'date_of_birth': fields.Date(),
    }, required=True)
})
@jwt_required
def route_user_patch(update_fields):
    return user_patch(update_fields)



@api.route('/users/doctor/', methods=['POST'])
@use_kwargs({
    'email': fields.Email(required=True),
    'phone': fields.Str(required=True),
    'identification': fields.Str(required=True),
    'password': fields.Str(required=True),
    'doctor_specialty': fields.Str(required=True),
})
@jwt_required
def route_create_doctor(
    email,
    phone,
    identification,
    password,
    doctor_specialty
):
    return create_doctor(
        email=email,
        type_user='doctor',
        phone=phone,
        identification=identification,
        password=password,
        doctor_specialty=doctor_specialty
    )


@api.route('/password-recovery/', methods=['POST'])
@use_kwargs({'email': fields.Email(required=True)})
def route_password_recovery(email):
    return password_recovery(email=email)


@api.route('/reset-password/', methods=['POST'])
@use_kwargs({
    'token': fields.Str(required=True),
    'new_password': fields.Str(required=True),
    'source': fields.Str(required=True)
})
def route_reset_password(token, new_password, source):
    return reset_password(token=token, new_password=new_password, source=source)


@api.route('/registrys/', methods=['POST'])
@use_kwargs({
    'medical_observations': fields.Str(required=True),
    'health_condition': fields.Str(required=True),
    'id_patient': fields.Str(required=True),
})
@jwt_required
def route_create_registrys(
    medical_observations,
    health_condition,
    id_patient,
):
    return create_registrys(
        id_patient=id_patient,
        medical_observations=medical_observations,
        health_condition=health_condition,
    )


@api.route('/registrys/', methods=['GET'])
@jwt_required
def route_get_registrys():
    return get_registrys()

@api.route('/registrys/to_print/', methods=['GET'])
@jwt_required
def route_registrys_print():
    return registrys_print()