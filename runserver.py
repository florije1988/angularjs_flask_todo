# -*- coding: utf-8 -*-

__author__ = 'florije'

from flask import Flask, send_file, Blueprint
from flask.ext.restful import Api, Resource, reqparse
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.marshmallow import Marshmallow

app = Flask(__name__)

app.debug = True
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///demo.db"

db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)


@app.route('/')
def hello_world():
    # return 'Hello World!'
    return send_file('templates/index.html'), 200


class ApiBaseError(Exception):
    '''
    基异常类。
    '''

    status_code = 200
    code = 0

    def __init__(self, message, code, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message if message else ''
        self.code = code if code else self.code
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload


class InvalidAPIUsage(ApiBaseError):
    code = 10000

    def __init__(self, message=None, code=None, status_code=None, payload=None):
        super(InvalidAPIUsage, self).__init__(message=message, code=code, status_code=status_code, payload=payload)


class ThingModel(db.Model):
    __tablename__ = 'things'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(length=20), nullable=True, unique=False, default='')


class TodoSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'content')


class ThingsHandler(Resource):
    def get(self):
        # return {'names': [{'content': 'xiaoqigui'}, {'content': 'hahaha'}]}
        res_task = ThingModel.query.all()
        task_ma = TodoSchema().dump(res_task, many=True)
        if task_ma.errors:
            raise InvalidAPIUsage(message=task_ma.errors)
        return task_ma.data


app_todo_blueprint = Blueprint('app_todo', __name__)
api_todo = Api(app_todo_blueprint, catch_all_404s=True)
api_todo.add_resource(ThingsHandler, '/things')

app.register_blueprint(app_todo_blueprint, )


manager = Manager(app)


@manager.command
def create_db():
    db.create_all()

if __name__ == '__main__':
    manager.run()  # runserver -p 5000 -h 127.0.0.1
