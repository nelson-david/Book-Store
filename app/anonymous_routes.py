from app import app, db
from flask import request, jsonify
from app.models import Uploads, User
from flask_login import current_user
from werkzeug.utils import secure_filename
import secrets
import os


@app.route("/bookmark", methods=["POST"])
def bookmark():
	if current_user.is_authenticated:
		upload = Uploads.query.filter_by(id=request.form['id1']).first()
		current_user.wishlist(upload)
		db.session.commit()
		return jsonify({'success' : 'true', 'like_num' : 3})

@app.route("/unbookmark", methods=["POST"])
def unbookmark():
	if current_user.is_authenticated:
		upload = Uploads.query.filter_by(id=request.form['id1']).first()
		current_user.unwishlist(upload)
		db.session.commit()
		return jsonify({'success' : 'true', 'like_num' : 3})


@app.route("/follow", methods=["POST"])
def follow():
	user = User.query.filter_by(username=request.form['username']).first()
	if user == current_user:
		return redirect(url_for('profile', name=current_user.username))
	current_user.follow(user)
	db.session.commit()

	return jsonify({'success' : 'true', 'like_num' : 3})

@app.route("/unfollow", methods=["POST"])
def unfollow():
	user = User.query.filter_by(username=request.form['username']).first()
	if user == current_user:
		return redirect(url_for('profile', name=current_user.username))
	current_user.unfollow(user)
	db.session.commit()

	return jsonify({'success' : 'true', 'like_num' : 3})


def change_file_name(name):
	file_name, file_ext = os.path.splitext(name)
	random_hex = secrets.token_hex(8)
	return f'{random_hex}{file_ext}'


@app.route("/upload_book/<name>/<desc>/", methods=["POST", "GET"])
def upload_book(name, desc):
	if request.method == "GET":
		return redirect(url_for('home'))
	file_s = request.files['file']
	names = name
	descs = desc

	filename = secure_filename(file_s.filename)
	file_1 = file_s.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

	new_id = secrets.token_hex(5)
	check = Uploads.query.filter_by(unique_id=new_id).first()
	if check:
		new_id = secrets.token_hex(5)
	new_upload = Uploads(name=names, description=descs,\
				book=filename, unique_id=new_id, author=current_user)
	db.session.add(new_upload)
	db.session.commit()
	return jsonify({'success' : 'true', 'like_num' : 3})