from flask import render_template, url_for, redirect, request
from app import app, db 
from app.models import Recipe
from app.forms import RecipeForm

@app.route('/dashboard')
def dashboard():
    recipes = Recipe.query.all()
    return render_template('base.html', recipes=recipes)

@app.route('/create_recipe', methods=['GET','POST'])
def create_recipe():
    form = RecipeForm()

    if request.method == 'POST' and 'add_ingredient' in request.form:
        form.ingredients.append_entry()
        return render_template('create_recipe.html', form=form)

    if form.validate_on_submit():
        ing_data = [f"{i['amount']} {i['unit']} {i['ingredient_name']}" for i in form.ingredients.data]
        ing_string = " | ".join(ing_data)

        new_recipe = Recipe(
            title=form.recipe_name.data, 
            ingredients=ing_string,
            instructions=form.instructions.data
        )

        db.session.add(new_recipe)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('create_recipe.html', form=form)

@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('view_recipe.html', recipe=recipe)
