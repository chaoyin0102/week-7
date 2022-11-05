# coding=UTF-8
from flask import Flask, request, render_template, session, redirect, jsonify
import mysql.connector
import mysql.connector.pooling
import os # for secret key

#create connection
mydb = {
    "host": "localhost",
    "user": "root",
    "password": "********",
    "database": "website",
    "buffered": True
}


cnx_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name = "website_pool",
    pool_size = 3,
    **mydb
)

# create application object
app = Flask(
    __name__,
    static_folder = "static",
    static_url_path = "/"
)

# create the secret key (generate random string)
app.secret_key = os.urandom(20)

# homepage
@app.route("/")
def home():
    return render_template("homepage.html")

# for creating an account
@app.route("/signup", methods = ["POST"])
def signup():
    # get name, username, password from form by POST
    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")
    try:
        # connect with connection pool
        cnx = cnxpool.get_connection()
        cnxcursor = cnx.cursor()
        cnxcursor.execute("SELECT * FROM member WHERE username=%s LIMIT 1", (username,))
        check_exist = cursor.fetchone()
        if check_exist:
            return redirect("/error?message=帳號已經被註冊")
        else:
            cnxcursor.execute("INSERT INTO member(name, username, password) VALUES(%s, %s, %s)", (name, username, password,))
            cnx.commit()
            return redirect("/")
    except:
        print("Unspected Error")
    finally:
        # close connection
        cnxcursor.close()
        cnx.close

# sign in
@app.route("/signin", methods = ["POST"])
def signin():
    # get username, password from form by POST
    username = request.form.get("username")
    password = request.form.get("password")
    try:
        cnx = cnxpool.get_connection()
        cnxcursor = cnx.cursor(dictionary = True)
        cnxcursor.execute("SELECT * FROM member WHERE username=%s AND password=%s", (username, password,))
        member = cursor.fetchone()
        if member:
            # create session
            session["id"] = member[0]
            session["name"] = member[1]
            session["username"] = member[2]
            return redirect("/member")
        else:
            return redirect("/error?message=帳號或密碼輸入錯誤")
    except:
        print("ERROR")
    finally:
        cnxcursor.close()
        cnx.close()

# /signout
@app.route("/signout")
def signout():
    session.pop("username")
    return redirect("/")

# /member
@app.route("/member")
def member():
    # if user has signed in
    if "username" in session:
        return render_template ("member.html", name = session["name"])

# /error
@app.route("/error")
def error():
    # get query string of message
    message = request.args.get("message")
    # show message on error page
    return render_template("error.html", message = message)

# /back
@app.route("/back")
def back():
    return redirect("/")

# Request-1
# api
@app.route("/api/member", methods = ["GET"])
def apiMember():
    username = request.args.get("username")
    try:
        cnx = cnxpool.get_connection()
        cnxcursor = cnx.cursor(dictionary = True)
        cnxcursor.execute("SELECT id, name, username FROM member WHERE username=%s", (username))
        profile = cnxcursor.fetchone()
        return jsonify({"data": profile}) # return JSON
    except:
        print("Unspected Error")
    finally:
        cnxcursor.close()
        cnx.close()

# Request-3
@app.route("/api/member", methods = ["PATCH"]) 
def update_name():
    if "username" in session:
        new_name = request.json
        try:
            cnx = cnxpool.get_connection()
            cnxcursor = cnx.cursor(dictionary = True)
            cnxcursor.execute("UPDATE member SET name=%s WHERE username=%s", (new_name["name"], session["username"]))
            cnx.commit()
            session["name"] = new_name["name"]
            return jsonify({"ok": True})
        except:
            print("Unspected Error")
        finally:
            cnxcursor.close()
            cnx.close()
    else:
        return jsonify({"error": True})

app.run(port = 3000, debug = True)
