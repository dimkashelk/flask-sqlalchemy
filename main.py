from flask_wtf import FlaskForm
from flask_login import LoginManager, login_user
from flask import Flask, render_template, redirect
from wtforms import *
from data import db_session, users, jobs
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField

app = Flask(__name__, template_folder='./template')
app.config['SECRET_KEY'] = 'yandex_lyceum_secret_key'


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class AddJobForm(FlaskForm):
    team_leader = StringField('Главный', validators=[DataRequired()])
    jod = StringField('Описание', validators=[DataRequired()])
    work_size = StringField('Количество часов для выполнения', validators=[DataRequired()])
    collaborators = StringField('Сотрудники (перечисление через запятую)', validators=[DataRequired()])
    is_finished = BooleanField('Закончена работа', validators=[DataRequired()])
    add = SubmitField('Добавить')


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
    db_session.global_init('db/blogs.sqlite')
    session = db_session.create_session()
    return render_template('prof.html', peoples=session.query(users.User), jobs=session.query(jobs.Jobs))


@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    form = AddJobForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        job = jobs.Jobs(
            team_leader=form.team_leader.data,
            jod=form.jod.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            is_finished=form.is_finished.data
        )
        session.add(job)
        session.commit()
        return redirect('/')
    return render_template('add_job.html', form=form)


if __name__ == '__main__':
    db_session.global_init('db/blogs.sqlite')
    app.run()
# http://127.0.0.1:5000/add_job
