from flask import render_template, url_for, redirect, request
from app import app, db 
from app.models import Recipe, User
from app.forms import RecipeForm, LoginForm

##This is for the image uploading & password validator##
import os 
from werkzeug.utils import secure_filename 
from werkzeug.security import generate_password_hash, check_password_hash
##----------------------------------------##


UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/home")
def home():
    return render_template("homepage.html")

#Page that displays all recipes
@app.route("/recipes")
def recipes():
    recipes = Recipe.query.all()
    #Code I have added for now until database is in place. This is only a temporary fix that will be removed.
    #Code provides formatting to the recipes . code can stay
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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user is None:
            return render_template(
                "login.html",
                email=email,
                email_accepted=False
            )

        if password is None or password == "":
            return render_template(
                "login.html",
                email=email,
                email_accepted=True
            )

        if user.check_password(password):
            return redirect(url_for("home"))
        else:
            return render_template(
                "login.html",
                email=email,
                email_accepted=True,
                password_error=True
            )

    return render_template("login.html")

@app.route('/create_recipe', methods=['GET','POST'])
def create_recipe():
#created recipe should now be stored in the database, and viewable on receipes page
    if request.method == 'POST':
        title = request.form.get('title')
        instructions = request.form.get('instructions')

        ingredient_names = request.form.getlist('ingredient_name[]')
        ingredient_qtys = request.form.getlist('ingredient_qty[]')
        ingredient_units = request.form.getlist('ingredient_unit[]')

        ingredients_list  = []
        for qty, unit, name in zip(ingredient_qtys, ingredient_units, ingredient_names):
            ingredient_text = f"{qty} {unit} {name}".strip()
            ingredients_list .append(ingredient_text)

        ing_string = " | ". join(ingredients_list)

        ##Handling of the image files##
        image_file = request.files.get('recipe_image')
        filename = None

        if image_file and image_file.filename != '': ##Checks for a name
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) ##Saves file data
            
        ##----------------------------------------------##
        
        new_recipe = Recipe(
	    title = title,
            ingredients = ing_string,
            instructions=instructions,
            image_filename=filename
        )

        db.session.add(new_recipe)
        db.session.commit()

        return redirect(url_for('recipes'))
    return render_template('create_recipe.html')

#Page to view individual recipe
@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    formatted_ingredients = []
    for item in recipe.ingredients.split(" | "):
        parts = item.split(" ", 2)
        formatted_ingredients.append({
            'quantity': parts[0] if len(parts) > 0 else "",
            'unit': parts[1] if len(parts) > 1 else "",
            'name': parts[2] if len(parts) > 2 else ""
        })

    recipe.ingredients = formatted_ingredients

    return render_template('view_recipe.html', recipe=recipe)

#Search page using the database
@app.route('/search')
def search():
    query = request.args.get("q", "").strip()

    if query:
        recipes = Recipe.query.filter(
            Recipe.title.ilike(f"%{query}%") |
            Recipe.ingredients.ilike(f"%{query}%") |
            Recipe.instructions.ilike(f"%{query}%")
        ).all()
    else:
        recipes = Recipe.query.all()

    for r in recipes:
        formatted_ingredients = []

        for item in r.ingredients.split(" | "):
            parts = item.split(" ", 2)
            formatted_ingredients.append({
                'quantity': parts[0] if len(parts) > 0 else "",
                'unit': parts[1] if len(parts) > 1 else "",
                'name': parts[2] if len(parts) > 2 else ""
            })

        r.ingredients = formatted_ingredients

    return render_template(
        "recipes.html",
        recipes=recipes,
        search_query=query
    )

@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return render_template(
                "create_account.html",
                error="An account with that email already exists."
            )

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("create_account.html")

@app.route("/rate_recipe/<int:recipe_id>", methods=["POST"])
def rate_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    rating = request.form.get("rating")

    if rating:
        recipe.rating = int(rating)
        db.session.commit()

    return redirect(url_for("recipes"))
