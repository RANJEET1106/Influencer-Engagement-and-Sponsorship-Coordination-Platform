from flask import render_template, request,redirect,url_for
from flask_login import current_user
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from datetime import date

from application.models import User, Sponsor, Influencer, AdRequest, Campaign,db
from application.sponsor_filter import filter_campaigns,filter_influencers

def sponsor_adRequest(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
            return "Influencer Not Found", 404
    
    if request.method=='GET':        
        campaigns=Campaign.query.all()        
        return render_template('sponsor/influencer_ad.html',influencer=influencer,campaigns=campaigns)
    
    if request.method=='POST':
        status = request.form.get('status')
        visibility = request.form.get('visibility')
        flag = 'False'
        search = request.form.get('search', '')
        campaigns = filter_campaigns(status, visibility, flag, search)
        return render_template('sponsor/influencer_ad.html', campaigns=campaigns,influencer=influencer,
                               status=status, visibility=visibility, search=search)
    
def campaign_adRequest(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if (not campaign):
        return "Campaign Not Found",404
    
    if campaign.flag=='True':
        return "Can't Put Request For Flagged Campaigns",403
    
    if request.method=='GET':
        influencers=Influencer.query.all()
        return render_template('sponsor/campaign_ad.html',campaign=campaign,influencers=influencers)

    if request.method=='POST':
        category = request.form.get('category')
        niche = request.form.get('niche')
        min_yt_followers = request.form.get('min_yt_followers')
        max_yt_followers = request.form.get('max_yt_followers')
        min_insta_followers = request.form.get('min_insta_followers')
        max_insta_followers = request.form.get('max_insta_followers')
        min_twitter_followers = request.form.get('min_twitter_followers')
        max_twitter_followers = request.form.get('max_twitter_followers')
        search = request.form.get('search')

        influencers = filter_influencers(category, niche,min_yt_followers, max_yt_followers,
                                 min_insta_followers, max_insta_followers,
                                 min_twitter_followers, max_twitter_followers,search)

        return render_template('sponsor/campaign_ad.html', influencers=influencers,campaign=campaign,
                           category=category, niche=niche,
                           min_yt_followers=min_yt_followers, max_yt_followers=max_yt_followers,
                           min_insta_followers=min_insta_followers, max_insta_followers=max_insta_followers,
                           min_twitter_followers=min_twitter_followers, max_twitter_followers=max_twitter_followers,
                           search=search)

def adRequest(influencer_id,campaign_id):
    influencer = Influencer.query.get(influencer_id)
    campaign = Campaign.query.get(campaign_id)
    if (not influencer  or not campaign):
        return "Influencer or Campaign Not Found",404
    
    if request.method=='GET':
        return render_template('sponsor/adRequest.html',campaign_id=campaign_id,influencer_id=influencer_id)
    
    if request.method=='POST':
        messages = request.form.get('messages')
        requirements = request.form.get('requirements')
        payment_amount = int(request.form.get('payment_amount'))
        sponsor_id = current_user.id

        if (payment_amount>int(campaign.remaining_budget)):
            return "Can't Put Request as the remaining budget is less than payment amount"

        new_ad_request = AdRequest(
            request_to='Influencer',
            campaign_id=campaign_id,
            sponsor_id=sponsor_id,
            influencer_id=influencer_id,
            messages=messages,
            requirements=requirements,
            payment_amount=payment_amount,
            status='Pending',
            date = date.today()
        )

        db.session.add(new_ad_request)
        db.session.commit()
        campaign.remaining_budget-=payment_amount
        db.session.commit()
        return redirect(url_for('sponsor_dashboard'))
    
def view_adRequest(adRequest_id):
    ad_request=AdRequest.query.get(adRequest_id)
    if not ad_request :
        return 'Ad Reuest Not Found',404
    
    if request.method=='GET':
        return render_template('influencer/view_ad_request.html',ad_request=ad_request)
    
def cancel_adRequest(ad_request_id):
    ad_request = AdRequest.query.get(ad_request_id)
    if not ad_request:
        return "Ad request not found", 404

    campaign=Campaign.query.get(ad_request.campaign_id)
    campaign.remaining_budget += ad_request.payment_amount
    db.session.commit()

    db.session.delete(ad_request)
    db.session.commit()
    return redirect(url_for('display_adRequest'))

def accept_adRequest(ad_request_id):
    ad_request = AdRequest.query.get(ad_request_id)
    campaign=Campaign.query.get(ad_request.campaign_id)
    influencer=Influencer.query.get(ad_request.influencer_id)

    if not ad_request:
        return "Ad request not found", 404
    
    if ad_request.payment_amount>campaign.remaining_budget:
        return "Remaining budget is too low to accept the request"

    ad_request.status = 'Accepted'
    ad_request.date = date.today()
    db.session.commit()

    influencer.count+=1
    influencer.totalcost += ad_request.payment_amount
    
    campaign.remaining_budget -= ad_request.payment_amount
    db.session.commit()
    return redirect(url_for('display_adRequest'))

def reject_adRequest(ad_request_id):
    ad_request = AdRequest.query.get(ad_request_id)
    if not ad_request:
        return "Ad request not found", 404

    ad_request.status = 'Rejected'
    ad_request.date = date.today()
    db.session.commit()

    return redirect(url_for('display_adRequest'))

def accept_negotiation(ad_request_id):
    ad_request = AdRequest.query.get(ad_request_id)
    campaign=Campaign.query.get(ad_request.campaign_id)
    influencer=Influencer.query.get(ad_request.influencer_id)

    if not ad_request:
        return "Ad request not found", 404

    if ad_request.negotiation_amount-ad_request.payment_amount>campaign.remaining_budget:
        return "Can't Accept Negotiation Cause Amount is too High"

    influencer.count+=1
    influencer.totalcost += ad_request.payment_amount

    ad_request.payment_amount = ad_request.negotiation_amount 
    ad_request.negotiation_status = 'Accepted'
    ad_request.date = date.today()
    db.session.commit()

    return redirect(url_for('display_adRequest'))

def reject_negotiation(ad_request_id):
    ad_request = AdRequest.query.get(ad_request_id)
    if not ad_request:
        return "Ad request not found", 404

    # Reject negotiation logic
    ad_request.negotiation_status = 'Negotiation Rejected'
    ad_request.date = date.today()
    db.session.commit()

    return redirect(url_for('display_adRequest'))