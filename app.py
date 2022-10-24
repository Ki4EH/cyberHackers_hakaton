from datetime import datetime

from flask import Flask, render_template, url_for, request, redirect
import hashlib

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class UserLogin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=True)
    phone = db.Column(db.String(30), nullable=True)

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
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return '<Session %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = 'username123'  # request.form['username']
        password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
        return session_start(username=username, password=password, grant_type='password')

    else:
        return render_template("login.html")


@app.route('/', methods=['GET'])
def session_start(username, password, grant_type):
    for id_, un, pw in db.session.query(UserLogin.id, UserLogin.username, UserLogin.password):
        if un == username:
            # userr = UserLogin.query.get(id_)
            # print(userr.username)
            if pw == password:
                new_session = Session(access_token='access_token', refresh_token='refresh_token', type=grant_type, user_id=id_)
                db.session.add(new_session)
                db.session.commit()
                return redirect(f'/user/{username}')
            else:
                return 'ERROR 404 incorrect_password'
    return 'ERROR 404 User not found'


@app.route('/', methods=['GET'])
def session_refresh(grant_type, refresh_token):
    session = Session.query.get_or_404(refresh_token)
    user_id = session.user_id
    new_access_token = 'new_access_token'
    session.access_token = new_access_token




@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':

        username = 'username123'  # request.form['username']
        password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
        email = request.form['email']
        phone = ''  # request.form['phone']

        first_name = request.form['first_name']
        last_name = request.form['last_name']

        if len(UserLogin.query.filter(UserLogin.username == username).all()) != 0:
            return 'Error 200 login_not_available'

        if len(UserLogin.query.filter(UserLogin.email == email).all()) != 0:
            return 'Error 200 mail_not_available'

        new_userLogin = UserLogin(username=username, password=password, email=email, phone=phone)
        new_userData = UserData(first_name=first_name, last_name=last_name)
        try:
            db.session.add(new_userLogin)
            db.session.commit()

            db.session.add(new_userData)
            db.session.commit()

            return redirect(f'/user/{username}')
        except Exception as ex:
            print(ex)
            return "DB ERROR"

    else:
        return render_template("registration.html")


@app.route('/user/<string:email>')
def user(email):
    return f"page {email}"


if __name__ == '__main__':
    app.run(debug=True)
