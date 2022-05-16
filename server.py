import datetime
import json
from flask import flash
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for


def load_clubs():
    with open('clubs.json') as c:
        list_of_clubs = json.load(c)['clubs']
        return list_of_clubs


def load_competitions():
    with open('competitions.json') as comps:
        list_of_competitions = json.load(comps)['competitions']
        date_format = "%Y-%m-%d %H:%M:%S"
        for competition in list_of_competitions:
            competition['date'] = datetime.datetime.strptime(competition["date"], date_format)
            if competition['date'] < datetime.datetime.now():
                competition['is_past'] = True
            else:
                competition['is_past'] = False
        return list_of_competitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = load_competitions()
clubs = load_clubs()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def show_summary():
    try:
        found_club = [c for c in clubs if c['email'] == request.form['email']][0]
    except IndexError:
        flash("Sorry, that email wasn't found.")
        return render_template('index.html')
    return render_template('welcome.html', club=found_club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    try:
        found_club = [c for c in clubs if c['name'] == club][0]
        found_competition = [c for c in competitions if c['name'] == competition][0]
    except IndexError:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)
    return render_template('booking.html', club=found_club, competition=found_competition)


@app.route('/purchasePlaces', methods=['POST'])
def purchase_places():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    places_max_limit = 12
    places_required = int(request.form['places'])
    places_remaining = int(competition['numberOfPlaces'])
    if places_required > places_remaining:
        flash(f"Cannot book more places than remaining ({places_remaining}).")
        return render_template('booking.html', club=club, competition=competition)
    elif places_required > int(club['points']):
        flash(f"Cannot book more places than points you have ({club['points']}).")
        return render_template('booking.html', club=club, competition=competition)
    elif places_required > places_max_limit:
        flash(f"Cannot book more than max limit ({places_max_limit}).")
        return render_template('booking.html', club=club, competition=competition)
    else:
        flash('Great-booking complete!')
        club['points'] = str(int(club['points']) - places_required)
        competition['numberOfPlaces'] = str(int(competition['numberOfPlaces']) - places_required)
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/clubs', methods=['POST'])
def display_clubs():
    return render_template('clubs.html', clubs=clubs, email=request.form['email'])


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
