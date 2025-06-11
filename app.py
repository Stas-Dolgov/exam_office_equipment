from flask import Flask, render_template, redirect, url_for, flash, request, Blueprint
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets
from config import Config
from models import db, User, LoginForm

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)  # Для миграций базы данных

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Для выполнения данного действия необходимо пройти процедуру аутентификации."


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Если уже вошел, на главную
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
            return render_template('auth/login.html', form=form)

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

app.register_blueprint(auth_bp)

# === Маршруты (переносим из routes.py) ===
@app.route('/')
def index():
    return render_template('index.html')


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    app.run(debug=True)