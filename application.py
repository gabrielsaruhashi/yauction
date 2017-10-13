from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify, send_from_directory
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir

from flask_jsglue import JSGlue
import re
import datetime
import time

from helpers import *
import os
from werkzeug.utils import secure_filename

# Import smtplib for the actual sending function
import smtplib



UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = ['jpg']


# configure application
app = Flask(__name__)

JSGlue(app)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response
        
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

        
# custom filter
app.jinja_env.filters["usd"] = usd
        
# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///yauction.db")

@app.route("/")
@login_required
def home():
    return redirect(url_for("index"))

@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    # if user reached route via POST (as by submitting a form via POST)
    # Displays items that the user has won in auction
        
    # select all of the user's bids 
    user = session["user_id"]
    bids = db.execute("SELECT * FROM bids WHERE bidder_id = :user", user = user)

    #  return apology("You don't have any open bids!")
    item_ids = []
    for bid in bids:
        item_ids.append(bid["item_id"])
        
    # ensure each item id only appears once 
    items = list(set(item_ids))
    won_items = []
    
    # iterate through items that the user has bid on
    for item_id in items:
        tempDict = dict()
        seller = db.execute("SELECT seller_id FROM items WHERE item_id = :item_id", item_id=item_id)[0]["seller_id"]
        item_status = db.execute("SELECT status FROM items WHERE item_id = :item_id", item_id = item_id)[0]["status"]
        auction_winner = db.execute("SELECT bidder_id FROM bids WHERE item_id = :item_id ORDER BY timestamp DESC LIMIT 1", item_id=item_id)[0]["bidder_id"]
        # if auction is expired and user was the highest bidder, display the item
        if item_status == 0 and auction_winner == user:
            tempDict["charge"] = db.execute("SELECT bid_amount FROM bids WHERE item_id = :item_id ORDER BY timestamp DESC LIMIT 1", item_id=item_id)[0]["bid_amount"]
            tempDict["item_name"] = db.execute("SELECT item_name FROM items WHERE item_id = :item_id", item_id = item_id)[0]["item_name"]
            tempDict["item_id"] = item_id
            tempDict["venmo"] = db.execute("SELECT * FROM users WHERE user_id=:seller", seller=seller)[0]["venmo"]
            tempDict["seller_email"] = db.execute("SELECT email from users WHERE user_id = :seller_id", seller_id=seller)[0]["email"]
            won_items.append(tempDict)
            
    # check if user has ever won an auction
    if len(won_items) < 1:
        return apology("You haven't won any items yet!")
        
    # display history of auctions won, and provide link to the seller's Venmo account for payment
    return render_template("history.html", won_items=won_items)
    

@app.route("/index")
@login_required
def index(): 
     # get user id    
    user = session["user_id"]
    
    # query database for 10 items that are currently live
    random_rows = db.execute("SELECT * FROM items WHERE status=:live LIMIT 9", live=1)
    return render_template("index.html", random_rows=random_rows)
    
