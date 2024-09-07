from flask import Flask, redirect, request, render_template, url_for,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, and_
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from datetime import date
from os import urandom


from application.models import Sponsor,Influencer,AdRequest,Campaign,User,db
from application.registration import registration,influencer_registration,sponsor_registration
from application.auth import login_logic, logout_logic
from application.sponsor import *
from application.sponsor_campaign import create_campaign,view_campaign,edit_campaign,delete_campaign
from application.sponsor_adRequest import sponsor_adRequest,campaign_adRequest,adRequest,view_adRequest,cancel_adRequest,accept_adRequest,reject_adRequest,accept_negotiation,reject_negotiation
from application.influencer import influencerDashboard, campaign_find, ad_requests, influencer_generate_charts
from application.influencer_adRequest import view_ad,cancel_ad,accept_ad,reject_ad,create_ad,negotiate_ad
from application.admin import adminDashboard, adminFind, viewUser, viewCampaign, flagUser, flagCampaign, removeUser, removeCampaign, admin_generate_charts

app = Flask(__name__)
app.secret_key=urandom(24)
bcrypt=Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iescp.sqlite3'

db.init_app(app)
app.app_context().push()
db.create_all()

login_manager=LoginManager()
login_manager.login_view='auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

## COMMON ROUTES

@app.route('/',methods=['GET','POST'])
def login():
    return login_logic()

@app.route('/register',methods=['GET','POST'])
def register():
    return registration()

@app.route('/regsponsor',methods=['GET','POST'])
def regsponsor():
    return sponsor_registration()

@app.route('/reginfluencer',methods=['GET','POST'])
def regifluencer():
    return influencer_registration()

@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    return logout_logic()


## ADMIN ROUTES

@app.route('/admin/dashboard',methods=['GET'])
@login_required
def admin_dashboard():
    return adminDashboard()

@app.route('/admin/find',methods=['GET','POST'])
@login_required
def admin_find():
    return adminFind()

@app.route('/admin/stats')
@login_required
def admin_stats():
    return admin_generate_charts()

@app.route('/admin/campaign/view/<campaign_id>')
@login_required
def view_admin_campaign(campaign_id):
    return viewCampaign(campaign_id)

@app.route('/admin/user/view/<user_id>')
@login_required
def view_user(user_id):
    return viewUser(user_id)

@app.route('/admin/user/flag/<user_id>')
@login_required
def flag_user(user_id):
    return flagUser(user_id)

@app.route('/admin/campaign/flag/<campaign_id>')
@login_required
def flag_campaign(campaign_id):
    return flagCampaign(campaign_id)

@app.route('/admin/user/remove/<user_id>',methods=['GET','POST'])
@login_required
def remove_user(user_id):
    return removeUser(user_id)

@app.route('/admin/campaign/remove/<campaign_id>',methods=['GET','POST'])
@login_required
def remove_campaign(campaign_id):
    return removeCampaign(campaign_id)
          
## SPONSOR ROUTES

@app.route('/sponsor/dashboard',methods=['GET'])
@login_required
def sponsor_dashboard():
    return sponsorDashboard()

@app.route("/sponsor/campaign",methods=['GET','POST'])
@login_required
def sponsor_campaign():
    return campaigns()

@app.route('/sponsor/campaign/create',methods=['GET','POST'])
@login_required
def sponsor_create_campaign():
    return create_campaign()

@app.route('/sponsor/campaign/view/<campaign_id>',methods=['GET','POST'])
@login_required
def sponsor_view_campaign(campaign_id):
    return view_campaign(campaign_id)

@app.route('/sponsor/campaign/edit/<campaign_id>',methods=['GET','POST'])
@login_required
def sponsor_edit_campaign(campaign_id):
    return edit_campaign(campaign_id)

@app.route('/sponsor/campaign/delete/<campaign_id>',methods=['POST','GET'])
@login_required
def sponsor_delete_campaign(campaign_id):
    return delete_campaign(campaign_id)

@app.route('/sponsor/campaign/ad_request/<campaign_id>',methods=['GET','POST'])
@login_required
def sponsor_create_ad_request(campaign_id):
    return sponsor_adRequest(campaign_id)

@app.route('/sponsor/find',methods=['GET','POST'])
@login_required
def sponsor_influencer_find():
    return influencer_find()

