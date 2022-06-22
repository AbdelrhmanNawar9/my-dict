from crypt import methods
import os
from venv import create
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import  login_required

import json




# for more information on how to install requests
# http://docs.python-requests.org/en/master/user/install/#install
import requests
import json

# import arabic_reshaper
# from bidi.algorithm import get_display


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded in terminal
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///my_dict.db")

# Credentials
# TODO: replace with your own app_id and app_key
app_id = "32f575f8"
app_key = "8421119fded20ce9c5f40c568bdbe1c1"

language = 'en-gb'
fields = 'definitions,pronunciations,registers,variantForms,domains,etymologies'
fields = ''
strictMatch = 'false'

# To get the results from both the API and db
def get_results(word, search_type):
    results = {"online_results": None, "my_results": None, "word": word, "in_my_list": False}
    if search_type == "translation(en-ar)":
        url = 'https://od-api.oxforddictionaries.com/api/v2/translations/en/ar/' + \
            word.lower() + '?' + 'strictMatch=' + strictMatch
    else:
        url = 'https://od-api.oxforddictionaries.com/api/v2/words/' + \
            language + '?q=' + word.lower()

    r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
    # print("status: {}".format(r.status_code))
    # print("responsetext: {}".format(r.text))
    # For translations
    # Check that there is a correct response
    if r.status_code == 200:
        # Get response entries
        lexical_entries = r.json()["results"][0]["lexicalEntries"]
        results["online_results"] = lexical_entries

    # check that table is exist in the db
    if len(db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='my_definitions'")) != 0:
        # Get my results from database
        my_results = db.execute(
            "SELECT * FROM my_definitions WHERE word = ? AND userr_id = ?", word, session["user_id"])
        # print("Those are my results ''''''''''''''''''''''",
        #       my_results, type(my_results))

        # Check that there is a correct response
        if len(my_results) != 0:
            results["my_results"] = my_results
            
        # Check if the word exists in my word list 
        word_count = db.execute("SELECT COUNT(*) as count FROM my_word_list WHERE userr_id = ? AND word = ?",session["user_id"], word)[0]["count"]
        # print("count", word_count)
        
        if word_count != 0:
            results["in_my_list"] = True
            

    return results


@app.route("/")
@login_required
def index():
    """Show HomePage for the site"""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        data = request.get_json()
        
        # print(data["userName"])
        
         # Ensure username was submitted
        if not data["userName"]:
            return jsonify({"message":"Enter User Name and Password"})

        # Ensure password was submitted
        elif not data["password"]:
            return jsonify({"message":"Enter User Name and Password"})
        
          # Ensure users table is exist 
        db.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY ,username TEXT NOT NULL, hash TEXT NOT NULL)")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", data["userName"])

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], data["password"]):
            return jsonify({"message":"Invalid User Name or Password"})

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # print("user id : {} loged in".format(session["user_id"]))

        # Redirect user to home page
        return jsonify("index.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    # If Post request register the user
    """Register user"""
    if request.method == "POST":
        data = request.get_json()

        # Check for errors
        # Ensure username was submitted
        if not data["userName"]:
            return jsonify({"message":"Enter User Name and Password"})
            
        # Ensure users table is exist 
        db.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY ,username TEXT NOT NULL, hash TEXT NOT NULL)")

        # Ensure username is not taken
        names1 = db.execute("SELECT username FROM users")
        names = []
        for s in names1:
            names.append(s["username"])

        if data["userName"] in names:
            return jsonify({"message":"Sorry, this user name is already taken."})
            
        # Ensure password was submitted
        elif not data["password"]:
            return jsonify({"message":"Enter the password"})
            
        # Ensure password-confirm was submitted
        elif not data["passwordConfirmation"]:
            return jsonify({"message":"Enter the password confirmation."})

        # Ensure password-confirm is the same as confirmation
        elif not data["passwordConfirmation"] ==  data["password"]:
            return jsonify({"message":"Password and password confirmation don't match!"})

        # Insert the user into users table (database)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", data["userName"], generate_password_hash(data["password"]))

        # Remember which user has logged in
        user = db.execute("SELECT id FROM users WHERE username = ?", data["userName"])[0]
        session["user_id"] = user["id"]

        # redirect to the home page for that user
        # We could return anything (as we don't need a particular thing as we wont use it) 
        return jsonify("index.html")
        
    # If it is  GET request then display the registeration form
    else:
        return render_template("register.html")

@app.route("/translate")
@login_required
def translate():
    """Show translations of a word"""
    word = request.args.get("word")
    search_type = request.args.get("search-type")

    # To deal from add function
    if word == None:
        word = ""

    results = get_results(word, search_type)
    return render_template("results.html", results=results)


