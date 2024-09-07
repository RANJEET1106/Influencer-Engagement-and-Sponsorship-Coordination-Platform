from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


# User Model
class User(UserMixin,db.Model):
    __tablename__='user'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password=db.Column(db.String,nullable=False)
    role=db.Column(db.String,nullable=False)   
    flag = db.Column(db.String, nullable=False , default='False')

    def get_id(self):
        return (self.id) 

# Sponsor model
class Sponsor(db.Model):
    __tablename__='sponsor'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    name =db.Column(db.String)
    companyname = db.Column(db.String, nullable=False)
    website = db.Column(db.String, default='Not Available') 

# Influencer model
class Influencer(db.Model):
    __tablename__='influencer'
    id = db.Column(db.Integer,db.ForeignKey('user.id'), primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    niche = db.Column(db.String, nullable=False)
    ytfollow = db.Column(db.Integer)
    ytlink = db.Column(db.String)
    instafollow = db.Column(db.Integer)
    instalink = db.Column(db.String)
    twitterfollow = db.Column(db.Integer)
    twitterlink = db.Column(db.String)
    totalcost = db.Column(db.Integer, nullable=False, default=0)
    count = db.Column(db.Integer, nullable=False, default=0)  
    
# Campaign model
class Campaign(db.Model):
    __tablename__='campaign'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    sponsor_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    start_date = db.Column(db.String, nullable=False)
    end_date = db.Column(db.String, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    remaining_budget = db.Column(db.Integer, nullable=False)
    visibility = db.Column(db.String, nullable=False)
    catagory = db.Column(db.String, nullable=False)
    niche = db.Column(db.String, nullable=False)
    flag = db.Column(db.String, nullable=False , default='False')

# AdRequest model
class AdRequest(db.Model):
    __tablename__='ad_request'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    request_to = db.Column(db.String, nullable=False) # Sponsor, Influencer
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    influencer_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.Column(db.String)
    requirements = db.Column(db.String, nullable=False)
    payment_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)  # Pending, Accepted, Rejected
    negotiation_amount = db.Column(db.Integer, nullable=True)  
    negotiation_status = db.Column(db.String, nullable=True) # Requested, Rejected
    date = db.Column(db.String, nullable=False)