@app.route('/sponsor/influencer/view/<influencer_id>',methods=['GET'])
@login_required
def sponsor_influencer_view(influencer_id):
    return influencer_view(influencer_id)

@app.route('/sponsor/influencer/ad_request/create/<influencer_id>',methods=['GET','POST'])
@login_required
def sponsor_adRequest_create(influencer_id):
    return sponsor_adRequest(influencer_id)

@app.route('/sponsor/campaign/ad_request/create/<campaign_id>',methods=['GET','POST'])
@login_required
def campaign_adRequest_create(campaign_id):
    return campaign_adRequest(campaign_id)

@app.route('/sponsor/ad_request/create/<influencer_id>/<campaign_id>', methods=['GET','POST'])
@login_required
def adRequest_create(influencer_id,campaign_id):
    return adRequest(influencer_id,campaign_id)

@app.route('/sponsor/ad_request',methods=['GET','POST'])
@login_required
def display_adRequest():
    return ad_Requests()

@app.route('/sponsor/ad_request/view/<ad_request_id>',methods=['GET'])
@login_required
def sponsor_view_adRequest(ad_request_id):
    return view_adRequest(ad_request_id)

@app.route('/sponsor/ad_request/cancel/<int:ad_request_id>', methods=['GET'])
@login_required
def sponsor_cancel_adRequest(ad_request_id):
    return cancel_adRequest(ad_request_id)

@app.route('/sponsor/ad_request/accept/<int:ad_request_id>', methods=['GET'])
@login_required
def sponsor_accept_adRequest(ad_request_id):
    return accept_adRequest(ad_request_id)

@app.route('/sponsor/ad_request/reject/<int:ad_request_id>', methods=['GET'])
@login_required
def sponsor_reject_adRequest(ad_request_id):
    return reject_adRequest(ad_request_id)

@app.route('/sponsor/ad_request/accept_negotiation/<int:ad_request_id>', methods=['GET'])
@login_required
def sponsor_accept_negotiation(ad_request_id):
    return accept_negotiation(ad_request_id)

@app.route('/sponsor/ad_request/reject_negotiation/<int:ad_request_id>', methods=['GET'])
@login_required
def sponsor_reject_negotiation(ad_request_id):
    return reject_negotiation(ad_request_id)

@app.route('/sponsor/stats',methods=['GET'])
@login_required
def sponsor_stats():
    return sponsor_generate_charts()

# INFLUENCER ROUTS

@app.route('/influencer/dashboard',methods=['GET'])
@login_required
def influencer_dashboard():
    return influencerDashboard()

@app.route('/influencer/find',methods=['GET','POST'])
@login_required
def influencer_campaign_find():
    return campaign_find()

@app.route('/influencer/ad_request',methods=['GET','POST'])
@login_required
def influencer_ad_request():
    return ad_requests()

@app.route('/influencer/stats')
@login_required
def influencer_stats():
    return influencer_generate_charts()

@app.route('/influencer/ad_request/create/<campaign_id>',methods=['GET','POST'])
@login_required
def influencer_create_adRequest(campaign_id):
    return create_ad(campaign_id)

@app.route('/influencer/ad_request/view/<ad_request_id>',methods=['GET'])
@login_required
def influencer_view_adRequest(ad_request_id):
    return view_ad(ad_request_id)

@app.route('/influencer/ad_request/cancel/<int:ad_request_id>', methods=['GET'])
@login_required
def influencer_cancel_adRequest(ad_request_id):
    return cancel_ad(ad_request_id)

@app.route('/influencer/ad_request/accept/<int:ad_request_id>', methods=['GET'])
@login_required
def influencer_accept_adRequest(ad_request_id):
    return accept_ad(ad_request_id)

@app.route('/influencer/ad_request/reject/<int:ad_request_id>', methods=['GET'])
@login_required
def influencer_reject_adRequest(ad_request_id):
    return reject_ad(ad_request_id)

@app.route('/influencer/ad_request/negotiate/<ad_request_id>', methods=['GET','POST'])
@login_required
def influencer_negotiate_request(ad_request_id):
    return negotiate_ad(ad_request_id)

if __name__ == '__main__':
    app.run(debug=True)