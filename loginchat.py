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
            return render_template("chat2/chatlist.html",username=username,res=res)
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
        session['username']=username
        print(session['username'])
        if password == confirm_pass:
            con=pymysql.connect(host='localhost',user='root',password='',db='loginchat')
            cur=con.cursor()
            sqla="INSERT INTO register(username,email,gender,birthdate,city,contact,password,photo)VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sqla,(username,email,gender,birthdate,city,contact,password,fname))
            con.commit()
            msg="Successfully Registered"
            cur.execute("select * from register ")
            res=cur.fetchall()
            return render_template("chat2/chatlist.html",msg=msg,res=res,username=username)
        else:
            msg="password and confirm password must be same..."
            return render_template("chat2/register.html",msg=msg)
    return render_template("chat2/register.html")  

@app.route("/chatlist_back") 
def chatlist_back():
    username=request.args.get("username")
    con=pymysql.connect(host='localhost',user='root',password='',db='loginchat')
    cur=con.cursor()
    cur.execute("select * from register ")
    res=cur.fetchall()
    return render_template("chat2/chatlist_back.html",username=username,res=res)


@app.route("/chatroom",methods=['GET','POST'])
def chatroom():
    session.clear()
    if request.method=="POST":
        username=request.form.get("username")
        receiver=request.form.get("receiver")
        roomcode=request.form.get("roomcode")
        new_room = {
                'members': 0,
                'receiver':"",
                'messages':[]
            }
        rooms[roomcode] = new_room
        
        session['username']=username
        session['receiver']=receiver
        session['roomcode']=roomcode
        messages = rooms[roomcode]['messages']
        receiver=rooms[roomcode]['receiver']
        print(rooms[roomcode])
    return render_template("chat2/chatroom.html",username=username,roomcode=roomcode,messages=messages,receiver=session['receiver'])

@app.route("/display_data")
def display_data():
    user=request.args.get('user_id')
    name=session.get('username')
    con=pymysql.connect(host='localhost',user='root',password='',db='loginchat')
    cur=con.cursor()
    cur.execute("select * from register where username=%s",user)
    res=cur.fetchall()
    return render_template("chat2/display_data.html",username=name,res=res)

@app.route("/delete_data")
def delete_data():
    user=request.args.get('del_id')
    name=session.get('username')
    con=pymysql.connect(host='localhost',user='root',password='',db='loginchat')
    cur=con.cursor()
    cur.execute("delete from register where username=%s",user)
    con.commit()
    con=pymysql.connect(host='localhost',user='root',password='',db='loginchat')
    cur=con.cursor()
    cur.execute("select * from register")
    res=cur.fetchall()
    return render_template("chat2/chatlist_back.html",res=res,username=name)

@socketio.on('connect')
def handle_connect():
    name=session.get('username')
    rec_id=session.get('receiver')
    room=session.get('roomcode')
    if name is None or room is None:
        return 
    if room not in rooms and rec_id not in rooms:
        leave_room(rec_id)
    join_room(rec_id)
    print(f"{name} joined room {rec_id}")
    send({
        "sender":"",
        "message":f"{name} has joined {rec_id}"
    },to=rec_id)
    print(rec_id)
    rooms[room]["members"]+=1
    rooms[room]["receiver"]=rec_id
    print(rooms[room])

@socketio.on('message')
def handle_message(payload):
    name=session.get('username')
    rec_id=session.get('receiver')
    room=session.get('roomcode')
    message = {
        "sender": name,
        "receiver":rec_id,
        "message": payload['data']
    }
    print(message)
    send(message, to=name)
    send(message,to=rec_id)
    rooms[room]["messages"].append(message)

@socketio.on('disconnect')
def handle_disconnect():
    name=session.get('username')
    rec_id=session.get('receiver')
    room=session.get('roomcode')
    leave_room(rec_id)

    if room in rooms:
        rooms[room]["members"]-=1
        if rooms[room]["members"]<=0:
            del rooms[rec_id]
    send({
            "message":f"{name} has left the chat",
            "sender" : ""  

         },to=rec_id)
    
if __name__=="__main__":
    app.debug=True
    socketio.run(app)


        
