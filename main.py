from flask_wtf import FlaskForm
import flask
from flask_login import LoginManager, login_user, current_user
from flask import Flask, render_template, redirect, request, \
    make_response, jsonify
from wtforms import *
from data import db_session, users, jobs, departments, jobs_api, user_api, users_resource
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField
from requests import get
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__, template_folder='./template', static_folder='./static')
app.config['SECRET_KEY'] = 'yandex_lyceum_secret_key'
api = Api(app)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль')
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class JobForm(FlaskForm):
    team_leader = StringField('Главный', validators=[DataRequired()])
    jod = StringField('Описание', validators=[DataRequired()])
    work_size = StringField('Количество часов для выполнения', validators=[DataRequired()])
    collaborators = StringField('Сотрудники (перечисление через запятую)', validators=[DataRequired()])
    is_finished = BooleanField('Закончена работа', default=0)
    add = SubmitField('Сохранить')


class DepForm(FlaskForm):
    title = StringField('Описание', validators=[DataRequired()])
    chief = IntegerField('Начальник', validators=[DataRequired()])
    members = StringField('Сотрудники (перечисление через запятую)', validators=[DataRequired()])
    email = EmailField('Почта')
    add = SubmitField('Сохранить')


def get_coords(place):
    apikey = "40d1649f-0493-4b70-98ba-98533de7710b"
    map_request = f"https://geocode-maps.yandex.ru/1.x/?geocode={place}&apikey={apikey}&format=json"
    response = get(map_request)
    if not response:
        print('Try again...')
    json_response = response.json()
    try:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    except IndexError:
        print('Try again...')
    x, y = map(float, toponym["Point"]["pos"].split())
    return x, y


def save_picture(addr):
    map_request = f"http://static-maps.yandex.ru/1.x/?" \
        f"ll={','.join(map(str, get_coords(addr)))}&" \
        f"z=12&" \
        f"l=sat&" \
        f"size=650,450"
    response = get(map_request)
    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
    map_f = f"./static/map.png"
    with open(map_f, "wb") as file:
        file.write(response.content)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(users.User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(users.User).filter(users.User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/')
def work_log():
    session = db_session.create_session()
    return render_template('prof.html', peoples=session.query(users.User),
                           jobs=session.query(jobs.Jobs))


@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    form = JobForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        job = jobs.Jobs(
            team_leader=form.team_leader.data,
            jod=form.jod.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            is_finished=form.is_finished.data,
        )
        if current_user.__name__ is not None:
            job.add_by = current_user.id
        session.add(job)
        session.commit()
        return redirect('/')
    return render_template('add_job.html', form=form)


@app.route('/editing_job/<int:id>', methods=['GET', 'POST'])
def edit_news(id):
    form = JobForm()
    if request.method == "GET":
        session = db_session.create_session()
        job = session.query(jobs.Jobs).filter(jobs.Jobs.id == id).first()
        if job:
            form.team_leader = job.team_leader
            form.jod = job.jod
            form.work_size = job.work_size
            form.collaborators = job.collaborators
            form.is_finished = job.is_finished
        else:
            flask.abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        if current_user.__name__ is None:
            job = session.query(jobs.Jobs).filter(jobs.Jobs.add_by == 1, jobs.Jobs.id == id).first()
        else:
            job = session.query(jobs.Jobs).filter(((jobs.Jobs.add_by == 1) |
                                                   (jobs.Jobs.add_by == current_user.id)),
                                                  jobs.Jobs.id == id).first()
        if job:
            job.team_leader = form.team_leader
            job.jod = form.jod
            job.work_size = form.work_size
            job.collaborators = form.collaborators
            job.is_finished = form.is_finished
            session.commit()
            return redirect('/')
        else:
            flask.abort(404)
    return render_template('add_job.html', form=form)


@app.route('/job_delete/<int:id>', methods=['GET', 'POST'])
def job_delete(id):
    session = db_session.create_session()
    job = session.query(jobs.Jobs).filter(jobs.Jobs.id == id).first()
    if job:
        if current_user.__name__ is not None:
            if job.add_by == current_user.id or current_user.id == 1:
                session.delete(job)
                session.commit()
            else:
                flask.abort(403)
        else:
            flask.abort(403)
    else:
        flask.abort(404)
    return redirect('/')


@app.route('/departments')
def department():
    session = db_session.create_session()
    print(*session.query(departments.Departments))
    return render_template('department.html', departments=session.query(departments.Departments),
                           peoples=session.query(users.User))


@app.route('/department_delete/<int:id>', methods=['GET', 'POST'])
def dep_delete(id):
    session = db_session.create_session()
    job = session.query(departments.Departments).filter(departments.Departments.id == id).first()
    if job:
        if current_user.__name__ is not None:
            if job.add_by == current_user.id or current_user.id == 1:
                session.delete(job)
                session.commit()
            else:
                flask.abort(403)
        else:
            flask.abort(403)
    else:
        flask.abort(404)
    return redirect('/')


@app.route('/editing_department/<int:id>', methods=['GET', 'POST'])
def edit_dep(id):
    form = DepForm()
    if request.method == "GET":
        session = db_session.create_session()
        job = session.query(departments.Departments).filter(departments.Departments.id == id).first()
        if job:
            form.title = job.title
            form.chief = job.chief
            form.members = job.members
            form.email = job.email
        else:
            flask.abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        if current_user.__name__ is None:
            job = session.query(departments.Departments).filter(departments.Departments.add_by == 1,
                                                                departments.Departments.id == id).first()
        else:
            job = session.query(departments.Departments).filter(((departments.Departments.add_by == 1) |
                                                                 (departments.Departments.add_by == current_user.id)),
                                                                departments.Departments.id == id).first()
        if job:
            job.title = form.title
            job.chief = form.chief
            job.members = form.members
            job.email = form.email
            session.commit()
            return redirect('/')
        else:
            flask.abort(404)
    return render_template('add_department.html', form=form)


@app.route('/add_departments')
def add_dep():
    form = DepForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        job = jobs.Jobs(
            title=form.title.data,
            chief=form.chief.data,
            members=form.members.data,
            email=form.email.data
        )
        if current_user.__name__ is not None:
            job.add_by = current_user.id
        session.add(job)
        session.commit()
        return redirect('/')
    return render_template('add_department.html', form=form)


@app.route('/users_show/<int:user_id>')
def users_city(user_id):
    try:
        user = get(f'http://127.0.0.1:5000/api/users/{user_id}').json()['users']
    except KeyError:
        return 'Not found'
    city = user['city_from']
    name = user['name']
    surname = user['surname']
    save_picture(city)
    return render_template('users_show.html', surname=surname, name=name)


if __name__ == '__main__':
    db_session.global_init("db/blogs.sqlite")
    api.add_resource(users_resource.UsersListResource, '/api/v2/users')
    api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(user_api.blueprint)
    app.run()
