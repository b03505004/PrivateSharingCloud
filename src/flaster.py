from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import hashlib
import time
import os
import random
import string
import cv2
import numpy as np
import json
import socket
import threading
import pyaudio
import wave
import moviepy.editor as mp
import requests

ip_port = '127.0.0.1:66'
app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
#tcp server
TCP_IP = '127.0.0.1'
TCP_PORT = 8787
BUFFER_SIZE  = 4096

@app.route("/")
def index():
    return render_template("index.html", IPPORT=ip_port)

@app.route("/play")
def play():
    return render_template("play.html", IPPORT=ip_port)


@app.route("/playcheck/<filename>")
def playcheck(filename):
    with open("./db.csv") as file:
        content=file.readlines()
    for line in content:
        c=line.split(",")
        idd=c[0]
        ttl=c[1]
        if(idd==filename):
            if(float(ttl)<time.time() or ttl=='-1'):
                md5=hashlib.md5()
                md5.update(idd.encode('utf-8'))
                if os.path.isfile("./templates/data/"+md5.hexdigest()+".html"):
                    os.system('del ".\\templates\\data\\'+md5.hexdigest()+'.html"')
                    os.system('del ".\\templates\\data\\'+md5.hexdigest()+'.csv"')
                    os.system('del ".\\static\\'+md5.hexdigest()+'.'+c[2]+'"')
                return '<script>alert("亲，您要求的 '+filename+' 视频已经过期了哦")</script><meta http-equiv="refresh" content="0;url=http://'+ip_port+'">'#http://140.112.211.30/project/">'
            else:
                md5=hashlib.md5()
                md5.update(idd.encode('utf-8'))
                return '<script>alert("亲，即将带领您訪問 '+filename+' 视频，请系好安全带哦")</script><meta http-equiv="refresh" content="0;url=http://'+ip_port+'/data/'+md5.hexdigest()+'.html" />'
    return '<script>alert("亲，这里找不到您要求的 '+filename+' 视频哦")</script><meta http-equiv="refresh" content="0;url=http://'+ip_port+'/">'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def getFileType(file):
    return file[file.find('.'):]

@app.route("/upload")
def upload():
    return render_template("upload.html", IPPORT=ip_port)

