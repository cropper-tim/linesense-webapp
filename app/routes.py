from flask import render_template, url_for, flash, redirect, request, session
from app import app, db
from app.forms import LoginForm, CreateAccount
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Customer, Business, Prediction, UserInput, CustomerCount
from werkzeug.urls import url_parse
from app.prediction_util import *
import datetime


@app.route('/')
@app.route('/home/')
def home():
    return render_template("home.html", title="Home")


@app.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("user_page"))
    form = LoginForm()
    if form.validate_on_submit():
        user = Customer.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash ("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('user_page', username=current_user.username)
        return redirect(next_page)
    return render_template("login.html", title="Login", form=form)


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/createaccount/", methods=["GET", "POST"])
def create_account():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = CreateAccount()
    if form.validate_on_submit():
        user = Customer(f_name=form.f_name.data, l_name=form.l_name.data, username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("%s has been registered!" % user.username)
        login_user(user)
        return redirect(url_for('user_page', username=current_user.username))
    return render_template("create_account.html", title="Create Account", form=form)


@app.route("/users/<username>/")
@login_required
def user_page(username):
    user = Customer.query.filter_by(username=username).first_or_404()
    [print(x) for x in user.follows]
    return render_template("user_page.html", title=user.username, user=user)

@app.route("/businesses/")
def businesses():
    businesses = Business.query.order_by(Business.name.desc()).all()
    return render_template("businesses.html", title="Our Businesses", businesses=businesses)

@app.route("/businesses/<business_id>/")
@login_required
def business_page(business_id):
    is_following = False
    business = Business.query.filter_by(id=business_id).join(Prediction).first_or_404()
    if business in current_user.follows:
        is_following = True
    return render_template("business_page.html", title=business.name, business=business, is_following=is_following)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def not_found_error(error):
    return render_template('500.html'), 404

@app.route("/user_input/", methods=["POST"])
def user_input():
    data = request.get_json()

    business = Business.query.filter_by(id=data['business']).first()

    ui = UserInput(user_id=current_user.id, business_id=business.id, wait_duration=data['wait_time'])

    db.session.add(ui)
    db.session.commit()

    return 'OK'

@app.route("/predictions/<business_id>")
def prediction_data(business_id):
    # prediction = Prediction.query.filter_by(business_id=business_id).order_by(Prediction.timestamp.desc()).first_or_404()
    # minutes = round((prediction.wait_time)/60)
    # return "{}".format(minutes)
    num_customers = CustomerCount.query.filter_by(business_id=business_id).order_by(CustomerCount.timestamp.desc()).first_or_404().customer_count
    return "{}".format(num_customers)

@app.route('/follow/<business_id>/')
@login_required
def follow(business_id):
    business_to_follow = Business.query.filter_by(id=business_id).first()
    if business_to_follow is None:
        flash('Business {} not found.'.format(business_to_follow))
    current_user.follow(business_to_follow)
    db.session.commit()
    flash('You are now following {}.'.format(business_to_follow.name))

    return redirect(request.referrer)

@app.route('/unfollow/<business_id>/')
@login_required
def unfollow(business_id):
    business_to_unfollow = Business.query.filter_by(id=business_id).first()
    if business_to_unfollow is None:
        flash('Business {} not found.'.format(business_to_unfollow))
    current_user.unfollow(business_to_unfollow)
    db.session.commit()
    flash('You are no longer following {}.'.format(business_to_unfollow.name))

    return redirect(request.referrer)

@app.route("/customer_count/", methods=['POST'])
def customer_count():
    businessID = request.args.get('businessID', default=None)
    if businessID is None:
        return 'businessID not found'

    new_count = request.args.get('new_count', default=None)
    if new_count is None:
        return 'new_count not found'

    new_entry = CustomerCount(business_id=businessID, customer_count=new_count)
    print(new_entry)
    db.session.add(new_entry)
    db.session.commit()

    # get a max of the last 50 customer inputs
    user_inputs = UserInput.query.filter_by(business_id=businessID).order_by(UserInput.timestamp.desc()).limit(50).all()
    print(user_inputs)

    # calculate service rate per person for each user input
    total_waits = []
    for inputs in user_inputs:
        # get the time the user got in line
        start_time = calc_in_line_time(inputs.timestamp, inputs.wait_duration)

        print('[debug] business id={} and start_time={}'.format(businessID, start_time))

        # get the line length for when the user got in line
        count = CustomerCount.query.filter((CustomerCount.business_id==businessID) & (CustomerCount.timestamp<=start_time)).first()

        if count is not None:
            # calculate the rate per person
            service_rate = inputs.wait_duration/count.customer_count

            total_waits.append(service_rate)
        else:
            print('[debug] count is none')

    print(total_waits)
    # calculate line stats
    stats = line_stats(total_waits)

    print(stats)

    # predicted wait = (avg. time/person) * people
    estimate = stats[0] * float(new_count)

    # create the prediction
    new_prediction = Prediction(business_id=businessID, wait_time=estimate, wait_time_stddev=stats[1])

    db.session.add(new_prediction)
    db.session.commit()
    return 'OK'
