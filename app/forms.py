from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DecimalField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired

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
