from datetime import datetime
from datetime import timedelta
import uuid
import requests
import base64
import csv
import json

from flask import render_template
from flask import abort
from flask import jsonify
from flask import send_file

from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import jwt_refresh_token_required
from flask_jwt_extended import get_current_user
from jwt.exceptions import InvalidTokenError
import jwt

from passlib.context import CryptContext
from dateutil.tz import tzstr


from config import *
from models import *



pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_user(identification):
    return User.query.filter_by(identification=identification).first().identification


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def hashed_password(password):
    return pwd_context.hash(password)


def generator_id(obj_type):
    return f'{obj_type}::{str(uuid.uuid4())}'

def get_current_date():
    return datetime.now(tzstr(s='GMT-5')).strftime(DATE_FORMAT)

def validate(email, identification):

    if User.query.filter(
        (User.email==email) | (User.identification==identification),
        User.active==True
    ).first():
        abort(404, 'there is already a user with this email or identification')


def send_email(email_to, identification, _id):
    context = {
        'project_name': 'Heippi',
        'id': identification,
        'email': email_to,
        'link': f'{LINK}{CONFIRMATION}{_id}/',
    }

    response = requests.post(
        MAILGUN_DOMAIN,
        auth=('api', MAILGUN_API_KEY),
        data={
            'from': f'Heippi <{EMAIL_SEND}>',
            'to': email_to,
            'subject': 'Confirmacion cuenta',
            'html': render_template('new_account.html', **context)
        }
    )

    if response:
        return {'msg': 'Email sent'}
    return {'msg': 'The mail could not be sent'}


def send_email_recoverd(email_to, token):
    context = {
        'project_name': 'Heippi',
        'link': f'{LINK}/recoverd/{token}/',
        'valid_hours': 1
    }

    response = requests.post(
        MAILGUN_DOMAIN,
        auth=('api', MAILGUN_API_KEY),
        data={
            'from': f'Heippi <{EMAIL_SEND}>',
            'to': email_to,
            'subject': 'Recuperacion de cuenta',
            'html': render_template('reset_password.html', **context)
        }
    )

    if response:
        return {'msg': 'Email sent'}
    return {'msg': 'The mail could not be sent'}


def access(identification):
    return {
        'access_token': create_access_token(
            identity=identification,
            expires_delta=timedelta(minutes=60 * 8)
        ),
        'refresh_token': create_refresh_token(
            identity=identification,
            expires_delta=timedelta(minutes=60 * 8)
        ),
        'token_type': 'Bearer',
    }


def confirm(_id):
    user = User.query.get(_id)

    if user:
        user.active = True
        db.session.commit()
        return {'msg': 'User active'}

    abort(404, 'The user with that id does not exist')


def update_attributes(user, update_fields):
    for key, value in update_fields.items():
        if key == 'date_of_birth':
            user.date_of_birth = value
        if key == 'name':
            user.name = value
        if key == 'address':
            user.address = value
        if key == 'medical_services':
            user.medical_services = value

        db.session.commit()


def create_user(
    email,
    type_user,
    phone,
    identification,
    password,
):
    if not type_user in (PATIENT_ROL, HOSPITAL_ROL):
        abort(404, 'The type of user must be patient or hospital')

    date_time = get_current_date()
    validate(email=email, identification=identification)
    _id = generator_id(USER)
    hashed = hashed_password(password=password)

    new_user = User(
        _id=_id,
        identification=identification,
        email=email,
        phone=phone,
        type_user=type_user,
        date_of_birth=None,
        medical_services=None,
        created_at=date_time,
        updated_at=date_time,
        active=False,
        hashed_password=hashed,
        name=None,
        address=None,
        updated_password=None,
        last_login=None,
        id_hospital=None,
        doctor_specialty=False
    )

    db.session.add(new_user)
    db.session.commit()

    return send_email(email_to=email, identification=identification, _id=_id)

def create_doctor(
    email,
    type_user,
    phone,
    identification,
    password,
    doctor_specialty
):
    user = User.query.filter_by(
        identification=get_current_user(),
        active=True
    ).first()

    if not user:
        abort(404,'user does not exist or user not active')

    if not user.type_user == HOSPITAL_ROL:
        abort(401,'Only hospitals can create doctors')

    date_time = get_current_date()
    validate(email=email, identification=identification)
    _id = generator_id(USER)
    hashed = hashed_password(password=password)

    new_user = User(
        _id=_id,
        identification=identification,
        email=email,
        phone=phone,
        type_user=type_user,
        date_of_birth=None,
        medical_services=None,
        created_at=date_time,
        updated_at=date_time,
        active=False,
        hashed_password=hashed,
        name=None,
        address=None,
        updated_password=None,
        last_login=None,
        id_hospital=user._id,
        doctor_specialty=doctor_specialty
    )

    db.session.add(new_user)
    db.session.commit()

    return send_email(email_to=email, identification=identification, _id=_id)