@app.route("/itm/<int:item_id>", methods=["GET", "POST"])
@login_required
def itm_page(item_id):
    # get user id
    user = session["user_id"]

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # if user clicks bid
        if request.form['btn'] == 'bid':

            if not request.form.get("place_bid"):
                return apology("missing bid")
            
            # convert user input to a float
            try:
                user_bid = float(request.form.get("place_bid"))
            
            # unless they provide invalid input
            except ValueError:
                return apology("invalid bid")
            
            # prevent user from bidding in their own auction
            seller_id = db.execute("SELECT seller_id FROM 'items' WHERE item_id = :itm_id", itm_id=item_id)[0]["seller_id"]
            if user == seller_id:
                return apology("you cannot bid on your own item")
                
            # ensure user provides positive number of shares
            if user_bid <= 0:
                return apology("invalid bid")
            
            # get current winning bid
            row = db.execute("SELECT current_bid FROM 'items' WHERE item_id = :itm_id", itm_id=item_id)
            current_bid = row[0]["current_bid"]
            
            # check if user bid actually tops current winning bid
            if user_bid <= current_bid:
                return apology("invalid bid")
            
            # add bid to database
            db.execute("INSERT INTO 'bids' (bidder_id, item_id, bid_amount) VALUES(:userid, :itm_id, :bid)", userid=user, itm_id=item_id, bid=user_bid)
            
            # update current_bid 
            db.execute("UPDATE 'items' SET current_bid=:bid WHERE item_id=:item_id", bid=user_bid, item_id=item_id)
            
            # update total_bids
            total_bids = db.execute("SELECT * FROM items WHERE item_id=:item_id", item_id=item_id)[0]["total_bids"]
            total_bids += 1
            db.execute("UPDATE items SET total_bids = :total_bids WHERE item_id=:item_id", total_bids=total_bids, item_id=item_id)
            
            # flash
            flash("Success")
            
            return redirect(url_for("itm_page", item_id=item_id))
            
        # if user clicked 
        if request.form['btn'] == 'watchlist':
            
            # check if the item is already in the user's watchlist
            row = db.execute("SELECT * FROM watchlist WHERE item_id = :item_id AND user_id = :user_id", item_id=item_id, user_id=user)
            
            # if yes, delete from watchlist
            if len(row) != 0:
                db.execute("DELETE FROM watchlist WHERE item_id = :item_id AND user_id = :user_id", item_id=item_id, user_id=user)
            
            # if not, insert into watchlist
            else:
                db.execute("INSERT INTO watchlist (item_id, user_id) VALUES (:item_id, :user_id)", item_id = item_id, user_id = user) 
        
            return redirect(url_for("watchlist"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        
        item_row = db.execute("SELECT * FROM 'items' WHERE item_id = :itm_id", itm_id=item_id)
        
        item_status = db.execute("SELECT status FROM items WHERE item_id=:itm_id", itm_id=item_id)[0]['status']
        if item_status == 1:
            # get current time
            time_now = datetime.datetime.utcnow()
            
            # get the timestamp of creation from the auction and format
            # in a way that is readable to python's datetime
            f = '%Y-%m-%d %H:%M:%S'
            time_start = datetime.datetime.strptime(item_row[0]["timestamp"], f)

            # delta of time
            elapsed = time_now - time_start

            # if more than established time
            if elapsed > datetime.timedelta(days=item_row[0]['duration']):
                db.execute("UPDATE 'items' SET status=:expired WHERE item_id=:itm_id", expired=0, itm_id=item_id)
        
        # check if user already has the item in his watchlist   
        row = db.execute("SELECT * FROM watchlist WHERE item_id = :item_id AND user_id = :user_id", item_id=item_id, user_id=user)
        
        # if there is a row, it means item is already in watchlist 
        if len(row) != 0:
            watchlist_status = 1
        
        # else, it is not in watchlist
        else: 
            watchlist_status = 0
        
        seller_id=item_row[0]["seller_id"]
        seller_name = db.execute("SELECT username FROM users WHERE user_id = :seller_id", seller_id=seller_id)[0]["username"]
        return render_template("itm.html", item_row=item_row, watchlist_status=watchlist_status, seller_name=seller_name, item_status=item_status)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
        
        flash("Welcome!")
        
        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))
    
@app.route("/my_auctions")
@login_required
def my_auctions():
    "Displays items that the user is currently selling."
        
    # select all of the user's auctions 
    user = session["user_id"]
    auctions = db.execute("SELECT * FROM items WHERE seller_id = :user", user = user)
   
    # create list of the items the user is selling
    item_ids = []
    for auction in auctions:
        item_ids.append(auction["item_id"])
        
    # ensure each item id only appears once 
    items = list(set(item_ids))
    current_auctions = []
    for item in items:
        auction_status = db.execute("SELECT status FROM items WHERE item_id=:item_id", item_id=item)[0]["status"]
        if auction_status == 1:
            tempDict = dict()
            tempDict["current_bid"] = db.execute("SELECT current_bid FROM items WHERE item_id = :item_id", item_id=item)[0]["current_bid"]
            tempDict["item_name"] = db.execute("SELECT item_name FROM items WHERE item_id = :item_id", item_id = item)[0]["item_name"]
            tempDict["item_id"] = item
            current_auctions.append(tempDict)

    # render html page with table of currently held stocks
    return render_template("auctions.html", current_auctions=current_auctions)


@app.route("/my_bids")
@login_required

