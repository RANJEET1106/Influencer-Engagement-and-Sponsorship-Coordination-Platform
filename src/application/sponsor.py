from flask import render_template, request,redirect,url_for
from flask_login import current_user
from sqlalchemy.orm import joinedload
from sqlalchemy import or_,func
from datetime import date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

from application.models import User, Sponsor, Influencer, AdRequest, Campaign,db
from application.sponsor_filter import filter_campaigns,filter_influencers,filter_ad_requests

def sponsorDashboard():
    if request.method == 'GET':
        username = current_user.username
        sponsor_id = current_user.id
        print(username)
        campaigns = db.session.execute('''select id, name 
                                         from campaign 
                                         where sponsor_id = :sponsor_id''', {'sponsor_id': sponsor_id})
        
        ad_requests = db.session.execute('''select a.id, a.campaign_id, u.username
                                           from ad_request a inner join user u
                                           on a.influencer_id = u.id 
                                           where a.request_to='sponsor' and a.sponsor_id = :sponsor_id ''',{'sponsor_id':sponsor_id})

        return render_template('sponsor/dashboard.html', username=username,
                               campaigns=campaigns,ad_requests=ad_requests)

def campaigns():
    if request.method=='GET':
        campaigns=Campaign.query.filter(Campaign.sponsor_id==current_user.id).all()
        return render_template('sponsor/campaigns.html',campaigns=campaigns)

    if request.method=='POST':
        status = request.form.get('status')
        visibility = request.form.get('visibility')
        flag = request.form.get('flag')
        search = request.form.get('search', '')

        campaigns = filter_campaigns(status, visibility, flag, search)
        return render_template('sponsor/campaigns.html', campaigns=campaigns,status=status,
                               visibility=visibility,flag=flag,search=search)


    
def influencer_find():
    if request.method=='GET':
        influencers = Influencer.query.all()
        for influencer in influencers:
            if influencer.count > 0:
                influencer.avgcost = influencer.totalcost / influencer.count
            else:
                influencer.avgcost = 0
        return render_template('sponsor/find.html', influencers=influencers)
    
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
        for influencer in influencers:
            if influencer.count > 0:
                influencer.avgcost = influencer.totalcost / influencer.count
            else:
                influencer.avgcost = 0
        return render_template('sponsor/find.html', influencers=influencers,
                           category=category, niche=niche,
                           min_yt_followers=min_yt_followers, max_yt_followers=max_yt_followers,
                           min_insta_followers=min_insta_followers, max_insta_followers=max_insta_followers,
                           min_twitter_followers=min_twitter_followers, max_twitter_followers=max_twitter_followers,
                           search=search)

def sponsor_generate_charts(pie_chart_filename='sponsor_pie_chart.png', bar_chart_filename='sponsor_bar_chart.png'):
    # Query to count the number of requests by status for 'Sponsor'
    status_counts = db.session.query(
        AdRequest.status,
        func.count(AdRequest.id)
    ).filter(
        AdRequest.sponsor_id == current_user.id
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

     # Query to count the number of requests by campaign and status
    campaign_status_counts = db.session.query(
        AdRequest.campaign_id,
        AdRequest.status,
        func.count(AdRequest.id)
    ).filter(
        AdRequest.sponsor_id==current_user.id
    ).group_by(
        AdRequest.campaign_id,
        AdRequest.status
    ).all()

    # Prepare data for bar chart
    campaign_data = {}
    status_types = ['Pending', 'Accepted', 'Rejected']

    # Collect data
    for campaign_id, status, count in campaign_status_counts:
        if campaign_id not in campaign_data:
            campaign_data[campaign_id] = {status_type: 0 for status_type in status_types}
        campaign_data[campaign_id][status] = count

    # Sort campaigns by ID for plotting
    sorted_campaigns = sorted(campaign_data.keys())
    sorted_campaigns_str = [str(campaign_id) for campaign_id in sorted_campaigns]
    data = {status: [campaign_data[campaign_id].get(status, 0) for campaign_id in sorted_campaigns] for status in status_types}

    # Create and save bar chart
    if all(value == 0 for status in data for value in data[status]):
        # Create and save an empty graph or a graph with a no data message
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'No Ad Requests', horizontalalignment='center', verticalalignment='center',
                fontsize=14, color='red', weight='bold')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title('Campaign vs Ad Requests (Pending, Accepted, Rejected)')
        plt.savefig(os.path.join('static', bar_chart_filename))
    else:
        # Convert sorted_campaigns to a numpy array for plotting
        x = np.arange(len(sorted_campaigns))
        width = 0.2  # Width of the bars

        # Create and save bar chart
        fig, ax = plt.subplots()
        bars = []
        for i, status in enumerate(status_types):
            bar_heights = [data[status][j] if not np.isnan(data[status][j]) else 0 for j in range(len(sorted_campaigns))]
            bars.append(ax.bar(x + i * width, bar_heights, width, label=status))

        ax.set_xlabel('Campaign ID')
        ax.set_ylabel('Number of Requests')
        ax.set_title('Campaign vs Ad Requests (Pending, Accepted, Rejected)')
        ax.set_xticks(x + width)
        ax.set_xticklabels(sorted_campaigns_str, rotation=45, ha='right')
        ax.legend()

        plt.tight_layout()  # Adjust layout to prevent clipping of tick labels
        plt.savefig(os.path.join('static', bar_chart_filename))

        plt.close()



    return render_template('sponsor/stats.html')

def influencer_view(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        return "Influencer not found", 404
    if influencer.count > 0:
        influencer.avgcost = influencer.totalcost / influencer.count
    else:
        influencer.avgcost = 0
    user = User.query.get(influencer.id) 
    return render_template('sponsor/view_influencer.html', 
                           influencer=influencer, username=user.username)
    
def ad_Requests():
    if request.method=='GET':
        ad_requests = AdRequest.query.filter_by(sponsor_id=current_user.id).all()
        return render_template('sponsor/all_ad_requests.html',ad_requests=ad_requests)


    if request.method == 'POST':
        ad_request_type = request.form.get('type')
        status = request.form.get('status')

        ad_requests = filter_ad_requests(ad_request_type=ad_request_type, status=status)
        ad_requests = ad_requests.filter_by(sponsor_id=current_user.id).all()
        return render_template('sponsor/all_ad_requests.html', ad_requests=ad_requests,
                           type=ad_request_type, status=status)