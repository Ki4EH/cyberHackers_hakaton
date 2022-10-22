from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'users {self.id}'


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        db.create_all()
        print('qw')
        name = ''
        surname = ''

        new_user = User(name=name, surname=surname)

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
