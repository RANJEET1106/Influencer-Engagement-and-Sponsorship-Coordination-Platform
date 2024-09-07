from flask import render_template, redirect, url_for, request,session
from flask_login import login_user, logout_user , current_user
from application.models import User, Influencer, Sponsor ,db # Adjust imports based on your models
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def login_logic():
    message = session.pop('message', None)  
    if request.method=='GET':
        return render_template('common/home.html',message=message)
    if request.method=='POST':
        name = request.form.get('username')
        password = request.form.get('password')

        user=User.query.filter_by(username=name).first()
        if user:
            validPass=bcrypt.check_password_hash(user.password,password)
        if(not user or not validPass):
            error = "Invalid username or password."
            return render_template('common/home.html', error=error)
        else :
            login_user(user)
            if(user.role=='admin'):
                return redirect(url_for('admin_dashboard'))
            elif(user.role=='sponsor'):
                return redirect(url_for('sponsor_dashboard'))
            else:
                return redirect(url_for('influencer_dashboard'))
            
def logout_logic():
    if request.method=='GET':
        return render_template('common/logout.html')
    if request.method=='POST':
        if(request.form['logout']=='Yes'):
            logout_user()
            return redirect(url_for('login'))
        else :
            if(current_user.role=='admin'):
                return redirect(url_for('admin_dashboard'))
            elif(current_user.role=='sponsor'):
                return redirect(url_for('sponsor_dashboard'))
            else:
                return redirect(url_for('influencer_dashboard'))
