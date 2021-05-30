from flask import render_template, flash, redirect, url_for, request, abort
from MicroBlog.forms import Signup, Login, Up_date, PostForm, RequestResetForm, ResetPasswordForm
from MicroBlog import app, db, bcrypt, mail
from MicroBlog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from flask_mail import Message
from MicroBlog import response, sports


news_data = response.json()
sports_news = sports.json()
news = news_data['articles']
spo_info = sports_news['articles']
k = len(news)
l = len(spo_info)
@app.route('/')
@login_required
def home():

    page = request.args.get('page', 1, type= int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("home.html" , title = 'Home', posts = posts, news=news, k=k, spo_info=spo_info, l=l)

@app.route('/signup', methods =['GET', 'POST'])
def sign_up():
    form = Signup()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(first_name = form.fname.data, last_name = form.lname.data, email = form.email.data,
                    password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created', 'success')
        return redirect(url_for('home'))
    return render_template("signup.html", form = form, title = 'Sign Up Page')

@app.route('/login', methods =['GET', 'POST'])
def log_in():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Login()
    user = User.query.filter_by(email = form.email.data).first()
    if form.validate_on_submit():
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Unsuccessful Login!!. try again!!!')
    return render_template("login.html", form = form, title = 'Login Page')
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('log_in'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)

    return picture_fn

@app.route('/updateprofile', methods =['GET', 'POST'])
@login_required
def update_profile():
    form = Up_date()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.first_name = form.fname.data
        current_user.last_name = form.lname.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account Updated')
        return redirect(url_for('update_profile'))
    elif request.method == 'GET':
        form.fname.data = current_user.first_name
        form.lname.data = current_user.last_name
        form.email.data = current_user.email
        imagefile = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template("updateprofile.html", title = 'Update Profile',imagefile = imagefile, form=form )

@app.route('/profile', methods =['GET', 'POST'])
@login_required
def profile():
    form = Up_date()
    imagefile = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template("profile.html", title = 'Profile Page',imagefile = imagefile, form=form)




@app.route('/post/new', methods =['GET', 'POST'])
@login_required
def new_post():
    form =PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, content = form.content.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created')
        return redirect(url_for('home'))
    return render_template("create_post.html", title = 'New Post', form=form, legend = 'New Post')

@app.route('/post/<post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title = post.title, post=post)

@app.route('/post/<post_id>/update', methods =['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user :
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been Updated", 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title = 'Update Post', form = form, legend = 'Update Post')


@app.route('/post/<post_id>/delete', methods =['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted", 'success')
    return redirect(url_for('home'))

@app.route("/user/<string:first_name>")
def user_posts(first_name):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(first_name=first_name).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


def send_reset_email(user):

    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)


@app.route('/reset_password', methods =['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("Email has been sent with instructions to change the password", 'info')
        return redirect(url_for('log_in'))
    return render_template('reset_request.html', title= 'Reset Password', form=form)

@app.route('/reset_password/<token>', methods =['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user =User.verify_reset_token(token)
    if user is None:
        flash("that is invalid or expired token", 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated', 'success')
        return redirect(url_for('home'))
    return render_template('reset_token.html', title= 'Reset Password', form=form)
