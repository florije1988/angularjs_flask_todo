# -*- coding: utf-8 -*-
__author__ = 'florije'

from flask import Flask, send_file, Blueprint, request
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
def index():
    # return 'Hello World!'
    return send_file('templates/index.html'), 200


class ApiBaseError(Exception):
    """
    异常基类。
    """

    status_code = 200
    code = 0

    def __init__(self, msg, code, status_code=None, data=None):
        Exception.__init__(self)
        self.msg = msg if msg else ''
        self.code = code if code else self.code
        if status_code is not None:
            self.status_code = status_code
        self.data = data


class InvalidAPIUsage(ApiBaseError):
    """
    非法接口使用异常
    """
    code = 10000

    def __init__(self, msg=None, code=None, status_code=None, data=None):
        super(InvalidAPIUsage, self).__init__(msg=msg, code=code, status_code=status_code, data=data)


class ThingModel(db.Model):
    """
    数据库Thing模型
    """
    __tablename__ = 'things'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(length=20), nullable=True, unique=False, default='')


class TodoSchema(ma.Schema):
    """
    数据库返回模型
    """
    class Meta:
        # Fields to expose
        fields = ('id', 'content')


class CusApi(Api):
    """
    自定义接口，主要是返回异常类。
    """
    def handle_error(self, error):
        code = getattr(error, 'code', 500)
        if issubclass(error.__class__, ApiBaseError):
            response = {
                'code': code,
                'msg': 'Server raise error: %s' % (error.msg,),
                'data': {}
            }
            return self.make_response(response, 200)
        if code:
            response = {
                'code': -1,
                'msg': 'Status_code: %s ,Server raise error: %s' % (code, error),
                'data': {}
            }
            return self.make_response(response, 200)
        return super(CusApi, self).handle_error(error)


class BaseHandler(Resource):
    """
    处理请求基类
    """
    @staticmethod
    def json_output(code=0, msg='success', data=None):
        return JSONResponse(code=code, msg=msg, data=data).to_json()


class JSONResponse(object):
    """
    返回值格式化类
    """
    def __init__(self, code=0, msg='success', data=None):
        self.code = code
        self.msg = msg
        self.data = data

    def to_json(self):
        # return simplejson.dumps(self.__to_dict(), ensure_ascii=False)
        res_dict = dict(code=self.code, msg=self.msg)
        if self.data:
            res_dict['data'] = self.data
        return res_dict


class ThingsHandler(BaseHandler):
    """
    Thing处理
    """
    def get(self):
        # return {'names': [{'content': 'xiaoqigui'}, {'content': 'hahaha'}]}
        res_task = ThingModel.query.all()
        task_ma = TodoSchema().dump(res_task, many=True)
        if task_ma.errors:
            raise InvalidAPIUsage(msg=task_ma.errors)
        return self.json_output(data=task_ma.data)

    def post(self):
        if not request.data:
            raise InvalidAPIUsage(msg='Request data type is error!')

        parser = reqparse.RequestParser()
        parser.add_argument('content', type=unicode, required=True, help="content cannot be blank!", location='json')
        args = parser.parse_args()
        thing = ThingModel(content=args.get('content'))
        try:
            db.session.add(thing)
            db.session.commit()
            return self.json_output(data=TodoSchema().dump(thing).data)
        except Exception as e:
            raise InvalidAPIUsage(msg=e.message)


app_todo_blueprint = Blueprint('app_todo', __name__)
api_todo = CusApi(app_todo_blueprint, catch_all_404s=True)
api_todo.add_resource(ThingsHandler, '/things')

app.register_blueprint(app_todo_blueprint, )

manager = Manager(app)


@manager.command
def create_db():
    """
    初始化数据库
    :return:
    """
    db.create_all()


if __name__ == '__main__':
    manager.run()  # runserver -p 5000 -h 127.0.0.1