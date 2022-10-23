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


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        new_user = UserLogin(email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
        except Exception as ex:
            print(ex)
            return "DB ERROR"
    else:
        return render_template("login.html")


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':

        username = 'username1'  # request.form['username']
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
