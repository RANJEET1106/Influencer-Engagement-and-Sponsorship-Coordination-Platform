# registration.py

from flask import request, render_template, redirect, url_for,session
from flask_bcrypt import Bcrypt
from application.models import Sponsor, Influencer, User,db # Import your SQLAlchemy models

bcrypt = Bcrypt()

def registration():
    if request.method=='GET':
        return render_template('common/registration.html')
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        role = request.form.get('filter')

        user = User.query.filter_by(username=username).first()
        if user:
            error = 'Username Already Exists'
            return render_template('common/registration.html', error=error)
        elif password != repassword:
            error = 'Password and Confirm Password Should be the Same'
            return render_template('common/registration.html', error=error)
        else :
            if role=='influencer':
                return render_template('common/reginfluencer.html',username=username,
                                       password=password,repassword=repassword)
            if role=='sponsor':
                return render_template('common/regsponsor.html',username=username,
                                       password=password,repassword=repassword)

def sponsor_registration():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        company = request.form.get('company')
        website = request.form.get('website')

        user = User.query.filter_by(username=username).first()
        if user:
            error = 'Username Already Exists'
            return render_template('common/regsponsor.html', error=error)
        elif password != repassword:
            error = 'Password and Confirm Password Should be the Same'
            return render_template('common/regsponsor.html', error=error)
        else:
            hashed_password = bcrypt.generate_password_hash(password)
            new_user = User(username=username,password=hashed_password,role='sponsor')
            db.session.add(new_user)
            db.session.commit()

            user=User.query.filter_by(username=username).first()
            new_user = Sponsor(id=user.id, companyname=company, website=website)
            db.session.add(new_user)
            db.session.commit()
            message = 'You Have Registered Successfully. Now You Can Proceed With Login'
            session['message'] = message 
            return redirect(url_for('login'))

def influencer_registration():
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        name = request.form.get('name')
        category = request.form.get('category')
        niche = request.form.get('niche')
        ytlink = request.form.get('ytlink')
        ytfollow = request.form.get('ytfollow')
        instalink = request.form.get('instalink')
        instafollow = request.form.get('instafollow')
        twitterlink = request.form.get('twitterlink')
        twitterfollow = request.form.get('twitterfollow')
        user = User.query.filter_by(username=username).first()
        if user:
            error = 'Username Already Exists'
            return render_template('common/registration.html', error=error)
        elif password != repassword:
            error = 'Password and Confirm Password Should be the Same'
            return render_template('common/regsponsor.html', error=error)
        else:
            hashed_password = bcrypt.generate_password_hash(password)
            new_user = User(username=username,password=hashed_password,role='influencer')
            db.session.add(new_user)
            db.session.commit()

            user=User.query.filter_by(username=username).first()
            new_user = Influencer(id=user.id, name=name, category=category, niche=niche,
                                  ytlink=ytlink, ytfollow=ytfollow, instalink=instalink,
                                  instafollow=instafollow, twitterlink=twitterlink, twitterfollow=twitterfollow)
            db.session.add(new_user)
            db.session.commit()
            message = 'You Have Registered Successfully. Now You Can Proceed With Login'
            session['message'] = message 
            return redirect(url_for('login'))
