from flask import Flask,redirect,url_for,render_template,request
from datetime import date
from application.models import Campaign,AdRequest,Influencer,Sponsor,db
from flask_login import current_user

def create_ad(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    sponsor = Sponsor.query.get(campaign.sponsor_id)
    influencer_id=current_user.id
    if (not campaign):
        return "Influencer or Campaign Not Found",404
    
    if request.method=='GET':
        return render_template('influencer/adRequest.html',campaign_id=campaign_id,influencer_id=influencer_id)
    
    if request.method=='POST':
        messages = request.form.get('messages')
        requirements = request.form.get('requirements')
        payment_amount = int(request.form.get('payment_amount'))

        new_ad_request = AdRequest(
            request_to='Sponsor',
            campaign_id=campaign_id,
            sponsor_id=campaign.sponsor_id,
            influencer_id=influencer_id,
            messages=messages,
            requirements=requirements,
            payment_amount=payment_amount,
            status='Pending',
            date = date.today()
        )

        db.session.add(new_ad_request)
        db.session.commit()
        return redirect(url_for('influencer_dashboard'))


def view_ad(adRequest_id):
    ad_request=AdRequest.query.get(adRequest_id)
    if not ad_request :
        return 'Ad Reuest Not Found',404
    
    if request.method=='GET':
        return render_template('influencer/view_ad_request.html',ad_request=ad_request)
    
def cancel_ad(ad_request_id):
    ad_request = AdRequest.query.get(ad_request_id)
    if not ad_request:
        return "Ad request not found", 404

    db.session.delete(ad_request)
    db.session.commit()
    return redirect(url_for('influencer_ad_request'))

def accept_ad(ad_request_id):
    ad_request = AdRequest.query.get(ad_request_id)
    influencer=Influencer.query.get(ad_request.influencer_id)

    if not ad_request:
        return "Ad request not found", 404

    ad_request.status = 'Accepted'
    ad_request.date = date.today()
    db.session.commit()

    influencer.totalcost += ad_request.payment_amount
    influencer.count += 1
    db.session.commit()
    return redirect(url_for('influencer_ad_request'))

def reject_ad(ad_request_id):
    ad_request = AdRequest.query.get(ad_request_id)
    if not ad_request:
        return "Ad request not found", 404

    ad_request.status = 'Rejected'
    ad_request.date = date.today()
    db.session.commit()

    campaign=Campaign.query.get(ad_request.campaign_id)
    campaign.remaining_budget += ad_request.payment_amount
    db.session.commit()

    return redirect(url_for('influencer_ad_request'))

def negotiate_ad(ad_request_id):
    ad_request=AdRequest.query.get(ad_request_id)
    if not ad_request :
        return 'Ad Reuest Not Found',404
    
    if request.method=='GET':
        return render_template('influencer/negotiate.html',ad_request=ad_request)
    
    if request.method=='POST':
        ad_request.negotiation_amount = request.form.get('negotiation_amount')
        ad_request.negotiation_status = 'Requested'
        db.session.commit()
        return redirect(url_for('influencer_dashboard'))

    