@app.route("/uploader", methods=['POST'])
def uploader():
    target = os.path.join(APP_ROOT, 'static/')
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)
    files = request.files.getlist("file")
    ID = ''
    fileType = ''
    hashedID=''
    if files:
        for file in files:
            print("____________________________________")
            ID = str(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)))
            md5 = hashlib.md5()
            md5.update(ID.encode('utf-8'))
            hashedID = md5.hexdigest()
            print('file name:', file)
            print('file id:', ID)  
            print('file hashed:', hashedID)  
            fileType = getFileType(file.filename)
            fileNameType = str(hashedID) + fileType
            destination = "/".join([target, fileNameType])
            print('file dest:', destination)
            file.save(destination)
            print("____________________________________")
        ttl = request.form.get("TTL")
        deadTime = time.time() + float(ttl)*60
        with open('db.csv', 'a') as f:
            f.write(ID)
            f.write(',')
            if ttl == '-1':
                f.write('-1')
            else:
                f.write(str(deadTime))
            f.write(',')
            f.write(fileType[1:])
            f.write('\n')
        with open('./templates/data/'+str(hashedID)+".html",'w', encoding="utf-8") as file:
            file.write('<!DOCTYPE html>\
            <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.6/socket.io.min.js"></script>\
            <html lang="en">\
            <head>\
                <meta charset="UTF-8">\
                <meta name="viewport" content="width=device-width, initial-scale=1.0">\
                <meta http-equiv="X-UA-Compatible" content="ie=edge">\
                <title>视频弹幕墙</title>\
                <link rel="stylesheet" href="{{ url_for(\'static\',filename=\'styles/style.css\') }}">\
            </head>\
            <body bgcolor="#CC3B23">\
                <div class="screen_container">\
                    <video controls controlsList="nodownload noremote foobar" id="vid" value="abc">\
                        <source src="{{ url_for(\'static\', filename=\''+str(hashedID)+'.mp4\') }}">\
                        Your browser does not support HTML5 video.\
                    </video>\
                </div>\
                <div class="screen_toolbar">\
                    <input id="screenBulletText" type="text" placeholder="请输入弹幕内容"/>\
                    <button id="send_button" class="send" onclick="send_button()" value=\''+str(hashedID)+'\'>发射</button>\
                    <button class="clear">开启/关闭弹幕</button>\
                </div>\
                <br><br><form action="http://'+ip_port+'" style="font-size:40px; text-align:center;"> <input type="submit" value="返回主页"></form>\
            </body>\
            <script type="text/javascript" src="{{ url_for(\'static\', filename=\'jquery-3.3.1.min.js\') }}"></script>\
            <script type="text/javascript" src="{{ url_for(\'static\', filename=\'main.js\') }}"></script>\
            <script type="text/javascript">\
                var v = JSON.parse(\'{{dic|tojson|safe}}\');\
                console.log(v.context);\
                if (v.time[0]!= -1){\
                    get_list(v);\
                    print_list();\
                }\
            </script>\
            </html>')

            """file.write('<link rel="stylesheet" href="{{url_for(\'static\',filename=\'styles/index.css\')}}"><video class=\
            "center" controls controlsList="nodownload noremote foobar"><source src="{{url_for(\'static\', filename=\''+hashedID+fileType+ '\')}}">\
            Your browser does not support HTML5 video.</video>\
            <br><br><form action="http://'+ip_port+'" style="font-size:40px; text-align:center;"> <input type="submit" value="返回主页"></form>')"""
        print(ttl)
        print(type(ttl))
        return '<!DOCTYPE html>\
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\
        <meta name="viewport" content="width=device-width, initial-scale=0.6">\
        <link rel="stylesheet" href="{{ url_for("static",filename="styles/index.css")} }">\
        <link rel="icon" type="image/png" sizes="32x32" href="{{ url_for("static",filename="favicon-32x32.css") }}">\
        <html>\
        <head>\
        <title>上传成功</title>\
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>\
        </head>\
        <body bgcolor="#CC3B23" style="font-size:40px; text-align:center;color: #FADF55;">\
        <br><br>\
        上传成功\
        <br><br>'\
        +'亲，您的视频号码: '+ ID +\
        '<br><br>\
        <form action="http://'+ip_port+'"> \
        <input type="submit" value="返回主页">\
        </form>\
        </body>\
        </html>'
    else:
        return '<meta http-equiv="refresh" content="0;url=http://'+ip_port+'/upload">'

@app.route("/data/<filename>")
def data_file(filename):
    print(filename)
    filePathName = './templates/data/'+filename[:-5]+'.csv'
    if os.path.isfile(filePathName):
        bullet = {}
        bullet['time'] = []
        bullet['context'] = []
        tosort = {}
        with open(filePathName, 'r') as f:
            for l in f.readlines():
                time = float(l.split(',')[0])
                text = l.split(',')[1][:-1]
                tosort[time] = text
                #bullet['time'].append(time)
                #bullet['context'].append(text)
        keylist = list(tosort.keys())
        keylist.sort()
        for key in keylist:
            bullet['time'].append(key)
            bullet['context'].append(tosort[key])
        print(bullet)
        return render_template("data/"+filename, dic=bullet)
    else:
        return render_template("data/"+filename, dic={'time':[-1]})

@socketio.on('new_bullet', namespace='/data')
def handle_new_bullet(bullet):
    print('0')
    print('___________________________')
    print(bullet)
    filename = bullet['id'] + '.csv'
    if bullet['bullet'] != '':
        with open('./templates/data/'+filename, 'a') as f:
            f.write(str(bullet['time']))
            f.write(',')
            f.write(bullet['bullet'])
            f.write('\n')

