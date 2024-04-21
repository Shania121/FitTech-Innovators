from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), unique=True, nullable=False)
  username = db.Column(db.String(80), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)

  def __init__(self, email, username, password):
    self.email = email
    self.username = username
    self.set_password(password)

  def set_password(self, password):
    self.password = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password, password)

  def search_workouts(self, bodypart, page):
    matching_workouts = None

    if bodypart == "Forearms":
      matching_workouts = Workout.query.filter_by(bodypart="Forearms")
    elif bodypart == "Quadriceps":
      matching_workouts = Workout.query.filter_by(bodypart="Quadriceps")
    elif bodypart == "Abdominals":
      matching_workouts = Workout.query.filter_by(bodypart="Abdominals")
    elif bodypart == "Lats":
      matching_workouts = Workout.query.filter_by(bodypart="Lats")
    elif bodypart == "Middle Back":
      matching_workouts = Workout.query.filter_by(bodypart="Middle Back")
    elif bodypart == "Lower Back":
      matching_workouts = Workout.query.filter_by(bodypart="Lower Back")
    elif bodypart == "Shoulders":
      matching_workouts = Workout.query.filter_by(bodypart="Shoulders")
    elif bodypart == "Biceps":
      matching_workouts = Workout.query.filter_by(bodypart="Biceps")
    elif bodypart == "Glutes":
      matching_workouts = Workout.query.filter_by(bodypart="Glutes")
    elif bodypart == "Triceps":
      matching_workouts = Workout.query.filter_by(bodypart="Triceps")
    elif bodypart == "Hamstrings":
      matching_workouts = Workout.query.filter_by(bodypart="Hamstrings")
    elif bodypart == "Neck":
      matching_workouts = Workout.query.filter_by(bodypart="Neck")
    elif bodypart == "Chest":
      matching_workouts = Workout.query.filter_by(bodypart="Chest")
    elif bodypart == "Traps":
      matching_workouts = Workout.query.filter_by(bodypart="Traps")
    elif bodypart == "Calves":
      matching_workouts = Workout.query.filter_by(bodypart="Calves")
    elif bodypart == "Abductors":
      matching_workouts = Workout.query.filter_by(bodypart="Abductors")

    else:
      matching_workouts = Workout.query

    return matching_workouts.paginate(page=page, per_page=12)


class Workout(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(80), nullable=False)
  description = db.Column(db.String(500), nullable=False)
  bodypart = db.Column(db.String(120), nullable=False)
  equipment = db.Column(db.String(120), nullable=False)
  image = db.Column(db.String(200), nullable=True)
  rating = db.Column(db.Float, nullable=False)

  def __init__(self, title, description, bodypart, equipment, image, rating):
    self.title = title
    self.description = description
    self.bodypart = bodypart
    self.equipment = equipment
    self.image = image
    self.rating = rating

  # def add_to_routine(self, routine_id, workout_id):
  #   routine = Routine.query.filter_by(id=routine_id).first()
  #   if not routine:
  #     return None
  #   routine_workout = RoutineWorkouts(workout_id=workout_id, routine_id=routine_id)
  #   db.session.add(routine_workout)
  #   db.session.commit()
  #return routine_workout

  # def add_to_routine(self, routine, workout):
  #   new_entry = RoutineWorkouts(routine_id=routine.id, workout_id=workout.id)
  #   return new_entry

  def delete_from_routine(self, routine_id, workout_id):
    my_routine = RoutineWorkouts.query.filter_by(routine_id=routine_id,
                                                 workout_id=workout_id)
    if not my_routine:
      return None
    db.session.delete(my_routine)
    db.session.commit()
    return True


class RoutineWorkouts(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  workout_id = db.Column(db.Integer,
                         db.ForeignKey('workout.id'),
                         nullable=False)
  routine_id = db.Column(db.Integer,
                         db.ForeignKey('routine.id'),
                         nullable=False)
  workout = db.relationship('Workout', backref='routines', lazy=True)
  routine = db.relationship('Routine', backref='routines', lazy=True)

  def __init__(self, workout_id, routine_id):
    self.workout_id = workout_id
    self.routine_id = routine_id


class Routine(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), unique=True, nullable=False)
  workout_id = db.Column(db.Integer,
                         db.ForeignKey('workout.id'),
                         nullable=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  user = db.relationship('User', backref=db.backref('routine', lazy=True))
  workout = db.relationship('Workout', backref='routine', lazy=True)

  def __init__(self, name, workout_id, user_id):
    self.name = name
    self.user_id = user_id
    self.workout_id = workout_id
