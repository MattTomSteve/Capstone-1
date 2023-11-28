from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FieldList, FormField
from wtforms.validators import DataRequired, Email, Length, InputRequired, Optional

# class CommentForm(FlaskForm):
    
class UserAddForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    pwd = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    email = StringField('Email', validators=[InputRequired()])
    img_url = StringField('Image URL')

class UserLoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])

class CocktailAddForm(FlaskForm):
    name = StringField('Cocktail Name', validators=[InputRequired(), Length(max=50)])
    instructions = TextAreaField('Instructions', validators=[InputRequired(), Length(max=200)])
    glass = StringField('Preferred Glass', validators=[InputRequired()])
    # look into FieldList and FormField for the ingredients
    img_url = StringField('Add Image URL')

class UserEditForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired()])
    img_url = StringField('Image URL')
    
# class IngredientAddForm(FlaskForm):



