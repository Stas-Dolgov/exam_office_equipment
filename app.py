from flask import Flask, render_template, redirect, abort, url_for, flash, request, current_app, send_file, Response
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from datetime import datetime
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, DateField, SelectField, FileField
from wtforms.validators import DataRequired, Length, NumberRange
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import hashlib
import os
from config import Config
from models import db, User, Equipment, Category, Photo, Role

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

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    photo = FileField('Фото', validators=[FileAllowed(ALLOWED_EXTENSIONS)]) 
    new_photo = FileField('Загрузить новую фотографию', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField('Сохранить')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Для выполнения данного действия необходимо пройти процедуру аутентификации.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role.name != role:
                flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
                return redirect(url_for('index')) 
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def generate_md5(filename):
    """Генерирует MD5 хэш для указанного файла."""
    md5_hash = hashlib.md5()
    try:
        with open(filename, "rb") as f:  # Открываем файл в бинарном режиме
            for chunk in iter(lambda: f.read(4096), b""):  # 4096 байт - размер чанка
                md5_hash.update(chunk)
        return md5_hash.hexdigest()  # Возвращаем хэш в шестнадцатеричном формате
    except FileNotFoundError:
        print(f"Файл не найден: {filename}")
        return None
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return None


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


@app.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
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


@app.route('/delete/<int:equipment_id>', methods=['POST'])
@login_required
@role_required('admin')
def equipment_delete(equipment_id):
    if current_user.role.name != 'admin':
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('index'))

    equipment = Equipment.query.get_or_404(equipment_id)
    db.session.delete(equipment)
    db.session.commit()
    flash('Оборудование успешно удалено.', 'success')
    return redirect(url_for('index')) 


@app.route('/equipment/<int:equipment_id>')
@login_required
@role_required('admin')
def equipment_detail(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    return render_template('equipment_detail.html', equipment=equipment)


@app.route('/equipment/<int:equipment_id>/add_maintenance_log', methods=['POST'])
@login_required
@role_required('tech')
def add_maintenance_log(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    comment = request.form.get('comment')

    if comment:
        new_log = MaintenanceLog(equipment_id=equipment_id, comment=comment)
        db.session.add(new_log)
        db.session.commit()

    return redirect(url_for('equipment_detail', equipment_id=equipment_id))


@app.route('/fill_db')
def fill_db():
    with app.app_context():
        admin_role = Role(name='admin', description='Администратор')
        db.session.add(admin_role)
        user_role = Role(name='user', description='Пользователь')
        db.session.add(user_role)
        tech_role = Role(name='tech', description='Тех')
        db.session.add(tech_role)

        admin = User(username='admin1', role=admin_role)
        admin.set_password('str0ng_p@ssWORD371')
        db.session.add(admin)

        user = User(username='Vasya', role=user_role)
        user.set_password('beer_in_hand-m4t_0n_bOaRd')
        db.session.add(user)

        user = User(username='user', role=user_role)
        user.set_password('who-IS-it?9')
        db.session.add(user)

        tech = User(username='user3', role=tech_role)
        user.set_password('йцукенгшщзх757575')
        db.session.add(user)

        tech = User(username='user5', role=tech_role)
        user.set_password('hf8374')
        db.session.add(user)

        db.session.commit()

    return "БД заполнена"


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_equipment(id):
    if current_user.role.name != 'admin':
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

        if form.photo.data:  # Проверяем, был ли загружен файл
            file = form.photo.data
            filename = secure_filename(file.filename)
            # Генерируем уникальное имя файла
            timestamp = int(datetime.now().timestamp())
            new_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
            # Вычисляем MD5-хеш
            md5_hash = generate_md5(filepath)
            # Проверяем, существует ли уже файл с таким хешем
            existing_photo = Photo.query.filter_by(md5_hash=md5_hash).first()
            if existing_photo:

                equipment.photo_id = existing_photo.id
                try: 
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], equipment.photo))
                except:
                    pass
            else:
                file.save(filepath)
                photo = Photo(filename=new_filename, mime_type=file.mimetype, md5_hash=md5_hash)
                db.session.add(photo)
                db.session.commit()

                equipment.photo_id = photo.id
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], equipment.photo))
                except:
                    pass
            equipment.photo = new_filename

        db.session.commit()
        flash('Оборудование успешно обновлено!', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', form=form, equipment=equipment)


@app.route('/uploads/<filename>')
def show_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def export_equipment_to_xml():
    equipment_list = Equipment.query.all()

    root = Element('EquipmentList')
    for equipment in equipment_list:
        equipment_element = SubElement(root, 'Equipment')

        name = SubElement(equipment_element, 'Name')
        name.text = equipment.name

        inventory_number = SubElement(equipment_element, 'InventoryNumber')
        inventory_number.text = equipment.inventory_number

        category = SubElement(equipment_element, 'Category')
        category.text = equipment.category.name

        purchase_date = SubElement(equipment_element, 'PurchaseDate')
        purchase_date.text = equipment.purchase_date.strftime('%Y-%m-%d')

        cost = SubElement(equipment_element, 'Cost')
        cost.text = str(equipment.cost)

        status = SubElement(equipment_element, 'Status')
        status.text = equipment.status

    xml_string = tostring(root, 'utf-8')
    dom = minidom.parseString(xml_string)
    pretty_xml_string = dom.toprettyxml()

    return pretty_xml_string

@app.route('/export_to_1c')
def export_to_1c():
    xml_data = export_equipment_to_xml()
    response =  Response(xml_data, mimetype='text/xml')
    response.headers['Content-Disposition'] = 'attachment; filename=equipment.xml'

    return response


if __name__ == '__main__':
    app.run(debug=True)