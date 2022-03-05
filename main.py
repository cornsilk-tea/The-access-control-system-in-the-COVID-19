import subprocess
from flask import Flask, request, session, render_template, redirect, url_for, send_file, send_from_directory, jsonify
import flask
from werkzeug.utils import secure_filename
from pymysql import cursors
from mysql.connector import cursor
import identify, os
import json, datetime
import pymysql
import sys
import time
import datetime
import kakaomsg as kmsg
from models import stu_temp_data
from pathlib import Path
# from flask_ngrok import run_with_ngrok

# Flask 객체 인스턴스 생성
app = Flask(__name__)
# run_with_ngrok(app)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['JSON_AS_ASCII'] = False


# 파일업로드 함수
@app.route('/fileupload', methods=['POST'])
def upload_file():
    file = request.files['userfile']
    file.save('./regi_user/'+ file.filename)
    return "success"

# 보내온 사진을 ./에 저장한 뒤
# identify.verify함수로 수행한 뒤
# 결과값을 딕셔너리타입으로 저장하여 반환
@app.route('/verify', methods=['POST', 'GET'])
def verify():
    # 사진 파일 받기
    file = request.files['src']
    file.save('./'+ file.filename)
    # print(file.filename)

    # temp 저장
    temp = request.form.get('temp')

    # verify 돌리기
    res = identify.verify('./'+ file.filename, "Facenet", temp)
    if len(res) <= 1:
        os.remove('./'+ file.filename)
        return res
    stu_num = res['stu_num']
    print(res)

    # 카톡으로 알림보내기
    if float(temp) < float(38.5):
        print(temp)
        msg = '{}의 출입이 확인되었습니다.'.format(stu_num)
    else:
        print(temp)
        msg = '#경고# {}의 온도가 {}입니다.'.format(stu_num, temp)
    kmsg.send_msg(msg)

    # db에 측정한 온도와 학번을 시간순으로 작성
    db = pymysql.connect(host='127.0.0.1', user='root',
    password='zkfelqlxkww01', db='capstonedb', charset='utf8')
    cursors = db.cursor(pymysql.cursors.DictCursor)
    cursors = db.cursor()

    sql_data = [stu_num, temp]
    sql = "INSERT INTO `daytempdb` (`stu_num`, `temp`) VALUES ({},{});".format(stu_num, temp)

    cursors.execute(sql)
    db.commit()
    value = cursors.fetchall()
    db.close()

    # 보내진 사진 삭제
    os.remove('./'+ file.filename)
    return res

