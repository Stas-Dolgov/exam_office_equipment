from flask import Flask, render_template, redirect, url_for, flash, request, current_app
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from datetime import datetime
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, DateField, SelectField, FileField
from wtforms.validators import DataRequired, Length, NumberRange
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os
from config import Config
from models import db, User, Equipment, Category, Photo

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)  # Для миграций базы данных

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Для выполнения данного действия необходимо войти."


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class EquipmentForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(max=255)])
    inventory_number = StringField('Инвентарный номер', validators=[DataRequired(), Length(max=50)])
    category_id = SelectField('Категория', coerce=int, validators=[DataRequired()])
    purchase_date = DateField('Дата покупки', validators=[DataRequired()])
    cost = DecimalField('Стоимость', validators=[DataRequired(), NumberRange(min=0)])
    status = SelectField('Статус', choices=[('В эксплуатации', 'В эксплуатации'), ('На ремонте', 'На ремонте'), ('Списано', 'Списано')], validators=[DataRequired()])
    photo_id = SelectField('Фотография', coerce=int, choices=[], validators=[])
    new_photo = FileField('Загрузить новую фотографию', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField('Сохранить')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'purchase_date', type=str)
    sort_order = request.args.get('sort_order', 'desc', type=str)  # от я до а
    category_filter = request.args.get('category', None, type=int)
    status_filter = request.args.get('status', None, type=str)
    date_from = request.args.get('date_from', None, type=str)
    date_to = request.args.get('date_to', None, type=str)

    per_page = 10

    query = Equipment.query

    if category_filter:
        query = query.filter(Equipment.category_id == category_filter)
    if status_filter:
        query = query.filter(Equipment.status == status_filter)

    if date_from:
        date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
        query = query.filter(Equipment.purchase_date >= date_from_dt)
    if date_to:
        date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
        query = query.filter(Equipment.purchase_date <= date_to_dt)

    if sort_by == 'category':
        sort_column = Equipment.category.has(name=Category.name)
    elif sort_by == 'status':
        sort_column = Equipment.status
    elif sort_by == 'purchase_date':
        sort_column = Equipment.purchase_date
    else:
        sort_column = Equipment.purchase_date

    if sort_order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    equipments = pagination.items

    categories = Category.query.all()
    statuses = ['В эксплуатации', 'На ремонте', 'Списано']

    return render_template('index.html',
                           equipments=equipments,
                           pagination=pagination,
                           categories=categories,
                           statuses=statuses,
                           sort_by=sort_by,
                           sort_order=sort_order,
                           category_filter=category_filter,
                           status_filter=status_filter,
                           date_from=date_from,
                           date_to=date_to
                           )


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_equipment():
    if current_user.role != 'admin':
        flash('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('index'))

    form = EquipmentForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    form.photo_id.choices = [(p.id, p.filename) for p in Photo.query.all()]

    if form.validate_on_submit():
        photo_id = None

        if form.new_photo.data:
            file = form.new_photo.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_photo = Photo(filename=filename, mime_type=file.mimetype,
                                  md5_hash='a09f3c477f097c052bc1e6d148842df3')
                db.session.add(new_photo)
                db.session.commit()
                photo_id = new_photo.id
        else:
            photo_id = form.photo_id.data

        equipment = Equipment(name=form.name.data,
                              inventory_number=form.inventory_number.data,
                              category_id=form.category_id.data,
                              purchase_date=form.purchase_date.data,
                              cost=form.cost.data,
                              status=form.status.data,
                              photo_id=photo_id)

        db.session.add(equipment)
        db.session.commit()
        flash('Оборудование успешно добавлено!', 'success')
        return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_equipment(id):
    if current_user.role != 'admin':
        flash('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('index'))
    
    equipment = Equipment.query.get_or_404(id)
    form = EquipmentForm(obj=equipment)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        equipment.name = form.name.data
        equipment.inventory_number = form.inventory_number.data
        equipment.category_id = form.category_id.data
        equipment.purchase_date = form.purchase_date.data
        equipment.cost = form.cost.data
        equipment.status = form.status.data

        # Обработка загрузки фотографии
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                if equipment.photo:
                    try:
                        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], equipment.photo))
                    except FileNotFoundError:
                        pass
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                equipment.photo = filename
        db.session.commit()
        flash('Оборудование успешно обновлено!', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', form=form, equipment=equipment)


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    app.run(debug=True)