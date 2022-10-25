import hashlib
import random
from datetime import datetime

from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

from itsdangerous import URLSafeTimedSerializer, SignatureExpired

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'NAZVANIE_KOMANDI_ZVEZDOCHKA'
app.config['MAIL_SERVER'] = 'smtp.mail.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'artem_konovalov2005@mail.ru'
app.config['MAIL_DEFAULT_SENDER'] = 'artem_konovalov2005@mail.ru'  # закинуть в переменные среды
app.config['MAIL_PASSWORD'] = '5vytGAzLURLzswzvg3S1'

db = SQLAlchemy(app)

mail = Mail(app)

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])


class UserLogin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    email_confirm = db.Column(db.String(30), default='False', nullable=False) # переделать стринг в бул или инт
    phone = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return '<UserLogin %r>' % self.id


class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return '<UserData %r>' % self.id


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(48), nullable=False)
    refresh_token = db.Column(db.String(48), nullable=False)
    type = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.String, default=datetime.utcnow(), nullable=False)

    def __repr__(self):
        return '<Session %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
        return session_start(username=username, password=password, grant_type='password')

    else:
        return render_template("login.html")


@app.route('/', methods=['GET'])
def session_start(username, password, grant_type):
    current_user = UserLogin.query.filter_by(username=username).first()

    if current_user:
        if current_user.password == password:
            new_session = Session(access_token='access_token',
                                  refresh_token='refresh_token',
                                  type=grant_type,
                                  user_id=current_user.id)
            try:
                db.session.add(new_session)
                db.session.commit()
            except Exception:
                return "DB ERROR"

            return redirect(f'/user/{username}')

        else:
            flash('Неправильный пароль')

    else:
        flash('Пользователь с таким именем не найден')
    return render_template('login.html')


@app.route('/', methods=['GET'])
def session_refresh(grant_type, refresh_token):
    session = Session.query.get_or_404(refresh_token)
    user_id = session.user_id
    new_access_token = 'new_access_token'
    session.access_token = new_access_token


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
        email = request.form['email']
        phone = request.form['phone']

        first_name = request.form['first_name']
        last_name = request.form['last_name']

        if UserLogin.query.filter(UserLogin.username == username).all():
            flash('Этот никнейм недоступен')
            return render_template("registration.html")

        elif UserLogin.query.filter(UserLogin.email == email).all():
            flash('Эта почта недоступна')
            return render_template("registration.html")
        else:
            new_userLogin = UserLogin(username=username, password=password, email=email, phone=phone)
            new_userData = UserData(first_name=first_name, last_name=last_name)
            try:
                db.session.add(new_userLogin)
                db.session.commit()

                db.session.add(new_userData)
                db.session.commit()

            except Exception as ex:
                print(ex)
                return "DB ERROR"
            token = s.dumps(email, salt='email-confirm')
            msg = Message('Confirm Email', recipients=[email])
            link = url_for('confirm_email', token=token, _external=True)
            msg.body = f'Чтобы подтвердить вашу почту к аккуанту {username}' \
                       f' перейдите по ссылке:\n{link}'
            mail.send(msg)
            return render_template("info.html", info=f'Вам отправлено письмо для подтверждения почты {email}\nСсылка действует 1 час')

    else:
        return render_template("registration.html")


@app.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        current_user = UserLogin.query.filter(UserLogin.email == email).first()
        if current_user:
            if current_user.email_confirm == 'True':
                token = s.dumps(email, salt='email-confirm')
                msg = Message('Reset password', recipients=[email])
                link = url_for('reset_password_success', token=token, _external=True)
                msg.body = f'Чтобы сменить пароль перейдите по ссылке:\n{link}'
                mail.send(msg)

            else:
                flash('Почта не подтверждена')
                return render_template("reset_password.html")
        else:
            flash('Почта не существует')
            return render_template("reset_password.html")

        return render_template("info.html", info='На вашу почту отправлена ссылка для смены пароля.\nСсылка действует 1 час')
    else:
        return render_template("reset_password.html")


@app.route('/reset_password_success/<token>')
def reset_password_success(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
        current_user = UserLogin.query.filter(UserLogin.email == email).first()

        new_password = ''

        for x in range(16):
            new_password = new_password + random.choice(list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ'))

        new_password_hash = hashlib.sha256(new_password.encode('utf-8')).hexdigest()

        current_user.password = new_password_hash
        try:
            db.session.commit()
        except Exception:
            return 'DB_ERROR'

        return render_template("info.html", info=f'Пароль для аккаунта {current_user.username} изменен\nВаш новый пароль: {new_password} ')
    except SignatureExpired:
        return render_template("info.html", info='Время действия токена превышено')


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=60)
        current_user = UserLogin.query.filter(UserLogin.email == email).first()
        current_user.email_confirm = 'True'
        try:
            db.session.commit()
        except Exception:
            return 'DB_ERROR'
        return render_template("info.html", info=f'Вы успешно зарегистрировались\nВаш никнейм {current_user.username} ')
    except SignatureExpired:
        return render_template("info.html", info='Время действия токена превышено')




@app.route('/user/<string:email>')
def user(email):
    return f"page {email} "




# dashboard




class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)

    def __repr__(self):
        return '<Course %r>' % self.id


class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    date = db.Column(db.String, nullable=False)
    course_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Lecture %r>' % self.id


@app.route('/homepage')
def homepage():
    return render_template("homepage.html")


@app.route('/homepage/new_course', methods=['POST', 'GET'])
def new_course():
    title = request.form['title']
    description = request.form['description']
    course = Course(title=title, description=description)
    try:
        db.session.add(course)
        db.session.commit()
    except Exception:
        return 'DB_ERROR'

    return render_template("new_course.html")


@app.route('/homepage/new_lecture', methods=['POST', 'GET'])
def new_lecture():
    title = request.form['title']
    description = request.form['description']
    date = request.form['date']
    course_id = request.form['course_id']


    lecture = Lecture(title=title, description=description, date=date, course_id=course_id)
    try:
        db.session.add(lecture)
        db.session.commit()
    except Exception:
        return 'DB_ERROR'

    return render_template("new_lecture.html")



if __name__ == '__main__':
    app.run(debug=True)
