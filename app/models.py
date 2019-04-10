from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime


@login.user_loader
def load_user(id):
    return Customer.query.get(int(id))


follows = db.Table("follows",
                   db.Column("customer_id", db.Integer, db.ForeignKey("customer.id"), primary_key=True),
                   db.Column("business_id", db.Integer, db.ForeignKey("business.id"), primary_key=True)
                   )


class Customer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(32), nullable=False)
    l_name = db.Column(db.String(32), nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    pass_hash = db.Column(db.String(128))
    user_inputs = db.relationship('UserInput', backref='Customer', lazy='dynamic')
    follows = db.relationship("Business", secondary=follows, lazy="dynamic", 
                                backref=db.backref("customers", lazy='dynamic'))

    def set_password(self, password):
        self.pass_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pass_hash, password)
    
    def follow(self, business):
        if not self.is_following(business.id):
            self.follows.append(business)

    def unfollow(self, business):
        if self.is_following(business.id):
            self.follows.remove(business)

    def is_following(self, business):
        return self.follows.filter_by(id=business).count() > 0

    def __repr__(self):
        return "<Customer %s>" % self.username


class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    zip_code = db.Column(db.Integer)
    customercounts = db.relationship('CustomerCount', backref='business', lazy='dynamic')
    predictions = db.relationship('Prediction', backref='business', lazy='dynamic')
    user_inputs = db.relationship('UserInput', backref='business', lazy='dynamic')

    def __repr__(self):
        return "<Business %s>" % self.name


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    wait_time = db.Column(db.Integer)
    wait_time_stddev = db.Column(db.Integer)

    def __repr__(self):
        return "<Prediction {} @ {}>".format(self.business_id, self.timestamp)


class UserInput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    wait_duration = db.Column(db.Integer)

    def __repr__(self):
        return "<User Input {} @ {}>".format(self.user_id, self.timestamp)


class CustomerCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    customer_count = db.Column(db.Integer)

    def __repr__(self):
        return "<Customer Count: Business: {}, Customers: {}, @ {}>".format(self.business_id, self.customer_count, self.timestamp)
