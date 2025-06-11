from flask import Blueprint, render_template, redirect, url_for, flash, request
from forms import LoginForm, RegistrationForm
from models import User, db
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрировались! Теперь можете войти.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # Если уже вошел, на главную
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
            return render_template('auth/login.html', form=form)

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))