# CREATE TABLE  my_definitions(word TEXT,word_meaning TEXT,word_trans TEXT,example_en TEXT,example_ar TEXT,word_type TEXT,word_notes TEXT,word_usuallywith TEXT);
# CREATE TABLE IF NOT EXISTS my_definitions(word TEXT,meaning TEXT,trans TEXT,example_en TEXT,example_ar TEXT,type TEXT,notes TEXT,usuallywith TEXT);


@app.route("/custom_definition", methods=["GET", "POST"])
@login_required
def add():
    """add a word to my definition db"""
    if request.method == "POST":
        word = request.form.get("word")
        meaning = request.form.get("meaning")
        trans = request.form.get("trans")
        type = request.form.get("type")
        example_en = request.form.get("example_en")
        example_ar = request.form.get("example_ar")
        notes = request.form.get("notes")
        usuallywith = request.form.get("usuallywith")
        # print(word, meaning, trans, type, example_en,
        #       example_ar, notes, usuallywith)

        # Create a table if not exists
        db.execute("CREATE TABLE IF NOT EXISTS my_definitions(id INTEGER PRIMARY KEY,userr_id INTEGER,word TEXT,meaning TEXT,trans TEXT,example_en TEXT,example_ar TEXT,type TEXT,notes TEXT,usuallywith TEXT)")

        # Add the word_def to db
        db.execute("INSERT INTO my_definitions (word,meaning,trans,type,example_en,example_ar,notes,usuallywith,userr_id) VALUES (?,?,?,?,?,?,?,?,?)",
                   word, meaning, trans, type, example_en, example_ar, notes, usuallywith, int(session["user_id"]))
        # Debug

        # print(db.execute("SELECT * FROM my_definitions WHERE word = ? AND userr_id = ?", word, session["user_id"]))

        # Refresh the page to display it with the new custome definition
        return redirect("/translate?word={}".format(word))
    else:
         # Fetch data from db
        my_custom_definitions_list = {"definitions": None, "definitions_count": 0}
        fetched_my_word_list = db.execute("SELECT * FROM my_definitions WHERE userr_id = ?", session["user_id"])
        definitions_count = len(fetched_my_word_list)
        # print("ssss",fetched_my_word_list)
        if not definitions_count == 0:
            my_custom_definitions_list["definitions"] = fetched_my_word_list
            my_custom_definitions_list["definitions_count"] = definitions_count
        return render_template("custom_definitions.html", my_definitions = my_custom_definitions_list)


@app.route("/remove", methods=["GET", "POST"])
def remove():
    """remove a word from my definitions db"""
    if request.method == "POST":
        word = request.form.get("word")
        id = request.form.get("id")

        # Delete from db 
        db.execute("DELETE FROM my_definitions WHERE id = ? AND userr_id =?", id, session["user_id"])

        # # Debug
        # print(db.execute("SELECT * FROM my_definitions WHERE id = ?", id))

        # Refresh the page to display it with the new custome definition
        return redirect("/translate?word={}".format(word))
    return render_template("index.html")

    
# //////////////////// My word list /////////////////////

@app.route("/add_to_word_list", methods=["POST", "GET"])
@login_required
def add_to_word_list():
    "Add a word to word list"
    
    # Add a word to my word list if POST request
    if request.method == "POST":
        data = request.get_json()
        word = data["word"]
        # Check for errors
        if not word:
            return jsonify({"message":"There was no word submited!"})
        
        # Make the table if not exist 
        db.execute("CREATE TABLE IF NOT EXISTS my_word_list (userr_id INTEGER,word TEXT)")
        
        # Insert the word to my words list 
        db.execute("INSERT INTO my_word_list (userr_id,word) VALUES (?,?)", session["user_id"], word)
        
        return jsonify({"status":"ok", "message": "Successfully added to word list"})
     
        
    # Display my word list if GET request
    else:
        # Fetch data from db
        my_word_list = {"words": None, "words_count": 0}
        fetched_my_word_list = db.execute("SELECT word FROM my_word_list WHERE userr_id = ?", session["user_id"])
        words_count = len(fetched_my_word_list)
        # print("fetched word list",fetched_my_word_list)
        if not words_count == 0:
            my_word_list["words"] = fetched_my_word_list
            my_word_list["words_count"] = words_count
        return render_template("my_word_list.html",  my_word_list=my_word_list)

@app.route("/remove_from_word_list", methods=["POST"])
def remove_word_list():
    """ Delete a word list from db"""
    data = request.get_json()
    word = data["word"]
    
     # Check for errors
    if not word:
        return jsonify({"message":"There was no word submited!"})
    
    # Delete from db 
    db.execute("DELETE FROM my_word_list WHERE word = ? AND userr_id =?", word, session["user_id"])   
    
    return jsonify({"status":"ok", "message": "Successfully removed from word list"}) 
    
    
if __name__ == "__main__":
    create_app().run()