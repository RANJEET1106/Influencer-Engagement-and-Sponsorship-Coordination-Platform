from flask import render_template, request,redirect,url_for
from flask_login import current_user
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from datetime import date

from application.models import User, Sponsor, Influencer, AdRequest, Campaign,db
from application.sponsor_filter import filter_campaigns,filter_influencers

def create_campaign():
    if request.method == 'GET':
        return render_template('sponsor/create_campaign.html')
    elif request.method == 'POST':
        sponsor_id = current_user.id
        name = request.form.get('name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        budget = int(request.form.get('budget'))
        visibility = request.form.get('visibility')
        catagory = request.form.get('catagory')
        niche = request.form.get('niche')
        
        new_campaign = Campaign(sponsor_id=sponsor_id, name=name, description=description,
                                start_date=start_date, end_date=end_date, budget=budget,
                                remaining_budget=budget,visibility=visibility,catagory=catagory,niche=niche)
        
        db.session.add(new_campaign)
        db.session.commit()
        return redirect(url_for('sponsor_campaign'))
    
def view_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return "Campaign not found", 404
    
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()
    influencer_ids = [ad_request.influencer_id for ad_request in ad_requests]
    influencers = Influencer.query.filter(Influencer.id.in_(influencer_ids)).all()
    
    return render_template('sponsor/view_campaign.html', campaign=campaign, influencers=influencers)

def edit_campaign(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    if not campaign:
        return "Campaign not found", 404

    if request.method == 'GET':
        return render_template('sponsor/edit_campaign.html', campaign=campaign)
    elif request.method == 'POST':
        old_budget = campaign.budget
        new_budget = int(request.form.get('budget'))
        temp=old_budget-campaign.remaining_budget
        if(new_budget<temp):
            return "budget Can't be less than amount spent"
        campaign.name = request.form.get('name')
        campaign.description = request.form.get('description')
        campaign.start_date = request.form.get('start_date')
        campaign.end_date = request.form.get('end_date')
        campaign.budget = int(request.form.get('budget'))
        campaign.remaining_budget = new_budget-temp
        campaign.visibility = request.form.get('visibility')
        db.session.commit()
        return redirect(url_for('sponsor_campaign'))
    
def delete_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return "Campaign not found", 404

    if request.method == 'GET':
        return render_template('sponsor/delete_campaign.html', campaign=campaign)
    if request.method == 'POST':
        db.session.delete(campaign)
        db.session.commit()
        AdRequest.query.filter_by(campaign_id=campaign_id).delete()
        db.session.commit()
        return redirect(url_for('sponsor_campaign'))