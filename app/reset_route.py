from app import app, mail, bcrypt, db
from flask import render_template, redirect, url_for, flash
from app.models import User
from app.forms import ResetPasswordForm, RequestResetForm
from flask_login import current_user
from flask_mail import Message

@app.route("/reset/password", methods=["POST", "GET"])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			token = user.get_reset_token()
			msg = Message("Hello", sender="ogwunelsondavid@gmail.com", recipients=[user.email])
			msg.body = f'''Click on the link to reset your password f{url_for('reset_token', token=token, _external=True)}'''
			mail.send(msg)
			flash("An email has has been sent with instructions to reset your password", "info")
			return redirect(url_for('login'))
		else:
			flash(f"There is no account registered with\
				this email, register{url_for('login')}", "warning")
	return render_template("reset_request.html", form=form)


@app.route("/reset/password/<token>", methods=["POST", "GET"])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash("That is an invalid or expired token ", "warning")
		return redirect(url_for('reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hash_password
		db.session.commit()
		flash("Your password has been updated !", "info")
		return redirect(url_for('login'))
	return render_template("reset_password.html", form=form)