def my_bids():
    "Displays items that the user is currently bidding on."
    user = session["user_id"]
    
    # select all of the user's bids 
    bids = db.execute("SELECT * FROM bids WHERE bidder_id = :user", user = user)

    item_ids = []
    for bid in bids:
        item_ids.append(bid["item_id"])
        
    # ensure each item id only appears once 
    items = list(set(item_ids))
    current_bids = []
    
    # iterate through items, creating a dictionary for each to store relevant data
    for item_id in items:
        tempDict = dict()
        item_status = db.execute("SELECT status FROM items WHERE item_id = :item_id", item_id = item_id)[0]["status"]
        if item_status == 1:
            tempDict["user_last_bid_amount"] = db.execute("SELECT bid_amount FROM bids WHERE item_id = :item_id AND bidder_id = :user ORDER BY timestamp DESC LIMIT 1", item_id = item_id, user = user)[0]["bid_amount"]
            tempDict["current_bid"] = db.execute("SELECT bid_amount FROM bids WHERE item_id = :item_id ORDER BY timestamp DESC LIMIT 1", item_id=item_id)[0]["bid_amount"]
            tempDict["item_name"] = db.execute("SELECT item_name FROM items WHERE item_id = :item_id", item_id = item_id)[0]["item_name"]
            tempDict["item_id"] = item_id
            current_bids.append(tempDict)
    if len(current_bids) == 0:
        return apology("You don't have any open bids!")

    # display user's current bids 
    return render_template("bids.html", current_bids=current_bids)
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")
        
        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")
        
        if not request.form.get("email"):
            return apology("must provide email address")
        
        # get user email
        user_email = request.form.get("email")
        
        # ensure he is from Yale
        if '@yale.edu' not in user_email:
            return apology("You Must Be A Yalie!")
        
        
        # ensure user insert Venmo
        if not request.form.get("venmo"):
            return apology("must provide Venmo username")
            
        # get venmo
        venmo_username = request.form.get("venmo")
        
        # remove "-" characters from input
        venmo_username = venmo_username.replace('@', '');
        
        # query database for username
        rows = db.execute("SELECT * FROM users WHERE user_id = :username OR email = :email", username=request.form.get("username"), email=user_email)
    
        # ensure username or email are already not being used
        if len(rows) == 1:
            return apology("username or email are already being used!")
        
        # ensure user input a password and the same password again
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords are not matching :(")
    
        # if everything is ok, register username and hashed password in our database
        user_id = db.execute("INSERT INTO users (username, hash, email, venmo) VALUES(:users, :hash, :email, :venmo)", users=request.form.get("username"), hash=pwd_context.encrypt(request.form.get("password")), email=user_email, venmo=venmo_username)
        
        # remember which user has logged in
        session["user_id"] = user_id
        
        # flash success message!
        flash("Registered!")
        
        # redirect user to home page
        return redirect(url_for("index"))
        
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
        

@app.route("/sales")
@login_required
def sales():
    
    # get user session
    user = session["user_id"]
    
    # get user's auctions that are already over
    past_sales = db.execute("SELECT * FROM items WHERE status = :expired AND seller_id = :user", expired=0, user=user)

    
    # if user has not sold anything before, return apology
    if len(past_sales) == 0:
        return apology("You have never sold an item before")
        
  
    
    for sale in past_sales:
        temp = db.execute("SELECT bidder_id from bids WHERE bid_amount = :bid AND item_id = :item_id", bid=sale["current_bid"], item_id=sale["item_id"])[0]["bidder_id"]
        sale["buyer_email"] = db.execute("SELECT email from users WHERE user_id = :user_id", user_id=temp)[0]["email"]
        
    return render_template("sales.html", past_sales=past_sales)

@app.route("/search")
def search():
    """Search for places that match query."""
    
    # check if valid query
    if not request.args.get("q"):
        raise RuntimeError("missing query")
     
    # get q argument passed into search as a get paramenter  
    q = request.args.get("q") + "%"
        
    # select places with postal code or name similar to that passed by argument q
    rows = db.execute("SELECT * FROM items WHERE item_name LIKE :q AND status=:live", q=q, live=1)
    
    # outputs resulting rows as JSON
    return jsonify(rows)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/sell",  methods=["GET", "POST"])
@login_required
def sell():
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # get user session 
        user = session["user_id"]

        # ensure user provides all needed info
        if not request.form.get("name"):
            return apology("must have name")
            
        # ensure user provides stock symbol
        if not request.form.get("description"):
            return apology("must have description")
        
        # ensure user provides start_price
        if not request.form.get("start_bid"):
            return apology("must have starting bid")
            
        # get the form info after checking
        auction_length = int(request.form.get("auction_length"))
        name = request.form.get("name")
        description = request.form.get("description")
        try: 
            start_bid = float(request.form.get("start_bid"))
        except ValueError:
            return apology("start bid must be numeric")
        # prepare to calculate timestamp_end
        difference = datetime.timedelta(days=auction_length)
        time_temp = datetime.datetime.utcnow() + difference
        time_now = time_temp.strftime('%Y-%m-%d %H:%M:%S')
        
        # insert into items database
        db.execute("INSERT INTO items (item_name, seller_id, start_bid, description, current_bid, timestamp_end, duration) VALUES(:name, :seller, :start_bid, :description, :start_bid, :time, :duration)", name=name, seller=user, start_bid=start_bid, description=description, time=time_now, duration=auction_length)

        # get created auction's id
        temp = db.execute("SELECT item_id FROM items WHERE seller_id = :user_id ORDER BY item_id DESC LIMIT 1", user_id=user)
        item_id = temp[0]["item_id"]
        
        item_row = db.execute("SELECT * FROM items WHERE item_id = :itm_id", itm_id=item_id)
        
        '''image file upload'''
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(str(item_id) + '.' + file.filename.rsplit('.', 1)[1])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        flash("Created Auction Successfully!")
        return redirect(url_for("itm_page", item_id=item_id))
    
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("sell.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
 

@app.route("/watchlist", methods=["GET", "POST"])
@login_required
def watchlist():
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        user = session["user_id"]
        
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        # get user session
        user = session["user_id"]
        
        # get user's watchlist
        watchlist_entries = db.execute("SELECT * FROM watchlist WHERE user_id = :user", user = user)
        
        # if user has no items in the watchlist return apology
        if len(watchlist_entries) == 0:
            return apology("Your watchlist is empty!")
        
        # else proceed to create his watchlist page
        watchlist_items = []
        for entry in watchlist_entries:
            item_id = entry["item_id"]
            item = db.execute("SELECT * from items WHERE item_id = :item_id", item_id=item_id)
            watchlist_items.append(item)
        return render_template("watchlist.html", watchlist_items=watchlist_items)
        


