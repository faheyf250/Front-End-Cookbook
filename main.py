from app import app

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


recipes_list = []


@app.route("/")
def home():
    return render_template("homepage.html")


@app.route("/recipes")
def recipes():
    return render_template("recipes.html", recipes=recipes_list)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/create_recipe", methods=["GET", "POST"])
def create_recipe():
    if request.method == "POST":
        title = request.form["title"]
        instructions = request.form["instructions"]

        ingredient_names = request.form.getlist("ingredient_name[]")
        ingredient_qtys = request.form.getlist("ingredient_qty[]")
        ingredient_units = request.form.getlist("ingredient_unit[]")

        image = request.files.get("recipe_image")

        ingredients = []
        for i in range(len(ingredient_names)):
            ingredients.append({
                "name": ingredient_names[i],
                "quantity": ingredient_qtys[i],
                "unit": ingredient_units[i]
            })

        recipe = {
            "title": title,
            "instructions": instructions,
            "ingredients": ingredients,
            "image_filename": image.filename if image and image.filename else None
        }

        recipes_list.append(recipe)

        return redirect(url_for("recipes"))

    return render_template("create_recipe.html")


if __name__ == "__main__":
    app.run(debug=True)