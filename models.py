from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, DateTime, func, Column, Integer, String, ForeignKey, Numeric, Date, Text
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))  

    def __repr__(self):
        return f'<Role {self.name}>'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref=db.backref('users_list', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Category {self.name}>'


class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    inventory_number = db.Column(db.String(50), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = relationship("Category", backref="equipment")
    purchase_date = db.Column(db.Date, nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(Enum('В эксплуатации', 'На ремонте', 'Списано', name='equipment_status'), nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=True)
    photo = relationship("Photo", backref="equipment")
    created_at = db.Column(DateTime, default=datetime.utcnow)
    responsible_persons = relationship("Person", secondary="equipment_person", back_populates="equipment")

    def __repr__(self):
        return f'<Equipment {self.name}>'


class Photo(db.Model):
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    mime_type = Column(String(255), nullable=False)
    md5_hash = Column(String(255), nullable=False)

    def __repr__(self):
        return f'<Photo {self.filename}>'


class EquipmentPerson(db.Model):
    __tablename__ = 'equipment_person'
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), primary_key=True)


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(255))
    contact_info = db.Column(db.String(255))

    equipment = relationship("Equipment", secondary="equipment_person", back_populates="responsible_persons") #связь с оборудованием

    def __repr__(self):
        return f'<Person {self.full_name}>'


class MaintenanceLog(db.Model):
    id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer, ForeignKey('equipment.id'), nullable=False)
    equipment = relationship("Equipment", backref="maintenances")
    date = Column(DateTime, nullable=False)
    type_of_maintenance = Column(String(255))  # "Ремонт", "Замена детали"
    comment = Column(Text)

    def __repr__(self):
        return f'<Maintenance {self.date}>'