def login(identification, password):
    user = User.query.filter_by(
        identification=identification,
        active=True
    ).first()


    if not user:
        abort(
            404,
            'There is no user with this identification or user not active'
        )

    if not verify_password(
        password=password,
        hashed_password=user.hashed_password
    ):
        abort(404, 'There is no user with this password')

    if user.type_user == DOCTOR_ROL:
        if user.last_login and not user.updated_password:
            abort(401, 'The medical role user must change the password')

    user.last_login = get_current_date()
    db.session.commit()
    return access(identification=identification)


def login_refresh():
    user_identification = get_current_user()
    return access(identification=user_identification)

def user_patch(update_fields):
    user = User.query.filter_by(
        identification=get_current_user(),
        active=True
    ).first()

    if not user:
        abort(404,'user does not exist or user not active')

    type_user = user.type_user

    if type_user == HOSPITAL_ROL:
        if update_fields.get('date_of_birth'):
            abort(401, 'The user hospital have not date_of birth')
        update_attributes(user, update_fields)

    if type_user == PATIENT_ROL:
        if update_fields.get('medical_services'):
            abort(401, 'The user patient have not medical_services')
        update_attributes(user, update_fields)

    if type_user == DOCTOR_ROL:
        update_attributes(user, update_fields)

    user.updated_at = get_current_date()
    db.session.commit()

    return jsonify(user.serialize())


def password_recovery(email):
    user = User.query.filter_by(
        email=email,
        active=True
    ).first()

    if not user:
        abort(404, 'The user with this email does not exist in the db')

    token = create_access_token(
            identity=email,
            expires_delta=timedelta(minutes=60 * 1)
        )

    return send_email_recoverd(email_to=email, token=token)

def reset_password(token, new_password, source):
    identity = verify_token(token)
    if not identity:
        abort(400, 'Invalid token')
    if source == 'email':
        user = User.query.filter_by(
            email=identity,
            active=True
        ).first()
    else:
        user = User.query.filter_by(
            identification=identity,
            active=True
        ).first()

    if not user:
        abort(404, 'No user')

    hashed = hashed_password(password=new_password)
    user.hashed_password = hashed
    user.updated_password = get_current_date()
    db.session.commit()

    return {'msg': 'Password updated successfully'}

def verify_token(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if 'identity' in decoded_token:
            return decoded_token['identity']
        return False
    except InvalidTokenError:
        return False

def create_registrys(
    medical_observations,
    health_condition,
    id_patient,
):
    user = User.query.filter_by(
        identification=get_current_user(),
        active=True
    ).first()

    if not user:
        abort(404,'user does not exist or user not active')

    if user.type_user != DOCTOR_ROL:
        abort(401,'only doctors can have records')

    patient =  User.query.filter_by(_id=id_patient, active=True).first()

    if not patient or patient.type_user != PATIENT_ROL:
        abort(401,'patient does not exist or not active')

    registry = Registry(
        _id=generator_id(REGISTRY),
        id_patient=id_patient,
        id_hospital=user.id_hospital,
        id_doctor=user._id,
        patient=User.query.get(id_patient).name,
        hospital=User.query.get(user.id_hospital).name,
        doctor=user.name,
        medical_observations=medical_observations,
        health_condition=health_condition,
        doctor_specialty=user.doctor_specialty,
        created_at=get_current_date()
    )
    db.session.add(registry)
    db.session.commit()

    return jsonify(registry.serialize())

def get_registrys_data():
    user = User.query.filter_by(
        identification=get_current_user(),
        active=True
    ).first()

    if not user:
        abort(404,'user does not exist or user not active')

    if user.type_user == PATIENT_ROL:
        registrys = Registry.query.filter_by(id_patient=user._id).all()
        if not registrys:
            abort(404,'user does not have registrys')
        return return_registrys(registrys)

    if user.type_user == DOCTOR_ROL:
        registrys = Registry.query.filter_by(id_doctor=user._id).all()
        if not registrys:
            abort(404,'user does not have registrys')
        return return_registrys(registrys)

    if user.type_user == DOCTOR_ROL:
        registrys = Registry.query.filter_by(id_hospital=user._id).all()
        if not registrys:
            abort(404,'user does not have registrys')
        return return_registrys(registrys)

    abort(404, 'The user not have rol')

def get_registrys():
    return jsonify(get_registrys_data())

def return_registrys(registrys):
    return [registry.serialize() for registry in registrys]

def registrys_print():
    registrys = get_registrys_data()
    if registrys:
        text_file = open('response.csv', 'w')
        text_file.truncate()

        for registry in registrys:
            with open('response.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([])
                writer.writerow([1, "Nombre del paciente:", f"{registry.get('patient')}"])
                writer.writerow([2, "Nombre del doctor:", f"{registry.get('doctor')}"])
                writer.writerow([3, "Especialidad del doctor:", f"{registry.get('doctor_specialty')}"])
                writer.writerow([4, "Estado de salud:", f"{registry.get('health_condition')}"])
                writer.writerow([5, "Hospital:", f"{registry.get('hospital')}"])
                writer.writerow([6, "Observaciones medicas:", f"{registry.get('medical_observations')}"])
                writer.writerow([7, "Fecha del registro:", f"{registry.get('created_at')}"])


    return send_file('response.csv',
        mimetype='text/csv',
        attachment_filename='response.csv',
        as_attachment=True
    )