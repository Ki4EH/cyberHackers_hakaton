from flask import Flask, render_template, url_for, request, redirect
import sqlite3

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id
# @staticmethod
# def add_new_user(name, password):
#     connection = sqlite3.connect(f'data/db/users.db')
#     cursor = connection.cursor()
#
#     cursor.execute(
#         """CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY, name STRING, password STRING)""")
#     connection.commit()
#
#     new_user = [name, password]
#     cursor.execute(f"SELECT * FROM users WHERE name = {name}")
#
#     if cursor.fetchone() is not None:
#         cursor.execute(f"DELETE FROM users WHERE name = {name}")
#         connection.commit()
#     cursor.execute("INSERT INTO users(name, password) values(?, ?);", new_user)
#     connection.commit()


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        new_user = User(email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
        except Exception as ex:
            print(ex)
            return "DB ERROR"
    else:
        return render_template("index.html")


@app.route('/user/<string:name>/<int:id_>')
def user(name, id_):
    return f"page {name} with id {id_}"


if __name__ == '__main__':
    app.run(debug=True)
