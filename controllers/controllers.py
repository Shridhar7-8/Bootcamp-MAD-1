from models.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, redirect, url_for, flash, session,Blueprint
import matplotlib.pyplot as plt
import os


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


@controllers.route("/view_posts",methods=['GET'])
def view_posts():
    posts = Post.query.all()
    return render_template('view_posts.html',posts=posts)


@controllers.route("/post/edit/<int:post_id>",methods=['GET','POST'])
def edit_post(post_id):
    if 'user_id' not in session:
        flash('Please log in to edit a post.')
        return redirect(url_for('controllers.login'))
    
    post = Post.query.get(post_id)
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


@controllers.route("/post/delete/<int:post_id>",methods=['GET'])
def delete_post(post_id):
    if 'user_id' not in session:
        flash('Please log in to delete a post.')
        return redirect(url_for('controllers.login'))
    
    post = Post.query.get(post_id)
    if post.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('You are not authorized to delete this post.')
        return redirect(url_for('controllers.view_posts'))
    
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!')
    return redirect(url_for('controllers.view_posts'))


@controllers.route("/post/flag/<int:post_id>",methods=['GET'])
def flag_post(post_id):
    if 'user_id' not in session:
        flash('Please log in to flag a post.')

    post = Post.query.get(post_id)

    if post.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('You are not authorized to flag this post.')
        return redirect(url_for('controllers.view_posts'))
    
    post.flagged = True
    db.session.commit()
    flash('Post flagged successfully!')
    return redirect(url_for('controllers.view_posts'))


@controllers.route("/post/unflag/<int:post_id>",methods=['GET'])
def unflag_post(post_id):
    if 'user_id' not in session:
        flash('Please log in to unflag a post.')

    post = Post.query.get(post_id)

    if post.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('You are not authorized to unflag this post.')
        return redirect(url_for('controllers.view_posts'))
    
    post.flagged = False
    db.session.commit()
    flash('Post unflagged successfully!')
    return redirect(url_for('controllers.view_posts'))

@controllers.route("/search_posts",methods=['GET','POST'])
def search_posts():
    title_query = request.args.get('title','').strip()
    user_id_query = request.args.get('user_id','').strip()

    query = Post.query

    if title_query:
        query = query.filter(Post.title.ilike(f'%{title_query}%'))
    if user_id_query:
        if user_id_query.isdigit():
            query = query.filter(Post.user_id == int(user_id_query))
        else:
            flash('Invalid user ID. Please enter a valid number.')
    posts = query.all()
    return render_template('view_posts.html', posts=posts)

@controllers.route("/summary")
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


    graph_path = os.path.join('static','user_post_summary.png')
    plt.savefig(graph_path)
    plt.close()

    return render_template('summary.html', url_for('static', filename='user_post_summary.png'))
