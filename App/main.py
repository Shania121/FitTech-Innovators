import os
from flask import Flask, jsonify,request, render_template, send_from_directory, flash, redirect, url_for
from functools import wraps
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import user

from .models import db, User, Workout, Routine, RoutineWorkouts
import csv

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    current_user,
    set_access_cookies,
    unset_jwt_cookies,
    current_user,
)
def create_app():
  app = Flask(__name__, static_url_path='/static')
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['TEMPLATES_AUTO_RELOAD'] = True
  app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
  app.config['DEBUG'] = True
  app.config['SECRET_KEY'] = 'MySecretKey'
  app.config['PREFERRED_URL_SCHEME'] = 'https'
  app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
  app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
  app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
  app.config["JWT_COOKIE_SECURE"] = True
  app.config["JWT_SECRET_KEY"] = "super-secret"
  app.config["JWT_COOKIE_CSRF_PROTECT"] = False
  db.init_app(app)
  app.app_context().push()
  return app
  
app = create_app()
jwt = JWTManager(app)



@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
  identity = jwt_data["sub"]
  return User.query.get(identity)
  

def parse_workouts():
  with open('Workouts2.csv', encoding='unicode_escape') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
      workout = Workout(title=row['Exercise_Name'],
                  description=row['Description_URL'],
                  bodypart=row['muscle_gp'],
                  equipment=row['Equipment'],
                  image=row['Exercise_Image1'],
                  rating=row['Rating'])
      db.session.add(workout)
  db.session.commit()

def initialize_db():
  db.drop_all()
  db.create_all()
  create_user()
  parse_workouts()
  print('database intialized')

def create_user():
  bob = User(email = "bob@email.com", username="bob", password="bobpass")
  db.session.add(bob)
  db.session.commit()

def login_user(username, password):
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    token = create_access_token(identity=user)
    return token
  return None

@app.route('/app')
@jwt_required()
def home_page():
  return render_template('home.html', user=current_user)


@app.route('/',methods=['GET'])
@app.route('/login', methods=['GET'])
def login():
  return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_action():
  username = request.form.get('username')
  password = request.form.get('password')
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    response = redirect(url_for('home_page'))
    access_token = create_access_token(identity=user.id)
    set_access_cookies(response, access_token)
    return response
  else:
    flash('Invalid username or password')
    return redirect(url_for('login'))


@app.route('/signup')
def signup():
  return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup_action():
  data = request.form
  newUser = User(email=data['email'], username=data['username'], password=data['password'])
  response = None
  try:
    db.session.add(newUser)
    db.session.commit()
    token = login_user(data['username'], data['password'])
    response = redirect(url_for('home_page'))
    set_access_cookies(response, token)
    flash('Account created!')
  except Exception:
    db.session.rollback()
    flash("username or email already exists")  
    response = redirect(url_for('login'))
  return response
    
    

@app.route('/createRoutine', methods=['POST'])
def create_routine():
  name=request.form['name']
  routine = Routine.query.filter_by(name=name, user_id=current_user.id).first()
  if routine:
    flash("This exercise is already added to your routine")
    return redirect(request.referrer)
  else: 
    routine = Routine(name=name, user_id=current_user.id, workout_id=None)
    db.session.add(routine)
    db.session.commit()
    flash("Exercise added to your routine")
    response = redirect(url_for('routines_page'))
    return response

@app.route('/deleteRoutine/<id>' , methods=['POST'])
def delete_routine(id):
  routine = Routine.query.filter_by(id=id).first()
  workouts = RoutineWorkouts.query.filter_by(routine_id=id).all()
  if routine:
    if workouts:
      for workout in workouts:
        db.session.delete(workout)
        db.session.commit()
    db.session.delete(routine)
    db.session.commit()
    flash("Routine has been deleted")
    return redirect(url_for('routines_page'))
  else:
    flash("Routine does not exist")
    return redirect(url_for('routines_page'))

@app.route('/addWorkouts/<id>', methods=['POST'])
@jwt_required()
def addWorkout(id):
  data = request.form
  workout = Workout.query.get(id)
  routine = Routine.query.filter_by(id=data['routine']).first()
  if workout and routine:
    new_entry = RoutineWorkouts(routine_id=routine.id, workout_id=workout.id)
    db.session.add(new_entry)
    db.session.commit()
    flash("Workout added to your routine")
    return redirect(request.referrer)

@app.route('/deleteWorkouts/<id>', methods=['POST'])
def deleteWorkout(id):
  exercise = RoutineWorkouts.query.filter_by(id=id).first()
  if exercise:
    db.session.delete(exercise)
    db.session.commit()
    flash("Exercise removed from routine")
  else:
    flash("This exercise is not in your routine")
  return redirect(url_for('routines_page'))


@app.route('/home')
def home():
  return render_template('home.html')

@app.route('/workouts')
@app.route('/workouts/<title>')
@jwt_required()
def workouts_page(title=None):
  page = request.args.get('page', 1, type=int)
  bodypart = request.args.get('bodypart',type=str)
  workouts = current_user.search_workouts(bodypart, page)
  routines = Routine.query.filter_by(user_id=current_user.id).all()
  clicked_workout_title = None
  clicked_workout_description = None
  clicked_workout_image = None
  clicked_workout_equipment = None
  clicked_workout_rating = None
  clicked_workout_musclegroup = None
  workout_id = request.args.get('id', default=None, type=int)
  if workout_id:
      workout = Workout.query.get(workout_id)
      if workout:
          clicked_workout_title = workout.title
          clicked_workout_description = workout.description
          clicked_workout_image = workout.image
          clicked_workout_equipment = workout.equipment
          clicked_workout_musclegroup = workout.bodypart
          clicked_workout_rating = workout.rating
  title_workout=None
  if title: 
    title_workout = Workout.query.filter_by(title=title).first()
  username = None
  useremail = None
  user = User.query.filter_by(id=current_user.id).first()
  if user:
    username = user.username
    useremail = user.email
  return render_template(
    'workouts.html', 
    workouts=workouts, 
    page=page, 
    title=title_workout, 
    bodypart=bodypart, 
    routines=routines,
    workout_id=workout_id, 
    clicked_title=clicked_workout_title,
    clicked_description=clicked_workout_description,
    clicked_image=clicked_workout_image,
    clicked_equipment=clicked_workout_equipment,
    clicked_musclegroup=clicked_workout_musclegroup,
    clicked_rating=clicked_workout_rating, 
    username=username,
    useremail=useremail)


@app.route('/routines')
@app.route('/routines/<id>', methods =['GET'])
@jwt_required()
def routines_page(id=None):
    routines = Routine.query.filter_by(user_id=current_user.id).all()
    myRoutine = RoutineWorkouts.query.filter_by(routine_id=id).all()
    return render_template('routines.html', routines=routines, myroutine=myRoutine)


@app.route('/logout', methods=['GET'])
@jwt_required()
def logout_action():
  flash('Logged Out')
  response = redirect(url_for('login'))
  unset_jwt_cookies(response)
  return response

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80, debug=True)
