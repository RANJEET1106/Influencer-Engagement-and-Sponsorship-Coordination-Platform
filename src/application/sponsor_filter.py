from application.models import Campaign,Influencer,AdRequest
from datetime import date
from sqlalchemy import or_

def filter_campaigns(status=None, visibility=None, flag=None, search=None):
    campaigns = Campaign.query

    if status == 'current':
        campaigns = campaigns.filter(Campaign.end_date >= date.today())
    elif status == 'past':
        campaigns = campaigns.filter(Campaign.end_date < date.today())

    if visibility and visibility != 'all':
        campaigns = campaigns.filter(Campaign.visibility == visibility)

    if flag == 'flagged':
        campaigns = campaigns.filter(Campaign.flag == 'True')
    elif flag == 'none':
        campaigns = campaigns.filter(Campaign.flag == 'False')

    if search:
        campaigns = campaigns.filter(or_(Campaign.name.ilike(f'%{search}%'),
                                         Campaign.description.ilike(f'%{search}%')))

    return campaigns.all()


def filter_influencers(category, niche, min_yt_followers, max_yt_followers,
                       min_insta_followers, max_insta_followers,
                       min_twitter_followers, max_twitter_followers,
                       search):
    influencers = Influencer.query

    if category:
        influencers = influencers.filter_by(category=category)

    if niche:
        influencers = influencers.filter_by(niche=niche)

    if min_yt_followers:
        influencers = influencers.filter(Influencer.ytfollow >= int(min_yt_followers))

    if max_yt_followers:
        max_yt_followers_value = int(max_yt_followers)
        if max_yt_followers_value > 0:
            influencers = influencers.filter(Influencer.ytfollow <= max_yt_followers_value)

    if min_insta_followers:
        influencers = influencers.filter(Influencer.instafollow >= int(min_insta_followers))
    else:
        influencers = influencers.filter(Influencer.instafollow >= 0)

    if max_insta_followers:
        max_insta_followers_value = int(max_insta_followers)
        if max_insta_followers_value > 0:
            influencers = influencers.filter(Influencer.instafollow <= max_insta_followers_value)

    if min_twitter_followers:
        influencers = influencers.filter(Influencer.twitterfollow >= int(min_twitter_followers))
    else:
        influencers = influencers.filter(Influencer.twitterfollow >= 0)

    if max_twitter_followers:
        max_twitter_followers_value = int(max_twitter_followers)
        if max_twitter_followers_value > 0:
            influencers = influencers.filter(Influencer.twitterfollow <= max_twitter_followers_value)

    if search:
        influencers = influencers.filter(Influencer.name.ilike(f"%{search}%"))

    return influencers.all()

def filter_ad_requests(ad_request_type='all', status='all'):

    ad_requests = AdRequest.query

    # Apply filters based on the type
    if ad_request_type == 'received':
        ad_requests = ad_requests.filter_by(request_to='Sponsor')
    elif ad_request_type == 'sent':
        ad_requests = ad_requests.filter_by(request_to='Influencer')
    elif ad_request_type == 'negotiation':
        ad_requests = ad_requests.filter_by(negotiation_status='Requested')

    # Apply filters based on the status
    if status != 'all':
        ad_requests = ad_requests.filter_by(status=status)

    return ad_requests.all()