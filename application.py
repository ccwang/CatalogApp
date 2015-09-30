from flask import (Flask, render_template, request, redirect,
                   jsonify, url_for, flash, make_response)
from flask import session as login_session

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import random
import string
import httplib2
import requests
import json


app = Flask(__name__)

# Database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


@app.route('/login')
def showLogin():
    """Create anti-gorgery state token and show login page"""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Connect google"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'
    
    # see if user exists, if it doesn't make a new one
    try:
        user = session.query(User).filter_by(email=data['email']).one()
        user_id = user.id
    except:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """Disconnect a connected user."""
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/disconnect')
def disconnect():
    """Disconnect google"""
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showLatest'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showLatest'))


def createUser(login_session):
    """Create user and add to dababase"""
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def isLoggedin():
    """Check is logged in or not"""
    if 'username' in login_session:
        logged_in = True
    else:
        logged_in = False
    return logged_in


@app.route('/')
@app.route('/catalog')
def showLatest():
    """Show the latest items"""
    category = session.query(Category).all()
    items = session.query(Item).order_by(Item.create_date.desc())
    return render_template('catalog_latest.html', category = category, 
                           items = items, logged_in = isLoggedin())
    
    
@app.route('/catalog/<name>')
@app.route('/catalog/<name>/items')
def showCategory(name):
    """Show items in each category"""
    category = session.query(Category).all()
    category_id = session.query(Category).filter_by(name=name).first().id
    items = session.query(Item).filter_by(category_id = category_id).all()
    return render_template('catalog_category.html', category = category, 
                           name = name, items = items, nitem = len(items),
                           logged_in = isLoggedin())


@app.route('/catalog/<name>/items/<itemname>')
def showDescription(name, itemname):
    """Show the description of an item"""
    item = session.query(Item).filter_by(name = itemname).first()
    user = session.query(User).filter_by(id=item.user_id).one()    
    return render_template('catalog_description.html', item=item, 
                           logged_in = isLoggedin())


@app.route('/catalog/<itemname>/edit', methods=['GET', 'POST'])
def editItem(itemname): 
    """Page to edit item if the item is created by the user."""
    item = session.query(Item).filter_by(name = itemname).first()
    user = session.query(User).filter_by(id=item.user_id).one()
    category = session.query(Category).all()
    cat = session.query(Category).filter_by(id=item.category_id).first()
    
    if not isLoggedin():
        return redirect('/login')
    if login_session['email'] != user.email:
        flash("You cannot edit this item")
        return "<script>function myFunction() {alert('You are not authorized to edit this item.');}</script><body onload='myFunction()''>"
    
    if request.method == 'POST':
        item.name = request.form['item-name']
        item.description = request.form['item-description']        
        newcategory = request.form['item-category']
        item.categroy_id = session.query(Category).filter_by(name = newcategory).first().id
        session.commit()
        
        flash('Item %s is Successfully updated' % (item.name))
        return redirect(url_for('showDescription', name = newcategory, 
                                itemname=item.name))
    else:
        return render_template('edit.html', category=category, 
                               name=cat.name, item=item, 
                               logged_in = isLoggedin())  


@app.route('/catalog/add', methods=['GET', 'POST'])
def addItem():
    """Add new items to the database if user is logged in."""
    category = session.query(Category).all()
    user = session.query(User).filter_by(email=login_session['email']).one()
    
    if not isLoggedin():
        return redirect('/login')    
        
    if request.method == 'POST':
        newcategory = request.form['item-category']
        newitemname = request.form['item-name']
        newdescription = request.form['item-description']
        
        if newcategory != '' and newitemname != '':
            cat = session.query(Category).filter_by(name = newcategory).first()
            if cat is None:
                cat = Category(user_id = user.id, name = newcategory)
                session.add(cat)
                session.commit()
            newitem = Item(user_id=user.id, name = newitemname, 
                description = newdescription,
                category = cat)
            session.add(newitem)
            session.commit()
            flash('New %s Item Successfully added' % (newitemname))
            return redirect(url_for('showDescription', name=newcategory, 
                                    itemname=newitem.name))
        else:
            return "<script>function myFunction() {alert('Category or item name is missing!');}</script><body onload='myFunction()''>"
    else:
        return render_template('add.html', logged_in = isLoggedin()) 


@app.route('/catalog/<itemname>/delete', methods=['GET', 'POST'])
def deleteItem(itemname):
    """Delete item if the item is created by the user."""
    item = session.query(Item).filter_by(name=itemname).first()
    user = session.query(User).filter_by(id=item.user_id).one()
    
    if not isLoggedin():
        return redirect('/login')
    if login_session['email'] != user.email:
        return "<script>function myFunction() {alert('You are not authorized to delete this item.');}</script><body onload='myFunction()''>"
    
    if request.method == 'POST':
        session.delete(item)
        flash('%s Successfully Deleted' % item.name)
        session.commit()
        return redirect(url_for('showLatest'))
    else:
        return render_template('delete.html', item=item, 
                               logged_in = isLoggedin())


@app.route('/catalog.json')
def catalogJSON():
    """Show json of category and items"""
    catalog = session.query(Category).all()
    items = session.query(Item).all()
    return jsonify(Category=[cat.serialize for cat in catalog],
                   Item = [item.serialize for item in items])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)