from flask import Flask
from models.models import db, User
from controllers.controllers import controllers
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shridhar.sqlite'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize the database
db.init_app(app)

# Register the blueprint
app.register_blueprint(controllers)

# Function to create an admin user if it doesn't exist
def create_admin_user():
    with app.app_context():
        admin_email = 'admin@example.com'  # Hardcoded admin email
        admin_user = User.query.filter_by(email=admin_email).first()
        
        if not admin_user:
            admin_username = 'admin'
            admin_password = generate_password_hash('admin123', method='pbkdf2:sha256')  # Hardcoded admin password
            admin_user = User(username=admin_username, email=admin_email, password=admin_password, roles='admin')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")

# Initialize the database and create admin user
with app.app_context():
    db.create_all()
    create_admin_user()

if __name__ == '__main__':
    app.run(debug=True)
