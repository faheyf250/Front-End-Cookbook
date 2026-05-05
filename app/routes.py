from flask import render_template, flash, url_for, redirect, request, session
from app import app, db 
from app.models import Recipe, User
from app.forms import RecipeForm, LoginForm

##this is for password revoery
import os
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
##This is for the image uploading & password validator##

from werkzeug.utils import secure_filename 
from werkzeug.security import generate_password_hash, check_password_hash
##----------------------------------------##
def send_reset_code(email, code):
    sender_email = os.environ.get("MAIL_USERNAME")
    sender_password = os.environ.get("MAIL_PASSWORD")

    if not sender_email or not sender_password:
        print(f"Password reset code for {email}: {code}")
        return

    message = EmailMessage()
    message["Subject"] = "Front End Cookbook Password Reset Code"
    message["From"] = sender_email
    message["To"] = email
    message.set_content(
        f"Your Front End Cookbook password reset code is: {code}\n\n"
        "This code will expire in 10 minutes."
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(message)

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/home")
def home():
    top_recipes = Recipe.query.filter(
        Recipe.rating > 0
    ).order_by(
        Recipe.rating.desc()
    ).limit(3).all()

    return render_template("homepage.html", top_recipes=top_recipes)

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

       # r.formatted_ingredients = formatted_ingredients
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
            session["user_id"] = user.id
            session["first_name"] = user.first_name
            session["last_name"] = user.last_name
            session["user_initials"] = user.first_name[0].upper() + user.last_name[0].upper()

            return redirect(url_for("home"))

        return render_template(
            "login.html",
            email=email,
            email_accepted=True,
            password_error=True
        )

    return render_template("login.html")

@app.route("/create_recipe", methods=["GET", "POST"])
def create_recipe():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title")
        instructions = request.form.get("instructions")

        quantities = request.form.getlist("quantity[]")
        units = request.form.getlist("unit[]")
        ingredients = request.form.getlist("ingredient[]")

        ingredient_parts = []

        for quantity, unit, ingredient in zip(quantities, units, ingredients):
            quantity = quantity.strip()
            unit = unit.strip()
            ingredient = ingredient.strip()

            if ingredient == "":
                continue

            ingredient_parts.append(f"{quantity} {unit} {ingredient}".strip())

        ingredient_string = " | ".join(ingredient_parts)

        image_file = request.files.get("recipe_image")
        image_filename = None

        if image_file and image_file.filename != "":
            if allowed_file(image_file.filename):
                image_filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
                image_file.save(image_path)

        if isinstance(ingredient_string, list):
            ingredient_string = " | ".join(
                f"{item.get('quantity', '')} {item.get('unit', '')} {item.get('name', '')}".strip()
                for item in ingredient_string
    )
        new_recipe = Recipe(
            title=title,
            ingredients=ingredient_string,
            instructions=instructions,
            image_filename=image_filename,
            user_id=session["user_id"]
        )

        db.session.add(new_recipe)
        db.session.commit()

        return redirect(url_for("recipes"))

    return render_template("create_recipe.html")

#Page to view individual recipe
@app.route("/recipe/<int:recipe_id>")
def view_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    #recipe.formatted_ingredients = format_ingredients(recipe.ingredients)

    return render_template("view_recipe.html", recipe=recipe)

# Search page using the database
@app.route("/search")
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

        if r.ingredients:
            for item in r.ingredients.split(" | "):
                parts = item.split(" ", 2)
                formatted_ingredients.append({
                    "quantity": parts[0] if len(parts) > 0 else "",
                    "unit": parts[1] if len(parts) > 1 else "",
                    "name": parts[2] if len(parts) > 2 else ""
                })

       # r.formatted_ingredients = formatted_ingredients

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

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/delete_recipe/<int:recipe_id>", methods=["POST"])
def delete_recipe(recipe_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    recipe = Recipe.query.get_or_404(recipe_id)

    if recipe.user_id != session["user_id"]:
        return redirect(url_for("recipes"))

    db.session.delete(recipe)
    db.session.commit()

    return redirect(url_for("recipes"))

def format_ingredients(ingredients_string):
    formatted_ingredients = []

    if not ingredients_string:
        return formatted_ingredients

    for item in ingredients_string.split(" | "):
        item = item.strip()

        if item == "":
            continue

        parts = item.split(" ", 2)

        formatted_ingredients.append({
            "quantity": parts[0] if len(parts) > 0 else "",
            "unit": parts[1] if len(parts) > 1 else "",
            "name": parts[2] if len(parts) > 2 else ""
        })

    return formatted_ingredients

@app.route("/fork_recipe/<int:recipe_id>", methods=["POST"])
def fork_recipe(recipe_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    original_recipe = Recipe.query.get_or_404(recipe_id)

    forked_recipe = Recipe(
        title=original_recipe.title + " copy",
        ingredients=original_recipe.ingredients,
        instructions=original_recipe.instructions,
        image_filename=original_recipe.image_filename,
        rating=0,
        user_id=session["user_id"],
        forked_from_id=original_recipe.id
    )

    db.session.add(forked_recipe)
    db.session.commit()

    return redirect(url_for("edit_recipe", recipe_id=forked_recipe.id))

@app.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    recipe = Recipe.query.get_or_404(recipe_id)

    if recipe.user_id != session["user_id"]:
        return redirect(url_for("recipes"))

    if request.method == "POST":
        title = request.form.get("title")
        instructions = request.form.get("instructions")

        quantities = request.form.getlist("quantity[]")
        units = request.form.getlist("unit[]")
        ingredients = request.form.getlist("ingredient[]")

        ingredient_parts = []

        for quantity, unit, ingredient in zip(quantities, units, ingredients):
            quantity = quantity.strip()
            unit = unit.strip()
            ingredient = ingredient.strip()

            if ingredient == "":
                continue

            ingredient_parts.append(f"{quantity} {unit} {ingredient}".strip())

        recipe.title = title
        recipe.instructions = instructions
        recipe.ingredients = " | ".join(ingredient_parts)

        image_file = request.files.get("recipe_image")

        if image_file and image_file.filename != "":
            if allowed_file(image_file.filename):
                image_filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
                image_file.save(image_path)
                recipe.image_filename = image_filename

        db.session.commit()

        return redirect(url_for("view_recipe", recipe_id=recipe.id))

    #recipe.formatted_ingredients = format_ingredients(recipe.ingredients)

    return render_template("edit_recipe.html", recipe=recipe)


##password recovery
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No account found with that email.")
            return redirect(url_for("forgot_password"))

        reset_code = str(random.randint(100000, 999999))

        session["reset_email"] = email
        session["reset_code"] = reset_code
        session["reset_code_expires"] = (
            datetime.now() + timedelta(minutes=10)
        ).isoformat()

        send_reset_code(email, reset_code)

        flash("A password reset code was sent to your email.")
        return redirect(url_for("verify_reset_code"))

    return render_template("forgot_password.html")


@app.route("/verify_reset_code", methods=["GET", "POST"])
def verify_reset_code():
    if request.method == "POST":
        entered_code = request.form.get("code", "").strip()
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        saved_email = session.get("reset_email")
        saved_code = session.get("reset_code")
        expires_at = session.get("reset_code_expires")

        if not saved_email or not saved_code or not expires_at:
            flash("Password reset session expired. Please try again.")
            return redirect(url_for("forgot_password"))

        if datetime.now() > datetime.fromisoformat(expires_at):
            session.pop("reset_email", None)
            session.pop("reset_code", None)
            session.pop("reset_code_expires", None)

            flash("Reset code expired. Please request a new code.")
            return redirect(url_for("forgot_password"))

        if entered_code != saved_code:
            flash("Invalid reset code.")
            return redirect(url_for("verify_reset_code"))

        if len(new_password) < 8:
            flash("Password must be at least 8 characters long.")
            return redirect(url_for("verify_reset_code"))

        if new_password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("verify_reset_code"))

        user = User.query.filter_by(email=saved_email).first()

        if not user:
            flash("Account could not be found.")
            return redirect(url_for("forgot_password"))

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        session.pop("reset_email", None)
        session.pop("reset_code", None)
        session.pop("reset_code_expires", None)

        flash("Password updated successfully. Please log in.")
        return redirect(url_for("login"))

    return render_template("verify_reset_code.html")
