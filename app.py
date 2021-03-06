from flask import Flask, request, make_response
from lib.qnyflib import qnyf
from flask_cors import *
from lib.model import *


app = Flask(__name__)
CORS(app, supports_credentials=True)


def check(yxdm, name, number, passwd):
    try:
        stu = qnyf(yxdm, number, name, passwd)
        return True
    except Exception as e:
        return False


def resp(code=200, msg="", data=""):
    if code == 500:
        msg = "服务器出现问题"
    return make_response({
        "code": code,
        "msg": msg,
        "data": data
    }, 200)


@app.route('/hello', methods=["GET"])
def hello():
    return make_response({
        "code": 200,
        "msg": "hello",
        "data": ""
    }, 200)


@app.route('/api/dakacount', methods=["GET"])
def dakacount():
    return resp(200, '', str(len(daka.select())))


@app.route('/api/query', methods=["GET"])
def query():
    try:
        args = request.args

        yxdm = args['yxdm']
        number = args['num'].strip()

        if not number or not yxdm:
            return resp(400, "字段不能为空")
        if not daka.select().where((yxdm == daka.yxdm) & (number == daka.number)).exists():
            return resp(400, "用户还未在数据库中")
        user = daka.get((daka.number == number))
        if not check(yxdm, user.name, number, user.passwd):
            return resp(400, user.name + '打卡状态不正常,请更新账号密码')
        return resp(200, user.name + '打卡状态正常, 打卡位置为: ' + user.loc)

    except Exception as e:
        print(e)
        return resp(500)


@app.route('/api/stop', methods=["GET"])
def stophan():
    try:
        args = request.args
        yxdm = args['yxdm'].strip()
        number = args['num'].strip()

        if not daka.select().where((yxdm == daka.yxdm) & (number == daka.number)).exists():
            return resp(400, '用户不存在或者密码学号有误，请检查')
        daka.delete().where(number == daka.number).execute()
        return resp(200, "删除成功")
    except Exception as e:
        print(e)
        return resp(500)


@app.route('/api/submit', methods=["GET"])
def add():

    args = request.args

    try:
        yxdm = args['yxdm'].strip()
        name = args['name'].strip()
        number = args['num'].strip()
        passwd = args['passwd'].strip()
        loc = args['address'].strip()

        if not name or not passwd or not number:
            return resp(400, "字段不能为空")

        if not check(yxdm, name, number, passwd):
            return resp(400, "学号或者密码有误，请检查")

        if daka.select().where(daka.number == number).exists():
            user = daka.get(daka.number == number)
            user.name = name
            user.passwd = passwd
            user.loc = loc
            user.save()
            return resp(200, "修改成功")
        else:
            daka.create(yxdm=yxdm, name=name, number=number,
                        passwd=passwd, loc='中国四川省成都市西华大学' if not loc else loc)
            return resp(200, "添加成功")

    except Exception as e:
        print(e)
        return resp(500)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=4000, use_reloader=True)
