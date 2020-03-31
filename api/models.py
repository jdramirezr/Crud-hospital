from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    _id = db.Column(db.String(100), primary_key=True)
    identification = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    type_user = db.Column(db.String(100))
    created_at = db.Column(db.DateTime())
    updated_at = db.Column(db.DateTime())
    active = db.Column(db.Boolean())
    medical_services = db.Column(db.ARRAY(db.String()))
    date_of_birth = db.Column(db.Date())
    hashed_password = db.Column(db.String(500))
    name = db.Column(db.String(100))
    address = db.Column(db.String(100))
    last_login = db.Column(db.DateTime())
    updated_password = db.Column(db.DateTime())
    id_hospital = db.Column(db.String(100))
    doctor_specialty = db.Column(db.String(100))

    def __init__(
        self,
        _id,
        identification,
        email,
        phone,
        type_user,
        created_at,
        updated_at,
        active,
        medical_services,
        date_of_birth,
        hashed_password,
        name,
        address,
        last_login,
        updated_password,
        id_hospital,
        doctor_specialty
    ):
        self._id = _id
        self.identification = identification
        self.email = email
        self.phone = phone
        self.type_user = type_user
        self.created_at = created_at
        self.updated_at = updated_at
        self.active = active
        self.medical_services = medical_services
        self.date_of_birth = date_of_birth
        self.hashed_password = hashed_password
        self.name = name
        self.address = address
        self.last_login = last_login
        self.updated_password = updated_password
        self.id_hospital = id_hospital
        self.doctor_specialty = doctor_specialty

    def __repr__(self):
        return '<id {}>'.format(self._id)

    def serialize(self):
        return {
            'identification': self.identification,
            'email': self.email,
            'phone': self.phone,
            'type_user': self.type_user,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'active': self.active,
            'medical_services': self.medical_services,
            'date_of_birth': self.date_of_birth,
            'hashed_password': self.hashed_password,
            'name': self.name,
            'address': self.address,
            'last_login': self.last_login,
            'updated_password': self.updated_password,
            'id_hospital': self.id_hospital,
            'doctor_specialty': self.doctor_specialty
        }


class Registry(db.Model):
    __tablename__ = 'registrys'

    _id = db.Column(db.String(100), primary_key=True)
    id_patient = db.Column(db.String(100))
    id_hospital = db.Column(db.String(100))
    id_doctor = db.Column(db.String(100))
    patient = db.Column(db.String(100))
    hospital = db.Column(db.String(100))
    doctor = db.Column(db.String(100))
    medical_observations = db.Column(db.String(500))
    health_condition = db.Column(db.String(300))
    doctor_specialty = db.Column(db.String(100))
    created_at = db.Column(db.DateTime())

    def __init__(
        self,
        _id,
        id_patient,
        id_hospital,
        id_doctor,
        patient,
        hospital,
        doctor,
        medical_observations,
        health_condition,
        doctor_specialty,
        created_at
    ):
        self._id = _id
        self.id_patient = id_patient
        self.id_hospital = id_hospital
        self.id_doctor = id_doctor
        self.medical_observations = medical_observations
        self.health_condition = health_condition
        self.doctor_specialty = doctor_specialty
        self.created_at = created_at
        self.patient = patient
        self.hospital = hospital
        self.doctor = doctor

    def __repr__(self):
        return '<id {}>'.format(self._id)

    def serialize(self):
        return {
            'patient': self.patient,
            'hospital': self.hospital,
            'doctor': self.doctor,
            'medical_observations': self.medical_observations,
            'health_condition': self.health_condition,
            'doctor_specialty': self.doctor_specialty,
            'created_at': self.created_at
        }