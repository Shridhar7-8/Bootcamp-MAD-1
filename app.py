from flask import Flask
from controllers.controllers import controllers
from models.models import *


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///thivya.db"
app.config['SECRET_KEY'] = "thivya"


db.init_app(app) # Initialize the database with the app

app.register_blueprint(controllers)

def create_admin():
    with app.app_context():
        admin_email = "admin@example.com"
        admin_user = User.query.filter_by(email = admin_email).first()
        if not admin_user:
            admin_username = "admin"
            admin_password = "admin123"
            admin_user = User(username=admin_username, email=admin_email, password = admin_password, roles="admin")
            db.session.add(admin_user)
            db.session.commit()
            print("Admin created successfully")
        else:
            print("Admin already exists")



with app.app_context():
    db.create_all()
    create_admin()



if __name__ == "__main__":
    app.run(debug=True)