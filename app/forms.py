from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, Optional
from flask_wtf.file import FileField, FileAllowed
from app.models import User
from flask_login import current_user

class RegisterForm(FlaskForm):
	register_username = StringField("Name", validators=[DataRequired(), Length(min=5, max=12)],\
		render_kw={'placeholder':'Username'})
	register_email = StringField("Email", validators=[DataRequired()],\
	 	render_kw={'placeholder':'Email'})
	password = PasswordField("Password", validators=[DataRequired(),\
	 	Length(min=5, message="Password must not be less than 5")],\
	 	render_kw={'placeholder':'Password'})
	confirm_password = PasswordField("Confirm Password",\
	 	validators=[EqualTo("password", message="Passwords do not match")],\
	 	render_kw={'placeholder':'Confirm Password'})

	def validate_username(self, username):
		user = User.query.filter_by(username=register_username.data).first()
		if user:
			raise ValidationError("This username is already taken")

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError("This email is already taken")


class LoginForm(FlaskForm):
	login_email = StringField("Email", validators=[DataRequired(), Email()],\
	 	render_kw={'placeholder':'Email'})
	password = PasswordField("Password", validators=[DataRequired(),\
	 	Length(min=5, message="Password must not be less than 5")],\
	 	render_kw={'placeholder':'Password'})
	remember_me = BooleanField("Remember me")

class UploadForm(FlaskForm):
	name = StringField("Name Of Book", validators=[DataRequired(), Length(min=4, max=25)],\
		render_kw={'placeholder':'Name Of Book', "id":"name"})
	description = TextAreaField("Book Description", validators=[DataRequired(),\
		Length(min=30, max=120)],\
		render_kw={'placeholder':'Book Description', 'id':"desc"})
	book = FileField("Book", validators=[FileAllowed(['pdf']), DataRequired()],\
		render_kw={'id':'pdf', 'hidden':'true'})


class EditProfileForm(FlaskForm):
	name = StringField("Name", validators=[Optional(), Length(min=5, max=12)],\
		render_kw={'placeholder':'Username'})
	email = StringField("Email", validators=[Optional(), Email()],\
		render_kw={'placeholder':'Email'})

	bio = TextAreaField("Bio", validators=[Optional(), Length(max=100)],\
		render_kw={'placeholder':'Bio', 'rows':1, 'cols': 30})

	def validate_username(self, username):
		user = User.query.filter_by(username=name.data).first()
		if current_user.name == name.data:
			pass
		else:
			if user:
				raise ValidationError("This username is already taken")

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if current_user.email == email.data:
			pass
		else:
			if user:
				raise ValidationError("This email is already in use")

class UpdateCoverPhotoForm(FlaskForm):
	picture = FileField("Update Profile Picture",\
		validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg']),\
		DataRequired()],\
		render_kw={})
	submit = SubmitField("save")


class SearchForm(FlaskForm):
	content = StringField("Search", validators=[DataRequired()],\
		render_kw={'placeholder':'Search For Books', 'type':'search'})


class RequestResetForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired(), Email()],\
	 	render_kw={'placeholder':'Enter Your Email Address'})

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			return ValidationError("There is no account with that email")


class ResetPasswordForm(FlaskForm):
	password = PasswordField("Password", validators=[DataRequired(),\
	 	Length(min=5, message="Password must not be less than 5")],\
	 	render_kw={'placeholder':'Password'})
	confirm_password = PasswordField("Confirm Password",\
	 	validators=[EqualTo("password", message="Passwords do not match")],\
	 	render_kw={'placeholder':'Confirm Password'})