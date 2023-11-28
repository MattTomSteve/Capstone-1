from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)
    app.app_context().push()

class User(db.Model):

    __tablename__ = 'users'
# Add autoincrement? Look up u uid
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    email = db.Column(db.Text, unique=True)
    # add default image
    img_url = db.Column(db.Text)

    comments = db.relationship('Comment', backref='user')
    likes = db.relationship('Like', backref='user')
    
    def __repr__(self):
        return f'<User {self.id}, {self.username}, {self.email}'
    
    @classmethod
    def register(cls, username, pwd, email, img_url):
        '''Register User w/hashed password and return user.'''

        hashed = bcrypt.generate_password_hash(pwd)
        hashed_utf8 = hashed.decode('utf8')

        # return instance of user w/username and hashed pwd
        u = User(username=username, password=hashed_utf8, email=email, img_url=img_url)
    
        db.session.add(u)
        return u
    
    @classmethod
    def authenticate(cls, username, password):
        '''Validate that user exists and password is correct'''
        '''Returns user if valid; else returns False'''

        u = cls.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False
    
class Cocktail(db.Model):

    __tablename__ = 'cocktails'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Text, nullable=False, unique=True)
# add default image
    img_url = db.Column(db.Text)

    desc = db.Column(db.Text)

    glass = db.Column(db.Text)

    ingredient = db.Column(db.Text)

    instructions = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # comments = db.relationship('Comment', backref='cocktail')
    # likes = db.relationship('Like', backref='cocktail')
    # ingredients = db.relationship('CocktailIngredient', backref='cocktail')
    # glasses = db.relationship('CocktailGlass', backref='cocktail')
    users = db.relationship('User', backref='cocktail')

    @classmethod
    def save(cls, cocktail, user_id):
        return cls(name=cocktail['name'], img_url=cocktail['image'],
                   glass=cocktail['glass'], instructions=cocktail['instructions'], user_id=user_id)

class Ingredient(db.Model):

    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Text, nullable=False, unique=True)

    type = db.Column(db.Text, nullable=False)

class Glass(db.Model):

    __tablename__ = 'glasses'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Text, nullable=False, unique=True)

    size = db.Column(db.Integer, nullable=False)

class Comment(db.Model):

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)

    text = db.Column(db.String(200), nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))

    cocktail_id = db.Column(db.Integer, db.ForeignKey('cocktails.id', ondelete='cascade'))

class Like(db.Model):

    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))

    cocktail_id = db.Column(db.Integer, db.ForeignKey('cocktails.id', ondelete='cascade'))

class CocktailIngredient(db.Model):

    __tablename__ = 'cocktail_ingredients'

    cocktail_id = db.Column(db.Integer, db.ForeignKey('cocktails.id'), primary_key=True)

    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)

class CocktailGlass(db.Model):

    __tablename__ = 'cocktail_glasses'

    cocktail_id = db.Column(db.Integer, db.ForeignKey('cocktails.id'), primary_key=True)

    glass_id = db.Column(db.Integer, db.ForeignKey('glasses.id'), primary_key=True)

