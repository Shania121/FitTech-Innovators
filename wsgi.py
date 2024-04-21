import click, sys, csv
from flask import Flask
from sqlalchemy.exc import IntegrityError
from main import app, User, Workout, Routine, initialize_db


@app.cli.command("init", help="Creates and initializes the database")
def initialize():
  initialize_db()