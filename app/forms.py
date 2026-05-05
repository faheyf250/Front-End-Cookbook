from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, SubmitField, 
DecimalField, SelectField, FieldList, FormField, PasswordField)
from wtforms.validators import DataRequired, Email, Length, Regexp

class IngredientForm(FlaskForm):
    class Meta: 
        csrf = False # Critical for nested forms
    ingredient_name = StringField('ingredient Name', validators = [DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired()])
    unit = SelectField('Unit', choices=[
        ('g', 'Grams'), ('oz','Ounces'), ('cup','Cups'),('tbsp','Tablespoons'), ('tsp', 'Teaspoons'),
    ])

class RecipeForm(FlaskForm):
    title = StringField('Recipe Title', validators=[DataRequired()])
    ingredients = FieldList(FormField(IngredientForm), min_entries = 1)
    instructions = TextAreaField('Preparation Steps', validators=[DataRequired()])
    submit = SubmitField('Post Recipe')

#login FlaskForm

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(),
        Email()
    ])

    password = PasswordField("Password", validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters."),
        Regexp(
            r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$",
            message="Error! Password must include a letter, number, and special character."
        )
    ])

