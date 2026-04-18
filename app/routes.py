from flask import render_template, url_for, redirect, request
from app import app, db 
from app.models import Recipe
from app.forms import RecipeForm



@app.route("/")
def home():
    return render_template("homepage.html")

#Pagee that displays all recipes
@app.route("/recipes")
def recipes():
    recipes = Recipe.query.all()
    #Code I have added for now until database is in place. This is only a temporary fix that will be removed.
    for r in recipes: 
        formatted_ingredients = []
        for item in r.ingredients.split(' | '):
            parts = item.split(' ', 2) 

            formatted_ingredients.append({
                'quantity': parts[0] if len(parts) > 0 else "",
                'unit': parts[1] if len(parts) > 1 else "",
                'name': parts[2] if len(parts) > 2 else ""
            })

        r.ingredients = formatted_ingredients
     ########--------------------------############## 
    return render_template("recipes.html", recipes=recipes)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/create_recipe', methods=['GET','POST'])
def create_recipe():
    form = RecipeForm()

    if request.method == 'POST' and 'add_ingredient' in request.form:
        form.ingredients.append_entry()
        return render_template('create_recipe.html', form=form)

    if form.validate_on_submit():
        #This code will also be changed in order to conform to the database, right now it is just old code
        ing_data = [f"{i['amount']} {i['unit']} {i['ingredient_name']}" for i in form.ingredients.data]
        ing_string = " | ".join(ing_data)

        new_recipe = Recipe(
            title=form.recipe_name.data, 
            ingredients=ing_string,
            instructions=form.instructions.data
        )
        ####-----------------##########
        db.session.add(new_recipe)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('create_recipe.html', form=form)

#Page to view individual recipe
@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('view_recipe.html', recipe=recipe)

