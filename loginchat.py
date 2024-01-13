from flask import Flask,render_template,request,session,flash
from flask_socketio import SocketIO,emit,send,join_room,leave_room
import pymysql
import os

app=Flask(__name__)
app.secret_key="login"
socketio=SocketIO(app)

rooms={}

@app.route('/',methods=['GET','POST'])
def home():
    msg=''
    if request.method == "POST":
        username=request.form.get("username")
        password=request.form.get("password")
        session['user']=username
        con=pymysql.connect(host='localhost',user='root',password='',db='loginchat')
        cur=con.cursor()
        cur.execute("SELECT username,password FROM register")
        res1=cur.fetchall()
        if (username , password) not in res1:
            msg="Invalid username or password...please try again"
            return render_template("chat2/login.html",msg=msg)
        else:

            print("login successfully...")
            cur.execute("select * from register ")
            res=cur.fetchall()
            return render_template("chat2/chatlist.html",userid=username,res=res)
    return render_template("chat2/login.html",msg=msg)

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=="POST":
        msg='--'
        username=request.form.get("username")
        email=request.form.get("email")
        gender=request.form.get("gender")
        birthdate=request.form.get("birthdate")
        city=request.form.get("city")
        contact=request.form.get("phone")
        password=request.form.get("password")
        confirm_pass=request.form.get("confirm_password")

         #upload photo code
        app.config['UPLOAD_FOLDER']=os.path.basename('static')
        file=request.files['photo']
        fname=file.filename
        f=os.path.join(app.config['UPLOAD_FOLDER'],"login_img/"+fname)
        file.save(f)

        if password == confirm_pass:
            con=pymysql.connect(host='localhost',user='root',password='',db='loginchat')
            cur=con.cursor()
            sqla="INSERT INTO register(username,email,gender,birthdate,city,contact,password,photo)VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sqla,(username,email,gender,birthdate,city,contact,password,fname))
            con.commit()
            msg="Successfully Registered"
            cur.execute("select * from register ")
            res=cur.fetchall()
            return render_template("chat2/chatlist.html",msg=msg,res=res,userid=username)
        else:
            msg="password and confirm password must be same..."
            return render_template("chat2/register.html",msg=msg)
    return render_template("chat2/register.html")

@app.route("/chatroom",methods=['GET','POST'])
def chatroom():
    session.clear()
    if request.method=="POST":
        username=request.form.get("username")
        roomcode=request.form.get("roomcode")
        new_room = {
                'members': 0,
                'messages': []
            }
        rooms[roomcode] = new_room

        session['username']=username
        session['roomcode']=roomcode
        messages = rooms[roomcode]['messages']
    return render_template("chat2/chatroom.html",username=username,roomcode=roomcode,messages=messages)

@socketio.on('connect')
def handle_connect():
    name=session.get('username')
    room=session.get('roomcode')
    if name is None or room is None:
        return 
    if room not in rooms:
        leave_room(room)
    join_room(room)
    print(f"{name} joined room {room}")
    send({
        "sender":"",
        "message":f"{name} has entered the chat"
    },to=room)
    rooms[room]["members"]+=1
    print(rooms[room])

@socketio.on('message')
def handle_message(payload):
    name=session.get('username')
    room=session.get('roomcode')
    message = {
        "sender": name,
        "message": payload['data']
    }
    print(message['message'])
    send(message, to=room)
    rooms[room]["messages"].append(message)

@socketio.on('disconnect')
def handle_disconnect():
    name=session.get('username')
    room=session.get('roomcode')
    leave_room(room)

    if room in rooms:
        rooms[room]["members"]-=1
        if rooms[room]["members"]<=0:
            del rooms[room]
    send({
            "message":f"{name} has left the chat",
            "sender" : ""  
         },to=room)
    
if __name__=="__main__":
    app.debug=True
    socketio.run(app)


        
