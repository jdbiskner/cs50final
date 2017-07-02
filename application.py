"""SQL Create table statement
CREATE TABLE 'transactions' ('transactionID' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'stock' TEXT NOT NULL, 
'shares' INTEGER NOT NULL, 'price' REAL NOT NULL, 'transaction_total' REAL NOT NULL, 'type' TEXT NOT NULL)
"""



from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    
    # store the users current portfolio and cash available cash
    stocks = db.execute("SELECT * FROM view_portfolio WHERE user_id = :user_id", user_id=session["user_id"])
    total_cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
    
    
    # grab stock information for stocks in portfolio
    for stock in stocks:
        
        # store lookup information on stock
        holding = lookup(stock["stock"])
        
        # update dict with name, price, and total value of stock
        stock["name"] = holding["name"]
        stock["price"] = usd(holding["price"])
        stock["total"] = usd(stock["shares"] * float(holding["price"]))
        
    # render table containg stock information
    return render_template("index.html", stocks=stocks, cash=usd(total_cash[0]["cash"]))

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    
    # if user reaches route via POST
    if request.method == "POST":
        
        # check for blank field and negative number of shares
        if request.form.get("shares", 0) == '':
            return apology("enter number of shares")
        elif int(request.form.get("shares")) < 1:
            return apology("enter positive number of shares")
            
        # store the stock and number of shares
        stock = lookup(request.form.get("stock"))
        shares = int(request.form.get("shares"))
        
        # check for a valid stock
        if stock == None:
            return apology("stock not known")
        
        # check to see that the user has enough cash
        rows = db.execute("SELECT cash FROM users WHERE ID = :user_id", user_id=session["user_id"])
        if len(rows) != 1:
            return apology("user not found")
        if rows[0]["cash"] < (stock["price"] * shares):
            return apology("not enough cash")
        
        # log the transaction in the transactions table
        db.execute("INSERT INTO transactions (stock, shares, price, transaction_total, type, user_id) VALUES (:stock, :shares, :price, :transaction_total, :Type, :user_id)", stock=stock["symbol"], shares=shares, price=stock["price"], transaction_total=(shares*stock["price"]), Type='BUY', user_id=session["user_id"] )
        
        # update the user's cash
        db.execute("UPDATE users SET cash = :total WHERE id = :user_id", total=(rows[0]["cash"] - (shares*stock["price"])) , user_id=session["user_id"])
        
        # redirect to index 
        return redirect(url_for("index"))       
        
    # if user reaches route via GET
    else:
        return render_template("buy.html")
    
@app.route("/history")
@login_required
def history():
    """Show history of transactions."""

    # get transactions from database
    transactions = db.execute("SELECT type, stock, price, shares, transaction_date FROM transactions WHERE user_id = :user_id ORDER BY transaction_date", user_id=session["user_id"])
    
    # send transactions to page
    return render_template("history.html", transactions=transactions)

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
        session["user_id"] = rows[0]["id"]

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

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    
    # if route reached via POST, return stock quote
    if request.method == "POST":
        
        # store the stock quote
        quoted = lookup(request.form.get("stock"))
        
        # check to verify symbol was verified
        if quoted == None:
            return apology("Stock symbol is not known")
        
        # show the price of the stock
        return render_template("quoted.html", name=quoted["name"], price=usd(quoted["price"]), symbol=quoted["symbol"])
    
    # if route was reached via GET, return the form
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    
    if request.method == "POST":
        
        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # ensure password_retype was submitted
        elif not request.form.get("password_retype"):
            return apology("must retype password")

        # ensure password and password_retype match
        elif request.form.get("password") != request.form.get("password_retype"):
            return apology("passwords do not match")

        # encrypt password pwd_contxt.encrypt(request.form.get("password")
        
        # write username and password to database
        result = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=pwd_context.encrypt(request.form.get("password")))
        
        # check if user already exists
        if not result:
            return apology("username already exists")
            
        # remember which user has logged in
        row = db.execute("SELECT id FROM users WHERE username like :username", username=request.form.get("username"))
        session["user_id"] = row[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    
    # implement the insert such that it registers the number of shares as a negative number.
    # this will make the view the sums these easier
    
    if request.method == "POST":
        
        # do some error checks to verify fields were filled and user has enough cash.
        # check for blank field and negative number of shares
        if request.form.get("shares", 0) == '':
            return apology("enter number of shares")
        elif int(request.form.get("shares")) < 1:
            return apology("enter positive number of shares")
            
        # store the stock and number of shares
        stock = lookup(request.form.get("stock"))
        shares = int(request.form.get("shares"))
        
        # check for a valid stock
        if stock == None:
            return apology("stock not known")
        
        # check to see that the user has enough shares
        rows = db.execute("SELECT shares FROM view_portfolio WHERE user_id = :user_id AND stock like :stock_symbol", user_id=session["user_id"], stock_symbol=stock["symbol"])
        if len(rows) != 1:
            return apology("user not found")
        if rows[0]["shares"] < int(request.form.get("shares")):
            return apology("not enough shares")
    
        usercash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
        
        # log the transaction in the transactions table
        db.execute("INSERT INTO transactions (stock, shares, price, transaction_total, type, user_id) VALUES (:stock, :shares, :price, :transaction_total, :Type, :user_id)", stock=stock["symbol"], shares=(shares * -1), price=stock["price"], transaction_total=(shares*stock["price"]), Type='SELL', user_id=session["user_id"] )
        
        # update the user's cash
        db.execute("UPDATE users SET cash = :total WHERE id = :user_id", total=(usercash[0]["cash"] + (shares*stock["price"])) , user_id=session["user_id"])
        
        # send them back to the homepage
        return redirect(url_for("index"))
    
    # if user reached page by GET method
    else:
        return render_template("sell.html")
        
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    
    # if the user reached method via POST
    if request.method == "POST":
        
        # validate all fields have been entered
        if not request.form.get("currentpass"):
            return apology("enter current password")
            
        elif not request.form.get("newpass"):
            return apology("enter new password")
        
        elif not request.form.get("retypepass"):
            return apology("re-type password")
        
        # validate currentpass was correct
        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session["user_id"])
        if not pwd_context.verify(request.form.get("currentpass"), rows[0]["hash"]):
            return apology("invalid current password")
        
        # validate newpass and retypepass match
        if not request.form.get("newpass") == request.form.get("retypepass"):
            return apology("passwords do not match")
    
        # update database with new password. 
        db.execute("UPDATE users SET hash = :hash WHERE id = :user_id", hash=pwd_context.encrypt(request.form.get("newpass")), user_id=session["user_id"])
        
        return redirect(url_for("index"))
        
    # if user reached method via GET    
    else:
        return render_template("change_password.html")
        
        
        # TODO, index fields, however that's done