from flask import Flask,request,redirect,url_for,render_template
from flask_login import current_user
from sqlalchemy import or_,func
from application.models import Influencer, Campaign, AdRequest, db
from datetime import date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

def influencerDashboard():
    if request.method == 'GET':
        user = current_user 
        influencer_id = current_user.id
        influencer = Influencer.query.get(influencer_id)
        
        ad_requests = db.session.execute('''select a.id, c.name, s.companyname
from ad_request a inner join user u
on a.influencer_id = u.id inner join campaign c
on c.id = a.campaign_id inner join sponsor s
on a.sponsor_id=s.id
where a.request_to='Influencer' and a.influencer_id = :influencer_id''',{'influencer_id':influencer_id})

        return render_template('influencer/dashboard.html', user=user,ad_requests=ad_requests,influencer=influencer)
    

def campaign_find():
    campaigns = Campaign.query
    campaigns = campaigns.filter(Campaign.end_date >= date.today())
    campaigns = campaigns.filter(Campaign.visibility == 'public')
    campaigns = campaigns.filter(Campaign.flag == 'False')
    

    if request.method=='GET':
        campaigns = campaigns.all()
        return render_template('influencer/campaigns.html',campaigns=campaigns)

    if request.method=='POST':
        search = request.form.get('search', '')
        if search:
            campaigns = campaigns.filter(or_(Campaign.name.ilike(f'%{search}%'),
                                         Campaign.description.ilike(f'%{search}%')))
        campaigns = campaigns.all()
        return render_template('influencer/campaigns.html', campaigns=campaigns,search=search)

def influencer_generate_charts(pie_chart_filename='influencer_pie_chart.png'):
    # Query to count the number of requests by status for 'Sponsor'
    status_counts = db.session.query(
        AdRequest.status,
        func.count(AdRequest.id)
    ).filter(
        AdRequest.influencer_id == current_user.id
    ).group_by(
        AdRequest.status
    ).all()
    # Prepare data for pie chart
    statuses = [row[0] for row in status_counts]
    counts = [row[1] for row in status_counts]

    # Handle NaN or None values in counts
    counts = [0 if count is None or isinstance(count, float) and (count != count) else count for count in counts]

    # Default data if no status counts were retrieved
    if not statuses:
        statuses = ['Pending', 'Accepted', 'Rejected']
        counts = [0, 0, 0]

    # Ensure that statuses and counts have the same length
    if len(statuses) != len(counts):
        raise ValueError("Mismatch between number of statuses and counts")

    # Check if all counts are zero
    if all(count == 0 for count in counts):
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'No Ad Requests', horizontalalignment='center', verticalalignment='center',
                fontsize=14, color='red', weight='bold')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title('Distribution of Ad Requests Status (Sponsor)')
    else:
        # Create and save pie chart
        fig, ax = plt.subplots()
        ax.pie(counts, labels=statuses, autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99'])
        ax.set_title('Distribution of Ad Requests Status (Sponsor)')

    plt.savefig(os.path.join('static', pie_chart_filename))
    plt.close()

    return render_template('influencer/stats.html')     

def filter_ad_requests(ad_request_type='all', status='all'):

    ad_requests = AdRequest.query

    # Apply filters based on the type
    if ad_request_type == 'received':
        ad_requests = ad_requests.filter_by(request_to='Influencer')        
    elif ad_request_type == 'sent':
        ad_requests = ad_requests.filter_by(request_to='Sponsor')
    elif ad_request_type == 'negotiation':
        ad_requests = ad_requests.filter_by(negotiation_status='Requested')

    # Apply filters based on the status
    if status != 'all':
        ad_requests = ad_requests.filter_by(status=status)

    return ad_requests.all()

def ad_requests():
    if request.method=='GET':
        ad_requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()
        return render_template('influencer/all_ad_requests.html',ad_requests=ad_requests)


    if request.method == 'POST':
        ad_request_type = request.form.get('type')
        status = request.form.get('status')

        ad_requests = filter_ad_requests(ad_request_type=ad_request_type, status=status)

        return render_template('influencer/all_ad_requests.html', ad_requests=ad_requests,
                           type=ad_request_type, status=status)