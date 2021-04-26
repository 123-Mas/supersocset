from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask import Flask, render_template, redirect, request, make_response, url_for
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class SendForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    text = StringField('Текст', validators=[DataRequired()])
    submit = SubmitField('Написать')


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    email = StringField('Email')
    submit = SubmitField('Зарегистрироваться')


class WallCreate(FlaskForm):
    text = StringField('Текст', validators=[DataRequired()])
    submit = SubmitField('Разместить')


class Log(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    submit = SubmitField('Посмотреть')


class AdminLog(FlaskForm):
    name = StringField('Имя первого', validators=[DataRequired()])
    name1 = StringField('Имя второго', validators=[DataRequired()])
    submit = SubmitField('Посмотреть')


class AdminWallCreate(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    text = StringField('Текст', validators=[DataRequired()])
    submit = SubmitField('Разместить')


def dumb(dat):
    with open('static/all.json') as Wall:
        data = json.loads(Wall.read())
        data['all'].append(dat)
    with open('static/all.json', 'w') as Wall:
        json.dump(data, Wall)
    #print(data)


@app.route('/')
def contact():
    return render_template('start.html')


@app.route('/direct', methods=['GET', 'POST'])
def direct():
    with open('static/Users.json') as Users:
        data = json.loads(Users.read())
    name = request.cookies.get('Name')
    if name is None:
        return 'Ошибка. Вход не выполнен.'
    if data[name][2] is True:
        form = AdminLog()
    else:
        form = Log()
    if form.validate_on_submit():
        if data[name][2] is True:
            name = form.name1.data
        name1 = form.name.data
        with open('static/direct.json') as Direct:
            data = json.loads(Direct.read())
        name, name1 = sorted([name, name1])
        if f'{name}, {name1}' not in data.keys():
            data[f'{name}, {name1}'] = []
        print(data[f'{name}, {name1}'])
        return render_template('wall_create.html', news=data[f'{name}, {name1}'])
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/write', methods=['GET', 'POST'])
def write():
    form = SendForm()
    with open('static/direct.json') as Direct:
        data = json.loads(Direct.read())
    name = request.cookies.get('Name')
    if name is None:
        return 'Ошибка. Вход не выполнен.'
    nam = name
    if form.validate_on_submit():
        name1 = form.name.data
        text = form.text.data
        name, name1 = sorted([name, name1])
        if f'{name}, {name1}' not in data.keys():
            data[f'{name}, {name1}'] = []
        data[f'{name}, {name1}'].append([nam, text, str(datetime.now())])
        with open('static/direct.json', 'w') as Direct:
            json.dump(data, Direct)
        return redirect('/direct')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/log', methods=['GET', 'POST'])
def log():
    form = Log()
    if form.validate_on_submit():
        with open('static/Wall.json') as Wall:
            data = json.loads(Wall.read())
        if form.name.data not in data:
            return 'Ошибка. Такого пользователя не существует'
        for i in data[form.name.data]:
            i.insert(0, form.name.data)
        print(data[form.name.data])
        if form.name.data in data.keys():
            return render_template('wall_create.html', news=data[form.name.data])
        return 'Нету('
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/create_new', methods=['GET', 'POST'])
def wall_create():
    with open('static/Users.json') as Users:
        data = json.loads(Users.read())
    name = request.cookies.get('Name')
    if name is None:
        return 'Ошибка. Вход не выполнен.'
    if data[name][2] is True:
        form = AdminWallCreate()
    else:
        form = WallCreate()
    if form.validate_on_submit():
        time = str(datetime.now())
        if data[name][2] is True:
            name = form.name.data
        text = form.text.data
        if len(text) > 300:
            return 'Ошибка. Слишком много символов. Лимит - 300'
        with open('static/Wall.json') as Wall:
            data = json.loads(Wall.read())
        if name in data.keys():
            data[name].append([text, time])
        else:
            data[name] = [[text, time]]
        #print(data)
        with open('static/Wall.json', 'w') as Wall:
            json.dump(data, Wall)
        dumb([name, text, time])
        return redirect('/wall')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with open('static/Users.json') as Users:
            data = json.loads(Users.read())
        #print(data)
        if form.username.data not in data.keys() or form.password.data not in data[form.username.data]:
            return 'Ошибка. Такого аккаунта с таким паролем не существует'
        res = make_response("<p><a href='http://127.0.0.1:8080/wall'>Успешно! Нажмите, чтобы зайти на стену</a></p> ")
        res.set_cookie('Name', form.username.data, max_age=60 * 60 * 24 * 365 * 2)
        return res
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        with open('static/Users.json') as Users:
            data = json.loads(Users.read())
        if form.username.data in data.keys():
            return 'Ошибка. Такое имя уже существует'
        #print([data[i][1] for i in data])
        if form.email.data in [data[i][1] for i in data]:
            return 'Ошибка. На такой email уже зарегистрирован аккаунт'
        data[form.username.data] = [form.password.data, form.email.data, False]
        with open('static/Users.json', 'w') as Users:
            json.dump(data, Users)
        #print(data)
        return redirect('/login')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/wall')
def wall():
    with open('static/all.json') as Wall:
        data = json.loads(Wall.read())
        #print(data)
        data = [i for i in data['all']][::-1]
    print(data)
    name = request.cookies.get('Name')
    return render_template('wall_create.html', news=data)




if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')