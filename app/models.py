from app import db

# Define the DB schema
class Recipe(db.Model):
    __tablename__='recipes'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)


    def __repr__(self):
        return self.title

