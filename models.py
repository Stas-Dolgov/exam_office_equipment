from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

db = SQLAlchemy()


class User(UserMixin, db.Model):  # UserMixin для flask_login
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # Храним хэш пароля
    role = db.Column(db.String(20), default='user')  # admin, tech, user

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


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
    category = relationship("Category", backref="equipment") #связь с категорией
    purchase_date = db.Column(db.Date, nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(Enum('В эксплуатации', 'На ремонте', 'Списано', name='equipment_status'), nullable=False)
    photo = db.Column(db.String(255))  # Store filename

    responsible_persons = relationship("Person", secondary="equipment_person", back_populates="equipment") #связь с ответственными лицами

    def __repr__(self):
        return f'<Equipment {self.name}>'


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


class MaintenanceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    equipment = relationship("Equipment", backref="maintenance_history") #связь с оборудованием
    date = db.Column(db.DateTime, default=datetime.utcnow)
    maintenance_type = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.Text)

    def __repr__(self):
        return f'<MaintenanceHistory {self.date}>'
