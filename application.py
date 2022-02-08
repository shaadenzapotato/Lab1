from asyncio.windows_events import NULL
from audioop import avg
import os
from cachelib import NullCache
import requests

from flask import Flask, jsonify, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine, null
from sqlalchemy.orm import scoped_session, sessionmaker



app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#change styling
#fix register, logout, log in
@app.route("/", methods=["POST","GET"])
def index():
    if request.method=="GET":
        if session.get("username") is None:
            #change this to not have navbar
            return render_template("index.html")
        else:
            message="You are already logged in."
            return render_template("message.html", message=message)
    else:
        message="You have successfully logged out."
        session["username"]=None
        session["password"]=None
        return render_template("message.html", message=message)

@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method=="GET":
        if session["username"] is None:
            message="Please log in first."
            return render_template("message.html",message=message)
        else:
            message= "Search for some books, "
            return render_template("search.html", username=session["username"], message=message)

    
    else:
        #add log out
        session["username"] = request.form.get("username")
        session["password"] = request.form.get("password")
        
        #check if register or login
        
        # check if username exists
        dbusername=db.execute("SELECT * FROM users WHERE username= :user",
            {"user": session["username"]}).fetchone()

        if dbusername is None:
                #if username doesnt exist
                #else:
                    #register
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                        {"username":session["username"], "password": session["password"]})
            db.commit()
            message= "You've successfuly registered an account. Welcome, ";
            return render_template("search.html", username=session["username"], message=message)

            #if username exists
        else:
        #login
        #check if the password matches
            if dbusername[1]==session["password"]:
                #if it matches then 
                message= "You've successfuly logged back in, "
                return render_template("search.html", username=session["username"], message=message)
            else:    
            #if it doesnt match
            #error
                message= "It seems like you have forgot your password."
                return render_template("message.html", message=message)


@app.route("/results", methods=["POST"])
def results():
        isbn = request.form.get("isbn")
        title = request.form.get("title")
        author = request.form.get("author")
 
        results=db.execute("SELECT isbn, title, author FROM books WHERE isbn ILIKE :isbn AND title ILIKE :title AND author ILIKE :author ", 
            {"title": '%'+title+'%', "author": '%'+author+'%' , "isbn": '%'+isbn+'%' })


        if int(results.rowcount) == 0:
            message="No results available."
            return render_template("message.html", message=message)
        else:
            return render_template("results.html", results=results)
        

@app.route("/results/<book_id>", methods=["GET","POST"])
def book(book_id):
        if request.method=="GET":
            if session["username"] is None:
                message="Please log in first."
                return render_template("message.html",message=message)
            book=db.execute("SELECT * FROM books WHERE isbn=:bid",
            {"bid": book_id}).fetchone()
            bookrev=db.execute("SELECT * FROM bookrevs WHERE bookid=:book_id",
                {"book_id": book_id})
            res = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": "isbn:"+book_id})
            data=res.json()
            if data["totalItems"]==0:
                        #if none use null
                        avgrating=NULL   
                        numofrat=NULL
            else:
                        avgrating=data["items"][0]["volumeInfo"]["averageRating"]
                        numofrat=data["items"][0]["volumeInfo"]["ratingsCount"]
            return render_template("book.html", book=book, bookrev=bookrev,avgrating=avgrating, numofrat=numofrat )
        else:
            book=db.execute("SELECT * FROM books WHERE isbn=:bid",
            {"bid": book_id}).fetchone()
            review = request.form.get("review")
            score = request.form.get("score")
            
            if review is "" and score is "":
                message="Please submit a score and/or comment for your review to be accepted."
                return render_template("message.html", message=message) 
            try:
                score = int(request.form.get("score"))
            except ValueError:
                message="Please type in a valid number."
                return render_template("message.html",message=message)
            rev=db.execute("SELECT * FROM bookrevs WHERE bookid=:book_id AND username=:username",
                                {"book_id": book_id, "username": session["username"]}).fetchone()
            sc=db.execute("SELECT * FROM bookrevs WHERE bookid=:book_id AND username=:username",
                                {"book_id": book_id, "username": session["username"]}).fetchone()
                
            if rev is None and sc is None:
                    db.execute("INSERT INTO bookrevs (bookid, username, review, score) VALUES (:book_id,:username, :review, :score)",
                                    {"book_id": book_id, "username":session["username"], "review": review, "score": score})
                    db.commit()
            else:
                    if score is None:
                        db.execute("UPDATE bookrevs SET review=:review WHERE bookid=:book_id AND username=:username",
                                    {"book_id": book_id, "username":session["username"], "review": review})
                        db.commit()
                    if review is None:
                        db.execute("UPDATE bookrevs SET score=:score WHERE bookid=:book_id AND username=:username",
                                    {"book_id": book_id, "username":session["username"], "score": score})
                        db.commit()              
                    if rev is not None and sc is not None:
                        db.execute("UPDATE bookrevs SET review=:review WHERE bookid=:book_id AND username=:username",
                                        {"book_id": book_id, "username":session["username"], "review": review,"score": score})
                        db.execute("UPDATE bookrevs SET score=:score WHERE bookid=:book_id AND username=:username",
                                        {"book_id": book_id, "username":session["username"], "review": review,"score": score})
                        db.commit()
                    

            bookrev=db.execute("SELECT * FROM bookrevs WHERE bookid=:book_id",
                    {"book_id": book_id})
            res = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": "isbn:"+book_id})
            data=res.json()
            if data["totalItems"]==0:
                    #if none use null
                    avgrating=NULL   
                    numofrat=NULL
            else:
                    avgrating=data["items"][0]["volumeInfo"]["averageRating"]
                    numofrat=data["items"][0]["volumeInfo"]["ratingsCount"]
            return render_template("book.html", book=book, bookrev=bookrev,avgrating=avgrating, numofrat=numofrat )

@app.route("/api/<isbn>")
def apibook(isbn):
        if session["username"] is None:
            message="Please log in first."
            return render_template("message.html",message=message)
        
        #check if in database 
        id=db.execute("SELECT isbn FROM books WHERE isbn= :isbn",
            {"isbn": isbn}).fetchone()

        if id is None:
            return jsonify({"404 error":"Invalid isbn"}),404 
        
        res = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": "isbn:"+isbn})
        data=res.json()

        if data["totalItems"]==0:
            #if none use null
            avgrating=NULL   
            numofrat=NULL
            isbn10=NULL
            isbn13=NULL
            pubdat=NULL     
            title=NULL     
            author=NULL
        else:
            avgrating=data["items"][0]["volumeInfo"]["averageRating"]
            numofrat=data["items"][0]["volumeInfo"]["ratingsCount"]
            isbn10=data["items"][0]["volumeInfo"]["industryIdentifiers"][0]["identifier"]
            isbn13=data["items"][0]["volumeInfo"]["industryIdentifiers"][1]["identifier"]
            pubdat=data["items"][0]["volumeInfo"]["publishedDate"]
            title=data["items"][0]["volumeInfo"]["title"]
            author=data["items"][0]["volumeInfo"]["authors"][0]

        return jsonify({
            "title": title,
            "author": author,
            "publishedDate": pubdat,
            "ISBN_10": isbn10,
            "ISBN_13": isbn13, 
            "reviewCount": avgrating, 
            "averageRating": numofrat
        })