@app.route('/dbtest', methods=['GET'])
def dbtest():
    def myconverter(o): # https://code-maven.com/serialize-datetime-object-as-json-in-python
        if isinstance(o, datetime.datetime):
            return o.__str__()
    db = pymysql.connect(host='127.0.0.1', user='root',
    password='zkfelqlxkww01', db='capstonedb', charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    # cursors = db.cursor(pymysql.cursors.DictCursor)
    cursors = db.cursor()
    # input ex) {'stu_num' : 20150597}
    stu_num = request.args['stu_num']
    sql = "SELECT * FROM daytempdb WHERE stu_num = '{}'".format(stu_num)
    cursors.execute(sql)
    res_dict = cursors.fetchall()
    res = json.dumps(res_dict, default = myconverter, indent=2)
    return res


# 웹, 애플리케이션과 연동된 회원가입과 로그인 함수
@app.route('/login', methods = ['GET', 'POST'])
def mydb():
    msg_received = flask.request.get_json()
    msg_subject = msg_received["subject"]

    if msg_subject == "register":
        return register(msg_received)
    elif msg_subject == "login":
        return login(msg_received)
    else:
        return "Invalid request."

# 앱에서 회원가입
def register(msg_received):
    name = msg_received["name"]
    dept = msg_received["dept"]   #test
    id = msg_received["id"]
    password = msg_received["password"]
    
    # db 내부 정보와 비교해서 중복 id가 있는지 확인
    select_query = "SELECT * FROM user WHERE id = " + "'" + id + "'"
    db_cursor.execute(select_query)
    records = db_cursor.fetchall()
    if len(records) != 0:
        return "Another user used the id. Please chose another id."
    
    # 회원가입시 입력한 정보를 user db에 작성
    insert_query = "INSERT INTO user (name, dept, id, password) VALUES (%s, %s, %s, MD5(%s))"
    insert_values = (name, dept, id, password)
    try:
        db_cursor.execute(insert_query, insert_values)
        mydb.commit()
        return "success"
    except Exception as e:
        print("Error while inserting the new record :", repr(e))
        return "failure"

# 로그인
def login(msg_received):
    id = msg_received["id"]
    password = msg_received["password"]

    # db 내부 정보와 비교해서 password의 일치, 불일치를 확인
    select_query = "SELECT name, dept FROM user WHERE id = " + "'" + id + "' and password = " + "MD5('" + password + "')"
    db_cursor.execute(select_query)
    records = db_cursor.fetchall()

    if len(records) == 0:
        return "failure"
    else:
        return "success"
try:
    mydb = pymysql.connect(host="127.0.0.1", user="root", password="zkfelqlxkww01", database="capstonedb")
except:
    sys.exit("Error connecting to the database. Please check your inputs.")
db_cursor = mydb.cursor()

# 웹 메인화면
@app.route('/', methods=['GET', 'POST'])
def main():
    error = None

    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']

        sql = "SELECT * FROM user WHERE id = %s AND password = MD5(%s)"
        value = (id, password)
        db_cursor.execute("set names utf8")
        db_cursor.execute(sql, value)

        data = db_cursor.fetchall()

        for row in data:
            data = row[0]

        if data:
            if (id == 'admin' and password == 'admin'):
                session['login_admin'] = id
                return redirect(url_for('admin'))

            session['login_user'] = id
            return redirect(url_for('home'))
        else:
            error = 'invalid input data detected !'
    return render_template('main.html', error=error)

# 회원가입 html
@app.route('/register.html', methods=['GET', 'POST'])
def register_web():
    error = None
    if request.method == 'POST':
        id = request.form['regi_id']
        password = request.form['regi_password']
        name = request.form['regi_name']
        dept = request.form['regi_dept']
        os.mkdir('img_data/'+id)
        print(Path('img_data/'+id).resolve())
        UPLOAD_FOLDER = Path('img_data/'+id).resolve()   # 저장할 경로 + 파일명
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

        sql = "INSERT INTO user VALUES ('%s', MD5(%s), '%s', '%s', NOW())" % (id, password, name, dept)
        db_cursor.execute(sql)

        data = db_cursor.fetchall()

        if not data:
            mydb.commit()
            file = request.files['file']
            # 저장할 경로 + 파일명
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('main'))
        else:
            mydb.rollback()
            return "Register Failed"

        db_cursor.close()
        mydb.close()
    return render_template('register.html', error=error)

# 웹 메인화면
@app.route('/home.html', methods=['GET', 'POST'])
def home():
    error = None
    id = session['login_user']

    return render_template('home.html', error=error, name=id)


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('login_user', None)
    return redirect('/')


@app.route('/dpdata.html', methods=['GET', 'POST'])
def dpdata():
    id = session['login_user']
    return render_template('dpdata.html', name=id)


#관리자 온도 확인 페이지: 회원별 전체 온도 확인
@app.route('/admin', methods = ['GET', 'POST'])
def admin():
    id = session['login_admin']
    return render_template('admin.html', name=id)


#관리자 페이지 json받아오기
@app.route('/admin/<stu_num>', methods = ['GET', 'POST'])
def adm_pf_temp(stu_num):
    data = stu_temp_data.get_all(stu_num)
    return jsonify(data)

@app.route('/admin_data.html', methods=['GET', 'POST'])
def admin_dpdata():
    id = session['login_admin']
    return render_template('admin_data.html', name=id)

# models.py에서 수집한 측정한 온도, 학번, 시간을 최신순으로 json형식으로 반환
@app.route('/test/<stu_num>', methods = ['GET', 'POST'])
def test(stu_num):
    data = stu_temp_data.get_all(stu_num)
    return jsonify(data)

# 등록되지 않은 사람들의 사진 목록
@app.route('/fileList')
def download_page():
    dir_path = './regi_user/'
    files = os.listdir(dir_path)
    return render_template('download.html', files=files)

#검색 사진 다운로드
@app.route('/fileDown', methods=['GET', 'POST'])
def download_page1():
    file_dir = "./regi_user/"
    return send_file(file_dir + request.form['file'], attachment_filename=request.form['file'], as_attachment=True)

#사진을 눌러서 다운로드
@app.route('/get-files/<path:path>',methods = ['GET','POST'])
def get_files(path):

        return send_from_directory("./regi_user/", path, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug = True)