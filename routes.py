from flask import Flask, render_template, request, session, redirect, url_for
from models import db, User, Place
from forms import SignupForm, LoginForm,AddressForm

import os
import psycopg2
import urllib

os.environ['DATABASE_URL'] = 'postgres://piwiohpehwhqfq:c6d305ca04cf48a034aec44dcfb06917f9cdbdd05e6c804a6b3714a664c8fe09@ec2-23-23-220-163.compute-1.amazonaws.com:5432/da1og5ol5cmrpc'
 
# urllib.parse.uses_netloc.append("postgres")
# url = urllib.parse(os.environ["DATABASE_URL"])

# conn = psycopg2.connect(
#     database=url.path[1:],
#     user=url.username,
#     password=url.password,
#     host=url.hostname,
#     port=url.port
# )


app=Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI']=os.environ['DATABASE_URL']

db.init_app(app)
db.create_all()

app.secret_key="development-key"

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/signup", methods=['GET','POST'])
def signup():
	if 'email' in session:
		return redirect(url_for('home'))

	form=SignupForm()
	if request.method=='POST':
		if form.validate()==False:
			return render_template('signup.html', form=form)
		else:
			newuser=User(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
			db.session.add(newuser)
			db.session.commit()

			session['email']=newuser.email
			return redirect(url_for('home'))

	elif request.method=='GET':
		return render_template('signup.html', form=form)

@app.route("/login", methods=['GET','POST'])
def login():
	if 'email' in session:
		return redirect(url_for('home'))

	form=LoginForm()
	if request.method=='POST':
		if form.validate()==False:
			return render_template('login.html', form=form)
		else:
			email=form.email.data
			password=form.password.data

			user=User.query.filter_by(email=email).first()
			if user is not None and user.check_password(password):
				session['email']=form.email.data
				return redirect(url_for('home'))
			else:
				return redirect(url_for('login'))

	elif request.method=='GET':
		return render_template('login.html', form=form)

@app.route("/logout")
def logout():
	session.pop('email', None)
	return redirect(url_for('index'))

@app.route("/home", methods=['GET','POST'])
def home():
	if 'email' not in session:
		return redirect(url_for('login'))

	form=AddressForm()

	places=[]
	my_coordinates=(45.348473, -75.7590777,17)

	if request.method=='POST':
		if form.validate()==False:
			return render_template('home.html', form=form)
		else:
			address=form.address.data

			p=Place()
			my_coordinates=p.address_to_latlng(address)
			places=p.query(address)

			return render_template('home.html', form=form, my_coordinates=my_coordinates, places=places)

	elif request.method=='GET':
		return render_template("home.html", form=form, my_coordinates=my_coordinates, places=places)

	

if __name__=="__main__":
	
	app.run(debug=True)