@app.route("/play2")
def vid():
    data = [1, 'foo']
    print(123)
    bullet = {}
    bullet['time'] = []
    bullet['context'] = []
    tosort = {}
    if os.path.isfile('abc.csv'):
        with open('abc.csv', 'r') as f:
            for l in f.readlines():
                time = float(l.split(',')[0])
                text = l.split(',')[1][:-1]
                tosort[time] = text
                #bullet['time'].append(time)
                #bullet['context'].append(text)
        keylist = list(tosort.keys())
        keylist.sort()
        for key in keylist:
            bullet['time'].append(key)
            bullet['context'].append(tosort[key])
        print(bullet)
        return render_template("play2.html", dic=bullet, data=json.dumps(data))
    else:
        return render_template("play2.html", dic={'time':[-1]})

#啟動接受WEBCAM影片server
def launchVideoReceiveServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)
    print('waiting for connection')
    conn, addr = s.accept()
    print ('Connection address:', addr)
    ttl = conn.recv(1024)
    print(ttl)
    ttl = int(ttl.decode())
    ID = str(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)))
    md5 = hashlib.md5()
    md5.update(ID.encode('utf-8'))
    hashedID = md5.hexdigest()
    newFileName = str(hashedID)+'.mp4'
    myfile = open('./static/'+newFileName, 'wb')
    #接收影片檔案
    while True:
        data = conn.recv(BUFFER_SIZE)
        try:
            pc = data.decode()
            if pc=='DONE':
                break
        except:
            pass
        myfile.write(data)
        print ('writing file ....')
        if not data:
            break
    print('finished writing file')
    #回傳影片ID
    conn.send(str.encode(ID))
    myfile.close()
    conn.close()
    print ('client disconnected')
    deadTime = time.time() + float(ttl)*60
    with open('db.csv', 'a') as f:
        f.write(ID)
        f.write(',')
        if ttl == '-1':
            f.write('-1')
        else:
            f.write(str(deadTime))
        f.write(',')
        f.write('mp4')
        f.write('\n')
    #製作播放影片HTML
    with open('./templates/data/'+str(hashedID)+".html",'w', encoding="utf-8") as file:
        file.write('<!DOCTYPE html>\
        <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.6/socket.io.min.js"></script>\
        <html lang="en">\
        <head>\
            <meta charset="UTF-8">\
            <meta name="viewport" content="width=device-width, initial-scale=1.0">\
            <meta http-equiv="X-UA-Compatible" content="ie=edge">\
            <title>视频弹幕墙</title>\
            <link rel="stylesheet" href="{{ url_for(\'static\',filename=\'styles/style.css\') }}">\
        </head>\
        <body bgcolor="#CC3B23">\
            <div class="screen_container">\
                <video controls controlsList="nodownload noremote foobar" id="vid" value="abc">\
                    <source src="{{ url_for(\'static\', filename=\''+str(hashedID)+'.mp4\') }}">\
                    Your browser does not support HTML5 video.\
                </video>\
            </div>\
            <div class="screen_toolbar">\
                <input id="screenBulletText" type="text" placeholder="请输入弹幕内容"/>\
                <button id="send_button" class="send" onclick="send_button()" value=\''+str(hashedID)+'\'>发射</button>\
                <button class="clear">开启/关闭弹幕</button>\
            </div>\
            <br><br><form action="http://'+ip_port+'" style="font-size:40px; text-align:center;"> <input type="submit" value="返回主页"></form>\
        </body>\
        <script type="text/javascript" src="{{ url_for(\'static\', filename=\'jquery-3.3.1.min.js\') }}"></script>\
        <script type="text/javascript" src="{{ url_for(\'static\', filename=\'main.js\') }}"></script>\
        <script type="text/javascript">\
            var v = JSON.parse(\'{{dic|tojson|safe}}\');\
            console.log(v.context);\
            if (v.time[0]!= -1){\
                get_list(v);\
                print_list();\
            }\
        </script>\
        </html>')
    print('UPLOADED')

#錄製视频页面
@app.route("/record")
def record():
    t = threading.Thread(target=launchVideoReceiveServer)
    t.daemon = True
    t.start()
    return render_template("start_record.html", IPPORT=ip_port)


if __name__ == "__main__":
    socketio.run(app, port=66, debug=True)