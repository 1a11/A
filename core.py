from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask_socketio import SocketIO

import random
import uuid
import pyotp
import qrcode
import datetime
import json
import importlib
import psutil
import sentry_sdk

import propperties
import database
import heartbeat
import code_handler
sentry_sdk.init("https://0758363ccc2f4f78aa40360e8fd27a65@o335594.ingest.sentry.io/5211269")

def get_cpuload():
    """
        Получаем время работы компьютера, загруженность процессора, видеокарты,
        оперативной памяти.
    """
    average = 0
    for x in range(3):
        average += float(psutil.cpu_percent(interval=1))
    return(average/3)

def check_status():
    db = database.db('main.db')
    name = db.get_user_name({'cid':str(request.cookies.get('sessionID'))})
    status = db.get_user_status(name)
    return status

def run():
    app = Flask(__name__)
    socketio = SocketIO(app)
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    @app.errorhandler(404)
    def http_error_handler(error):
        return render_template('e404.html')

    @app.route('/')
    def i_am_idiot():
        resp = redirect("/login")
        return(resp)

    @app.route('/login', methods=['POST', 'GET'])
    def main_page():

        with open("./config.json", "r", encoding='utf8') as read_file:
            data = json.load(read_file)

        if not data['shf'] == 'Yes':
            if request.method == 'POST' and request.form.get('password'):
                    login = request.form.get('login')
                    password = request.form.get('password')
                    code = str(request.form.get('code'))


                    db = database.db('main.db')
                    if db.check_user({'login':login}):
                        if db.get_user_password(login) == password:
                            if not propperties.OTP:
                                cid = (str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())).replace('-','')
                                db.create_auth({'cid':cid,'login':login})

                                resp = redirect("/dashboard")
                                resp.set_cookie('sessionID', cid, max_age = 60*60*24*365)
                                return resp
                            totp = pyotp.TOTP(db.get_user_gaseed(login)[0][0])
                            otp = totp.now() == code
                            #print(totp.now())
                            if otp:


                                cid = (str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())).replace('-','')
                                db.create_auth({'cid':cid,'login':login})

                                resp = redirect("/dashboard")
                                resp.set_cookie('sessionID', cid, max_age = 60*60*24*365)
                                return resp
                            else:
                                resp = redirect("/login")
                                return resp
                        else:
                            resp = redirect("/login")
                            return resp
                    else:
                        resp = redirect("/login")
                        return resp

            if not request.cookies.get('coockieid'):
                resp = redirect("/setid")
                resp.set_cookie('coockieid', str(uuid.uuid4()).split('-')[0], max_age = 60*60*24*365)
                return(resp)
            elif request.cookies.get('sessionID'):
                resp = redirect("/dashboard")
                return resp
            else:
                return render_template('login.html',projectname=propperties.PROJECTNAME,coockieid=str(request.cookies.get('coockieid')),image="bg{}.png".format(random.randint(1, 6)))
        else:
            return render_template('shf.html',projectname=propperties.PROJECTNAME,coockieid=str(request.cookies.get('coockieid')),image="bg{}.png".format(random.randint(1, 6)))
    @app.route('/setid')
    def setid():
        if not request.cookies.get('coockieid'):
            resp = redirect("/setid")
            resp.set_cookie('coockieid', str(uuid.uuid4()).split('-')[0], max_age = 60*60*24*365)
            return(resp)
        else:
            #return('ID set. Redirect in 5 sec')
            return('<head><meta http-equiv="refresh" content="2; url=/login"/></head>ID set. Redirect in 5 sec')
        return render_template('login.html',projectname='Astra',coockieid=request.cookies.get('coockieid'))

    @app.route('/dashboard', methods=['POST', 'GET'])
    def dashboard():
        with open("./config.json", "r", encoding='utf8') as read_file:
            data = json.load(read_file)
        db = database.db('main.db')
        if request.method == 'POST':
            if db.check_coockie({'cid':request.cookies.get('sessionID')}):
                username = db.get_user_name({'cid':request.cookies.get('sessionID')})
                status = db.get_user_status(username)
                if status == 'Admin':
                    print('Umpa-Lumpa')
                    with open("./config.json", "r", encoding='utf8') as read_file:
                        data = json.load(read_file)
                    if data['shf'] == 'No':
                        print('Turning SHF mode on')
                        data['shf'] = 'Yes'
                        with open('config.json', 'w') as outfile:
                            json.dump(data, outfile, indent=4)
                    else:
                        data['shf'] = 'No'
                        print('Turning SHF mode off')
                        with open('config.json', 'w') as outfile:
                            json.dump(data, outfile, indent=4)
                else:
                    resp = redirect('/dashboard')
                    return resp

        if not request.cookies.get('sessionID'):


            resp = redirect("/login")
            return(resp)
        if db.check_coockie({'cid':request.cookies.get('sessionID')}):
            username = db.get_user_name({'cid':request.cookies.get('sessionID')})
            status = db.get_user_status(username)
            if status == 'Admin' or status == 'User':
                if data['shf'] == 'Yes':
                    return render_template('index.html',projectname='Astra',coockieid=request.cookies.get('coockieid'), shf_status ="Выключить")
                else:
                    return render_template('index.html',projectname='Astra',coockieid=request.cookies.get('coockieid'), shf_status ="Включить")
            else:
                return "You can't view this page. Your status is {} but you need to have Admin or User".format(status)

        #resp = redirect("/login")
        return 'Error'
    @app.route('/logout', methods=['POST', 'GET'])
    def logout():
        resp = redirect("/login")
        resp.set_cookie('sessionID', '', max_age = 60*60*24*365)
        return resp


    @app.route('/sysinfo', methods=['POST', 'GET'])
    def sysinfo():
        with open("./config.json", "r", encoding='utf8') as read_file:
            data = json.load(read_file)
        sysinfo = heartbeat.get_statistics()
        if sysinfo['cuda'] == 'Not instaled':
            return render_template('sysinfo.html',projectname='Astra',coockieid=request.cookies.get('coockieid'),\
                                   pc_name=data['pc_name'],pc_desctiption=data['pc_desctiption'],pc_cpu_load=(str(sysinfo['cpu_load'])+'%'),\
                                   pc_ram_free=str(round(sysinfo['ram']['available']/1024/1024/1024,2))+'GB',pc_ram_used=str(sysinfo['ram']['percent'])+'%',pc_speed_upload=str(round(sysinfo['network_latency']['upload']/1024/1024,2))+'mbit/s',\
                                   pc_speed_download=str(round(sysinfo['network_latency']['download']/1024/1024,2))+'mbit/s',pc_speed_ping=sysinfo['network_latency']['ping'],\
                                   pc_cuda_status = '❌')
        else:
            return render_template('sysinfo.html',projectname='Astra',coockieid=request.cookies.get('coockieid'),\
                                   pc_name=data['pc_name'],pc_desctiption=data['pc_desctiption'],pc_cpu_load=(str(sysinfo['cpu_load'])+'%'),\
                                   pc_ram_free=str(round(sysinfo['ram']['available']/1024/1024/1024,2))+'GB',pc_ram_used=str(sysinfo['ram']['percent'])+'%',pc_speed_upload=str(round(sysinfo['network_latency']['upload']/1024/1024,2))+'mbit/s',\
                                   pc_speed_download=str(round(sysinfo['network_latency']['download']/1024/1024,2))+'mbit/s', pc_speed_ping=sysinfo['network_latency']['ping'],\
                                   pc_cuda_status = '✔️')


    @app.route('/dbmanager', methods=['POST', 'GET'])
    def dbm():
        if check_status() == 'Admin':
            return render_template('database.html',projectname='Astra',coockieid=request.cookies.get('coockieid'))
        else:
            resp = redirect("/dashboard")
            return resp

    @app.route('/approve', methods=['POST', 'GET'])
    def apr():
        if check_status() == 'Admin':
            return render_template('approve.html',projectname='Astra',coockieid=request.cookies.get('coockieid'))
        else:
            resp = redirect("/dashboard")
            return resp

    @app.route('/register', methods=['POST', 'GET'])
    def reg():
        if request.method == 'POST' and request.form.get('password') and not request.form.get('otpk'):
                login = request.form.get('login')
                password = request.form.get('password')

                db = database.db('main.db')
                if not db.check_user({'login':login}):
                    otpk = db.create_user({'login':login,'pass':password})
                    img = qrcode.make(pyotp.totp.TOTP(request.form.get('otpk')).provisioning_uri("{}".format(login), issuer_name="Dashboard"))
                    img.save('./static/users/qrs/{}.png'.format(request.form.get('login')))
                    return render_template('register_qr.html',projectname='Astra',coockieid=request.cookies.get('coockieid'), qr = './static/users/qrs/{}.png'.format(request.form.get('login')),image="bg{}.png".format(random.randint(1, 6)))
        return render_template('register.html',projectname='Astra',coockieid=request.cookies.get('coockieid'),image="bg{}.png".format(random.randint(1, 6)))

    @socketio.on('database_query')
    def hande_query(json, methods=['GET', 'POST']):
        db = database.db('main.db')
        resp = db.make_custom_query(json['query'])
        socketio.emit('query_response', {'time':str(datetime.datetime.now()),'query_response':resp})

    @socketio.on('status_query')
    def hande_status(json, methods=['GET', 'POST']):
        db = database.db('main.db')
        #print([json['username']])
        if db.set_user_status([json['username']]):
            socketio.emit('add_response', {'query_response':'Done'})

    @socketio.on('load_lib')
    def hande_lib(methods=['GET', 'POST']):
        print('Got laoding request.')

        f = open('llibs.data')
        counter = 0

        for i in f:
            try:
                importlib.import_module(i.strip())
            except Exception as e:
                print('Error loading {}'.format(i))
                socketio.emit('lib_response', {'number':counter,'name':i,'status':'❌'})

            else:
                print('Loaded {}'.format(i))
                socketio.emit('lib_response', {'number':counter,'name':i,'status':'✔️'})

            counter += 1
    @socketio.on('parse_query')
    def hande_query(json, methods=['GET', 'POST']):
        data = code_handler.parse(json['query'])
        resp = ''
        if json['query'].split()[0] == 'ls':
            for i in data:
                resp += ' ' + i
        else:
            resp = data
        socketio.emit('code_response', {'time':str(datetime.datetime.now()),'query_response':resp})
    #socketio.emit(db_answer)
    #app.run(host= '192.168.1.68')
    socketio.run(app)
run()
