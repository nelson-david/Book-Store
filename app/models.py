from app import db, login_manager, app
from flask_login import UserMixin, current_user
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class Follow(db.Model):
	__tablename__ = "follows"
	follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
	followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Wishlist(db.Model):
	__tablename__ = "wishlists"
	wishlister_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
	wishlisted_id = db.Column(db.Integer, db.ForeignKey('uploads.id'), primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True, unique=True)
	username = db.Column(db.String(), unique=True, nullable=False)
	email = db.Column(db.String(), unique=True, nullable=False)
	password = db.Column(db.String(), unique=True, nullable=False)
	bio = db.Column(db.String(), nullable=True)
	unique_id = db.Column(db.String(30), unique=True, nullable=False)
	date_joined = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
	image_file = db.Column(db.String(30), nullable=False, default='default.jpg')
	uploads = db.relationship("Uploads", backref="author", lazy=True)
	bookmark = db.relationship("Bookmark", backref="saver", lazy=True)

	followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],\
		backref=db.backref('follower', lazy='joined'), lazy='dynamic',\
		cascade='all, delete-orphan')
	followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],\
		backref=db.backref('followed', lazy='joined'), lazy='dynamic',\
		cascade='all, delete-orphan')

	wishlisted = db.relationship('Wishlist', foreign_keys=[Wishlist.wishlister_id],\
		backref=db.backref('added', lazy='joined'), lazy='dynamic',\
		cascade='all, delete-orphan')

	def get_reset_token(self, expires_sec=1800):
		s = Serializer(app.config["SECRET_KEY"], expires_sec)
		return s.dumps({'user_id' : self.id}).decode('utf-8')


	@staticmethod
	def verify_reset_token(token):
		s = Serializer(app.config["SECRET_KEY"])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None

		return User.query.get(user_id)


	def __repr__(self):
		return f'{self.username}, {self.email}'

	def follow(self, user):
		if not self.is_following(user):
			f = Follow(follower=self, followed=user)
			db.session.add(f)

	def unfollow(self, user):
		f = self.followed.filter_by(followed_id=user.id).first()
		if f:
			db.session.delete(f)

	def is_following(self, user):
		return self.followed.filter_by(followed_id=user.id).first() is not None

	def is_followed_by(self, user):
		return self.followers.filter_by(follower_id=user.id).first() is not None

	def wishlist(self, user):
		if not self.is_wishlisting(user):
			f = Wishlist(added=self, adder=user)
			db.session.add(f)

	def unwishlist(self, user):
		f = self.wishlisted.filter_by(wishlisted_id=user.id).first()
		if f:
			db.session.delete(f)

	def is_wishlisting(self, user):
		return self.wishlisted.filter_by(
			wishlisted_id=user.id).first() is not None

	def all_wishlist(self):
		return self.wishlisted.filter_by(wishlister_id=self.id).all() is not None




class Uploads(db.Model):
	id = db.Column(db.Integer, primary_key=True, unique=True)
	name = db.Column(db.String(20), nullable=False)
	description = db.Column(db.String(110), nullable=False)
	book = db.Column(db.String(30), nullable=False)
	unique_id = db.Column(db.String(30), unique=True, nullable=False)
	date_posted = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	bookmark = db.relationship("Bookmark", backref="saved", lazy=True)

	def __repr__(self):
		return f'{self.name}, {self.description}, {self.book}, {self.book_icon},\
			{self.date_posted}'

	wishlisters = db.relationship('Wishlist', foreign_keys=[Wishlist.wishlisted_id],\
		backref=db.backref('adder', lazy='joined'), lazy='dynamic',\
		cascade='all, delete-orphan')


	def is_wishlisted_by(self, user):
		return self.wishlisters.filter_by(
			wishlister_id=user.id).all()

class Bookmark(db.Model):
	id = db.Column(db.Integer, primary_key=True, unique=True)
	date_added = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	upload_id = db.Column(db.Integer, db.ForeignKey('uploads.id'), nullable=False)
	uploads_unique = db.Column(db.String(), unique=True, nullable=False)


	def __repr__(self):
		return f'{self.saver}, {self.saved}'