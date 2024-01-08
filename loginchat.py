from flask import Flask,render_template,request,session,flash
from flask_socketio import SocketIO
import pymysql

app=Flask(__name__)
app.secret_key="login"
socketio=SocketIO(app)

@app.route('/')
def home():
    return render_template("chat2/login.html")

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

        if password == confirm_pass:
           con=pymysql.connect(host='localhost',user='root',password='',db='loginchat')
           cur=con.cursor()
           sqla="INSERT INTO register(username,email,gender,birthdate,city,contact,password)VALUES(%s,%s,%s,%s,%s,%s,%s)"
           cur.execute(sqla,(username,email,gender,birthdate,city,contact,password))
           con.commit()
           msg="Successfully Registered"
           return render_template('chat2/chatlist.html',msg=msg,username=username)
        else:
            msg="password and confirm password must be same..."
            return render_template("chat2/register.html",msg=msg)

    return render_template("chat2/register.html")

@app.route('/logout')
def logout():
    return render_template("chat2/login.html")


if __name__=="__main__":
    app.debug=True
    socketio.run(app)


        
