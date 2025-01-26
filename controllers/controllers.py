from models.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, redirect, url_for, flash, session,Blueprint


controllers = Blueprint('controllers', __name__)




@controllers.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email,role='admin').first()
        if user and check_password_hash(user.password, password):
            session['user_id']=user.id
            session['role'] = user.roles
            flash("Admin login Succesful")
            return redirect(url_for('controllers.admin_dashboard'))
        else:
            flash("Admin login failed, check your credentials")
    return render_template('admin_login.html')

#user login
@controllers.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  # Store user ID in session
            session['role'] = user.roles  # Store user role in session
            flash('Login successful!')
            if user.roles == 'admin':
                return redirect(url_for('controllers.admin_dashboard'))
            else:
                return redirect(url_for('controllers.user_dashboard'))  # Redirect to user dashboard
        else:
            flash('Login failed. Check your credentials and try again.')
    
    return render_template('login.html')

#registration

@controllers.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully! Please log in.')
        return redirect(url_for('controllers.login'))
    
    return render_template('registration.html')



#user dashboard 
@controllers.route('/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.')
        return redirect(url_for('controllers.login'))

    # Fetch the current user's posts
    user_id = session['user_id']
    posts = Post.query.filter_by(user_id=user_id).all()

    return render_template('user_dashboard.html', posts=posts)


# Route for creating a post
@controllers.route('/post/create', methods=['GET', 'POST'])
def create_post():
    if 'user_id' not in session:
        flash('Please log in to create a post.')
        return redirect(url_for('controllers.login'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session['user_id']

        new_post = Post(title=title, content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully!')
        return redirect(url_for('controllers.view_posts'))
    
    return render_template('create_post.html')


# Route for user logout
@controllers.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    session.pop('role', None)  # Remove user role from session
    flash('You have been logged out.')
    return redirect(url_for('controllers.login'))

