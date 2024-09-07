from flask import Flask,request,redirect,url_for,render_template
from flask_login import current_user
from sqlalchemy import or_,func
from application.models import Influencer, Campaign, AdRequest, User, Sponsor, db
from datetime import date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def adminDashboard():
    user=current_user
    ongoing_campaigns = Campaign.query.filter(
        Campaign.end_date >= date.today()
    ).all()

    flagged_campaigns = Campaign.query.filter(
        Campaign.flag == 'True'
    ).all()

    flagged_users = User.query.filter(
        User.flag == 'True'
    ).all()

    return render_template(
        'admin/dashboard.html',
        ongoing_campaigns=ongoing_campaigns,
        flagged_campaigns=flagged_campaigns,
        flagged_users=flagged_users,
        user=user
    )

def adminFind():
    campaigns = Campaign.query
    campaigns = campaigns.filter(Campaign.end_date >= date.today())
    campaigns = campaigns.filter(Campaign.visibility == 'public')
    campaigns = campaigns.filter(Campaign.flag == 'False')
    
    users = User.query
    users = users.filter(User.flag == 'False')
    if request.method=='GET':
        campaigns = campaigns.all()
        users = users.all()
        return render_template('admin/find.html',campaigns=campaigns,users=users)

    if request.method=='POST':
        search = request.form.get('search', '')
        if search:
            campaigns = campaigns.filter(or_(Campaign.name.ilike(f'%{search}%'),
                                         Campaign.description.ilike(f'%{search}%')))
            users = users.filter(User.username.ilike(f"%{search}%"))
        campaigns = campaigns.all()
        users = users.all()
        return render_template('admin/find.html', campaigns=campaigns,users=users,search=search)
    
def admin_generate_charts(pie_chart_filename='admin_pie_chart.png', 
                    sponsor_bar_chart_filename='admin_bar_chart.png'):
    
    # Helper function to create pie chart
    def create_pie_chart(data, labels, title, filename):
        fig, ax = plt.subplots()
        ax.pie(data, labels=labels, autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99'])
        ax.set_title(title)
        plt.savefig(os.path.join('static', filename))
        plt.close()

    # Query to count the number of requests by status for all ad requests
    status_counts_all = db.session.query(
        AdRequest.status,
        func.count(AdRequest.id)
    ).group_by(
        AdRequest.status
    ).all()

    statuses_all = [row[0] for row in status_counts_all]
    counts_all = [row[1] for row in status_counts_all]

    # Example data if no status counts were retrieved
    if not statuses_all:
        statuses_all = ['Pending', 'Accepted', 'Rejected']
        counts_all = [0, 0, 0]

    create_pie_chart(counts_all, statuses_all, 'Overall Distribution of Ad Requests Status', pie_chart_filename)

    # Query to count the number of requests by sponsor and fetch the username
    sponsor_counts = db.session.query(
        AdRequest.sponsor_id,
        User.username,
        AdRequest.status,
        func.count(AdRequest.id)
    ).join(
        User, User.id == AdRequest.sponsor_id
    ).group_by(
        AdRequest.sponsor_id,
        User.username,
        AdRequest.status
    ).all()

    # Prepare data for the bar chart
    sponsor_usernames = list(set(row[1] for row in sponsor_counts))
    status_types = ['Pending', 'Accepted', 'Rejected']

    # Initialize data structures
    data = {username: {status: 0 for status in status_types} for username in sponsor_usernames}
    
    # Populate the data
    for sponsor_id, username, status, count in sponsor_counts:
        if username in data:
            data[username][status] = count

    # Convert data for plotting
    sorted_usernames = sorted(data.keys())
    x = np.arange(len(sorted_usernames))
    width = 0.2  # Width of the bars

    # Create lists for each status type
    bars_data = {status: [data[username].get(status, 0) for username in sorted_usernames] for status in status_types}

    # Create and save the bar chart
    fig, ax = plt.subplots()
    bars = []
    for i, status in enumerate(status_types):
        bars.append(ax.bar(x + i * width, bars_data[status], width, label=status))

    ax.set_xlabel('Sponsor Username')
    ax.set_ylabel('Number of Ad Requests')
    ax.set_title('Number of Ad Requests per Sponsor by Status')
    ax.set_xticks(x + width)
    ax.set_xticklabels(sorted_usernames, rotation=45, ha='right')
    ax.legend()

    # Add grid and set y-limits
    ax.grid(True, which='both', linestyle='--', linewidth=0.7)
    ax.set_ylim(0, max(max(bars_data[status]) for status in status_types) + 1)  # Set y-limit for visibility

    plt.tight_layout()  # Adjust layout to prevent clipping of tick labels
    plt.savefig(os.path.join('static', sponsor_bar_chart_filename))
    plt.close()

    return render_template('admin/stats.html')

def viewCampaign(campaign_id):
    campaign=Campaign.query.filter(Campaign.id==campaign_id).first()
    if not campaign:
        return "Campaign not found", 404
    return render_template('admin/viewCampaign.html',campaign=campaign)

def viewUser(user_id):
    user=User.query.filter(User.id==user_id).first()
    if not user:
        return "User not found", 404
    
    if(user.role=='sponsor'):
        sponsor=Sponsor.query.filter(Sponsor.id==user_id).first()
        return render_template('admin/viewUser.html',user=user,sponsor=sponsor)
    
    if(user.role=='influencer'):
        influencer=Influencer.query.filter(Influencer.id==user_id).first()
        return render_template('admin/viewUser.html',user=user,influencer=influencer)
    return

def flagUser(user_id):
    user=User.query.filter(User.id==user_id).first()
    if not user:
        return "User not found", 404
    
    if(user.flag=='True'):
        user.flag='False'
        db.session.commit()

    elif(user.flag=='False'):
        user.flag='True'
        db.session.commit()

    return redirect(url_for('admin_dashboard'))

def flagCampaign(campaign_id):
    campaign=Campaign.query.filter(Campaign.id==campaign_id).first()
    if not campaign:
        return "Campaign not found", 404
    
    if(campaign.flag=='True'):
        campaign.flag='False'
        db.session.commit()

    elif(campaign.flag=='False'):
        campaign.flag='True'
        db.session.commit()

    return redirect(url_for('admin_dashboard'))

def removeUser(user_id):
    user = User.query.get(user_id)
    if not user:
        return "User not found", 404
    
    if request.method == 'GET':
        return render_template('admin/remove_user.html',user=user)
    if request.method == 'POST':
        if user.role=="Sponsor":
            AdRequest.query.filter_by(sponsor_id=user_id).delete()
            Campaign.query.filter_by(sponsor_id=user_id).delete()
            Sponsor.query.filter_by(id=user_id).delete()
            db.session.commit()
        elif user.role == "Influencer":
            AdRequest.query.filter_by(influencer_id=user_id).delete()
            Influencer.query.filter_by(id=user_id).delete()
            db.session.commit()

        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

def removeCampaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return "Campaign not found", 404

    if request.method == 'GET':
        return render_template('admin/remove_campaign.html', campaign=campaign)
    if request.method == 'POST':
        db.session.delete(campaign)
        db.session.commit()
        AdRequest.query.filter_by(campaign_id=campaign_id).delete()
        db.session.commit()
        return redirect(url_for('admin_dashboard'))