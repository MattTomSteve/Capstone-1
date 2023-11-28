from flask import Flask, render_template, request, redirect, flash, session, g, jsonify
import requests
from models import db, connect_db, User, Cocktail, Ingredient, Glass, Comment, Like, CocktailIngredient, CocktailGlass
from forms import UserAddForm, UserLoginForm, CocktailAddForm, UserEditForm
from sqlalchemy.exc import IntegrityError
API_BASE_URL = 'https://www.thecocktaildb.com/api/json/v1/1'
import ast

CURR_USER_KEY = 'curr_user'

key = '1'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///capstone_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'abc123'

connect_db(app)
# db.create_all()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.before_request
def add_user_to_g():

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    
    session[CURR_USER_KEY] = user.id

def do_logout():

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserAddForm()
    if form.validate_on_submit():
        try:
            user = User.register(
                username = form.username.data,
                pwd = form.pwd.data,
                email=form.email.data,
                img_url=form.img_url.data)
            db.session.commit()
        
        except IntegrityError:
            flash('Username unavailable', 'danger')
            return render_template('/register.html', form=form)
        
        do_login(user)

        return redirect('/')
    
    else:
        return render_template('/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                form.password.data)
        
        if user:
            do_login(user)
            return redirect('/cocktails')
        
        else:
            flash('Invalid Username/Password', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('curr_user')
    return redirect('/')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route('/')
def home():
    return render_template('cocktails.html')

@app.route('/cocktails')
def show_cocktails():
    return render_template('cocktails.html')
    
@app.route('/cocktail_search')
def get_cocktail():
    try:
        cocktailsearch = request.args.get('cocktailsearch')
        res = requests.get(f'{API_BASE_URL}/search.php', params={'s' : cocktailsearch})
        # import pdb
        # pdb.set_trace()
    # move logic below into own function
        data = res.json()
        cocktails = data.get('drinks', []) if data['drinks'] else None
        cocktail_info = [{'name': cocktail.get('strDrink'), 'image': cocktail.get('strDrinkThumb'), 'id': cocktail.get('idDrink')} for cocktail in cocktails]
        return render_template('cocktails.html', cocktail_info=cocktail_info)
    except:
        flash("Sorry, could not find cocktail!", 'danger')
        return render_template('cocktails.html')

@app.route('/cocktail_details/<int:cocktail_id>')
def cocktail_details(cocktail_id):
    
    res = requests.get(f'{API_BASE_URL}/lookup.php', params={'i' : cocktail_id})
# move logic below into own function
    data = res.json()
    cocktails = data.get('drinks', []) if data['drinks'] else None
    cocktail_info = [{'name': cocktail.get('strDrink'), 
                      'image': cocktail.get('strDrinkThumb'), 
                      'id': cocktail.get('idDrink'),
                      'glass': cocktail.get('strGlass'),
                      'instructions': cocktail.get('strInstructions')} for cocktail in cocktails]

    return render_template('cocktail_details.html', cocktail_info=cocktail_info)

@app.route('/ingredient_search')
def get_ingredient():
    try:
        ingredientsearch = request.args.get('ingredientsearch')
        res = requests.get(f'{API_BASE_URL}/filter.php', params={'i' : ingredientsearch})
        data = res.json()
        cocktails = data.get('drinks', []) if data['drinks'] else None
        cocktail_info = [{'name': cocktail.get('strDrink'), 'image': cocktail.get('strDrinkThumb'), 'id': cocktail.get('idDrink')} for cocktail in cocktails]
        return render_template('cocktails.html', cocktail_info=cocktail_info)
    except:
        flash("Sorry, could not find cocktail!", 'danger')
        return render_template('cocktails.html')

@app.route('/save_cocktail', methods=['POST'])
def save_new_cocktail():

    if not g.user:
        flash("Saving for members only, please log in.", "danger")
        return redirect("/login")

    try:
        cocktail = request.form['saved']
        dictionary_object = ast.literal_eval(cocktail)

        new_cocktail = Cocktail.save(dictionary_object, session['curr_user'])
        db.session.add(new_cocktail)
        db.session.commit()
        # print(request.form['saved'])
        flash('Cocktail saved to profile!', 'success')
        return redirect('/cocktails')
    except IntegrityError as e:
        db.session.rollback()
        error_info = str(e.orig)
        if 'duplicate key value violates unique constraint' in error_info:
            flash("Cocktail with this name already saved", 'error')
        else:
            flash("An error occured while saving cocktail", 'error')
   
    return redirect('/')

@app.route('/add_cocktail', methods=['GET', 'POST'])
def add_cocktail():
    
    if not g.user:
        flash("Please log in.", "danger")
        return redirect("/login")
    
    form = CocktailAddForm()

    if form.validate_on_submit():
        try:
            name = form.name.data
            glass = form.glass.data
            instructions = form.instructions.data
            img_url = form.img_url.data

            new_cocktail = Cocktail(name=name, instructions=instructions, glass=glass, img_url=img_url)
            
            new_cocktail.user_id = session['curr_user']

            db.session.add(new_cocktail)
            db.session.commit()
            flash('Cocktail added!', 'success')
            
        except IntegrityError as e:
            db.session.rollback()
            error_info = str(e.orig)
            if 'duplicate key value violates unique constraint' in error_info:
                flash("Cocktail with this name already added", 'error')
            else:
                flash("An error occured while adding cocktail", 'error')

        return redirect('/add_cocktail')

    return render_template('add_cocktail.html', form=form)

@app.route('/profile/<int:user_id>')
def user_profile(user_id):
    if g.user:
        return render_template('profile.html', user=g.user)
    else:
        flash('Please log in', 'danger')
        return redirect('/login')
    
# @app.route('/profile/<int:user_id>/edit', endpoint='user_edit', methods=['POST'])
# def user_profile(user_id):
#     if not g.user:
#         flash('Please log in.', 'danger')
#         return redirect('/login')
#     form = UserEditForm(obj=g.user)

    

@app.route('/profile/<int:user_id>/delete', endpoint='user_delete', methods=['POST'])
def user_profile(user_id):
    if not g.user:
        flash('Please log in.', 'danger')
        return redirect('login')
    
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()

    flash ('Account deleted!', 'success')
    return redirect('/')
    
@app.route('/user_cocktails/<int:cocktail_id>')
def user_cocktail(cocktail_id):
    if g.user:
        cocktail = Cocktail.query.get(cocktail_id)
        return render_template('user_cocktail.html', user=g.user, cocktail=cocktail)
    else:
        flash('Please log in', 'danger')
        return redirect('/login')

@app.route('/user_cocktails/<int:cocktail_id>/delete', endpoint='cocktail_delete', methods=['POST'])
def user_cocktail_delete(cocktail_id):
    if not g.user:
        flash('Please log in.', 'danger')
        return redirect('/login')

    cocktail = Cocktail.query.get(cocktail_id)
    db.session.delete(cocktail)
    db.session.commit()

    flash('Cocktail deleted!', 'success')
    return redirect('/')


# @app.route('/users/<user_id>')

# @app.route('/')
# def index():
#     cocktails = Cocktail.query.all()
#     return render_template('index.html', cocktails=cocktails)

# @app.route('/search', methods=['POST'])
# def search():
#     cocktail_name = request.form.get('cocktail')
#     res = requests.get(f'{API_BASE_URL}/search.php', params={'s': cocktail_name})
#     data = res.json()

#     if 'drinks' in data:
#         cocktails_data = data['drinks']
#         cocktails = [Cocktail(name=cocktail['strDrink']) for cocktail in cocktails_data]
#         db.session.add_all(cocktails)
#         db.session.commit()
#         flash(f'Found {len(cocktails)} cocktails with the name: {cocktail_name}', 'success')
#     else:
#         flash(f'No cocktails found with the name: {cocktail_name}', 'danger')

#     return redirect(url_for('index')