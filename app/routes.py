from app import app, bcrypt, db
from flask import render_template, redirect, url_for, flash, request, jsonify, session
from app.forms import LoginForm, RegisterForm, UploadForm, EditProfileForm,\
	UpdateCoverPhotoForm, SearchForm
from app.models import User, Uploads, Follow, Wishlist, Bookmark
import secrets
from flask_login import login_user, logout_user, current_user
import secrets
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from sqlalchemy.sql.expression import func
from PIL import Image

@app.route("/login", methods=['POST', 'GET'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.login_email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember_me.data)
			return redirect(url_for('home'))
		else:
			flash("invalid username or password", "warning")
	return render_template('login.html', form=form)


@app.route("/register", methods=['POST', 'GET'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegisterForm()
	if form.validate_on_submit():
		hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		new_id = secrets.token_hex(5)
		check = User.query.filter_by(unique_id=new_id).first()
		if check:
			new_id = secrets.token_hex(5)
		new_user = User(username=form.register_username.data,\
			email=form.register_email.data, password=hash_password, unique_id=new_id)
		db.session.add(new_user)
		db.session.commit()
		return redirect(url_for('login'))
	return render_template('register.html', form=form)


@app.route("/", methods=["POST", "GET"])
def home():
	if current_user.is_authenticated:
		form = SearchForm()
		page = request.args.get('page', 1, type=int)
		all_uploads = Uploads.query\
			.order_by(func.random()).paginate(page, app.config['POST_PER_PAGE'], False)
		return render_template("index.html", all_uploads=all_uploads.items, form=form)
	else:
		flash("Flash Not Yet Logged In", "warning")
		return redirect(url_for('login'))

@app.route('/upload', methods=['POST', 'GET'])
def upload():
	if current_user.is_authenticated:
		form = UploadForm()
		user_uploads = Uploads.query.\
			filter_by(author=current_user).order_by(Uploads.date_posted.desc()).all()
		return render_template('upload.html', form=form, user_uploads=user_uploads)
	else:
		return redirect(url_for('login'))

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
	i = Image.open(form_picture)
	i.save(picture_path)
	return picture_fn

@app.route("/u/<string:name>", methods=["POST", "GET"])
def profile(name):
	if current_user.is_authenticated:
		form1 = UpdateCoverPhotoForm()
		if form1.validate_on_submit():
			picture_file = save_picture(form1.picture.data)
			current_user.image_file = picture_file
			db.session.commit()
			flash("Your cover photo has been updated successfuly")
			return redirect(url_for("profile", name=current_user.username))
		form = EditProfileForm()
		if form.validate_on_submit():
			current_user.username = form.name.data
			current_user.bio = form.bio.data 
			current_user.email = form.email.data	
			db.session.commit()
			flash("Account Updated Successfully")
			return redirect(url_for('profile', name=current_user.username))
		elif request.method == 'GET':
			form.name.data = current_user.username
			form.bio.data = current_user.bio
			form.email.data = current_user.email
		user = User.query.filter_by(username=name).first()
		if user:
			if user.username != current_user.username:
				return redirect(url_for('profile', name=current_user.username))
			return render_template("profile.html", form=form, len=len, form1=form1)
		return redirect(url_for('home'))
	else:
		flash("Not yet logged in", "danger")
		return redirect(url_for('login'))

@app.route("/o/<string:name>", methods=["POST", "GET"])
def others_profile(name):
	if current_user.is_authenticated:
		user = User.query.filter_by(username=name).first()
		if user == current_user:
			return redirect(url_for('profile', name=user.username))
		user_uploads = Uploads.query.filter_by(author=user)
		return render_template("user_profile.html", len=len, user=user,\
			user_uploads=user_uploads)
	else:
		return redirect(url_for('login'))

@app.route("/your/wishlist", methods=["POST", "GET"])
def yourwishlist():
	if current_user.is_authenticated:
		user_list = Uploads.query.order_by(Uploads.date_posted.desc()).all()
		return render_template('wish.html', user_list=user_list, len=len)
	else:
		return redirect(url_for('login'))


@app.route('/logout/')
def logout():
	if current_user.is_authenticated:
		logout_user()
		flash("Logout in successfull", "success")
		return redirect(url_for('login'))
	else:
		flash("Not yet logged in", 'warning')
		return redirect(url_for('login'))