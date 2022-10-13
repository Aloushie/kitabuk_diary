from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Quest
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 3:
            flash('Entry is too short! Your diary entry must be at least 3 characters ', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Entry added!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/zbi', methods=['GET', 'POST'])
@login_required
def questionnaire():
    if request.method == 'POST':
        enter = request.form.get('enter')


        new_entry = Quest(entry=enter, user_id=current_user.id)
        db.session.add(new_entry)
        db.session.commit()
        flash('Entry added!', category='success')

    return render_template("questionnaire.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            flash('Entry deleted!', category='success')
    return jsonify({})

@views.route('/delete-enter', methods=['POST'])
def delete_enter():
    enter = json.loads(request.data)
    enterId = enter['enterId']
    enter = Quest.query.get(enterId)
    if enter:
        if enter.user_id == current_user.id:
            db.session.delete(enter)
            db.session.commit()
            flash('Entry deleted!', category='success')
    return jsonify({})
