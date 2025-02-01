from models.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, redirect, url_for, flash, session,Blueprint
import matplotlib.pyplot as plt
import os


controllers = Blueprint('controllers', __name__)




# Home route
@controllers.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('controllers.view_posts'))
    return redirect(url_for('controllers.register'))

# Route for user registration
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

@controllers.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
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

# Route for admin login (separate route if needed)
@controllers.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email, roles='admin').first()
        if user and user.password == password:
            session['user_id'] = user.id  # Store user ID in session
            session['role'] = user.roles  # Store user role in session
            flash('Admin login successful!')
            return redirect(url_for('controllers.admin_dashboard'))
        else:
            flash('Admin login failed. Check your credentials and try again.')
    
    return render_template('admin_login.html')

# Route for admin dashboard
@controllers.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('You are not authorized to access this page.')
        return redirect(url_for('controllers.login'))
    
    # Fetch all flagged posts
    flagged_posts = Post.query.filter_by(flagged=True).all()
    # Fetch all users
    users = User.query.all()
    
    return render_template('admin_dashboard.html', flagged_posts=flagged_posts, users=users)

# Route for user dashboard
@controllers.route('/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.')
        return redirect(url_for('controllers.login'))

    # Fetch the current user's posts
    user_id = session['user_id']
    posts = Post.query.filter_by(user_id=user_id).all()

    return render_template('user_dashboard.html', posts=posts)

# Route for user logout
@controllers.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    session.pop('role', None)  # Remove user role from session
    flash('You have been logged out.')
    return redirect(url_for('controllers.login'))

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

# Route to view all posts
@controllers.route('/posts')
def view_posts():
    posts = Post.query.all()
    return render_template('view_posts.html', posts=posts)

# Route for editing a post
@controllers.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'user_id' not in session:
        flash('Please log in to edit a post.')
        return redirect(url_for('controllers.login'))
    
    post = Post.query.get_or_404(post_id)
    if post.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('You are not authorized to edit this post.')
        return redirect(url_for('controllers.view_posts'))

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash('Post updated successfully!')
        return redirect(url_for('controllers.view_posts'))
    
    return render_template('edit_post.html', post=post)

# Route for deleting a post
@controllers.route('/post/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session:
        flash('Please log in to delete a post.')
        return redirect(url_for('controllers.login'))
    
    post = Post.query.get_or_404(post_id)
    if post.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('You are not authorized to delete this post.')
        return redirect(url_for('controllers.view_posts'))

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!')
    return redirect(url_for('controllers.view_posts'))

# Route for flagging a post
@controllers.route('/post/flag/<int:post_id>', methods=['POST'])
def flag_post(post_id):
    if 'user_id' not in session:
        flash('Please log in to flag a post.')
        return redirect(url_for('controllers.login'))

    post = Post.query.get_or_404(post_id)
    if post.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('You are not authorized to flag this post.')
        return redirect(url_for('controllers.view_posts'))

    post.flagged = True
    db.session.commit()
    flash('Post flagged successfully!')
    return redirect(url_for('controllers.view_posts'))

# Route for unflagging a post
@controllers.route('/post/unflag/<int:post_id>', methods=['POST'])
def unflag_post(post_id):
    if 'user_id' not in session:
        flash('Please log in to unflag a post.')
        return redirect(url_for('controllers.login'))

    post = Post.query.get_or_404(post_id)
    if session.get('role') != 'admin':
        flash('You are not authorized to unflag this post.')
        return redirect(url_for('controllers.view_posts'))

    post.flagged = False
    db.session.commit()
    flash('Post unflagged successfully!')
    return redirect(url_for('controllers.view_posts'))

# Route for searching posts
@controllers.route('/search_posts', methods=['GET'])
def search_posts():
    title_query = request.args.get('title', '').strip()
    user_id_query = request.args.get('user_id', '').strip()
    
    query = Post.query

    if title_query:
        query = query.filter(Post.title.ilike(f'%{title_query}%'))
    if user_id_query:
        if user_id_query.isdigit():
            query = query.filter(Post.user_id == int(user_id_query))
        else:
            return "Invalid user ID. It must be a numeric value.", 400

    posts = query.all()
    return render_template('view_posts.html', posts=posts)

# Route for summary and graph
@controllers.route('/summary')
def summary():
    user_data = db.session.query(User.username, db.func.count(Post.id)).join(Post).group_by(User.id).all()
    
    usernames = [user[0] for user in user_data]
    post_counts = [user[1] for user in user_data]

    plt.figure(figsize=(10, 6))
    plt.bar(usernames, post_counts, color='skyblue')
    plt.xlabel('Usernames')
    plt.ylabel('Number of Posts')
    plt.title('Number of Posts per User')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    graph_path = os.path.join('static', 'user_posts_graph.png')
    plt.savefig(graph_path)
    plt.close()

    return render_template('summary.html', graph_url=url_for('static', filename='user_posts_graph.png'))


