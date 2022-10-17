from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Quest, Question, User, Todo
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 2:
            flash('Entry is too short! Your diary entry must be at least 3 characters ', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Entry added!', category='success')

    return render_template("home.html", user=current_user)

# @views.route('/zbi', methods=['GET', 'POST'])
# @login_required
# def questionnaire():
#     if request.method == 'POST':
#         enter = request.form.get('enter')


#         new_entry = Quest(entry=enter, user_id=current_user.id)
#         db.session.add(new_entry)
#         db.session.commit()
#         flash('Entry added!', category='success')

#     return render_template("questionnaire.html", user=current_user)


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



@views.route('/ask', methods=['GET', 'POST'])
@login_required
def ask():
    if request.method == 'POST':
        question = request.form['question']
        expert = request.form['expert']

        question = Question(
            question=question, 
            expert_id=expert, 
            asked_by_id=current_user.id
        )

        db.session.add(question)
        db.session.commit()
        flash('Your question has been sent!', category='success')

        return redirect(url_for('views.ask'))
        
    experts = User.query.filter_by(expert=True).all()
    context = {
        'experts' : experts
    }

    return render_template('ask.html', user=current_user, **context)

    

@views.route('/answer/<int:question_id>', methods=['GET', 'POST'])
@login_required
def answer(question_id):
    if not current_user.expert:
        return redirect(url_for('views.home'))

    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        question.answer = request.form['answer']
        db.session.commit()

        return redirect(url_for('views.unanswered'))

    context = {
        'question' : question
    }

    return render_template('answer.html', user=current_user, **context)

@views.route('/question/<int:question_id>')
def question(question_id):
    question = Question.query.get_or_404(question_id)

    context = {
        'question' : question
    }

    return render_template('question.html', user=current_user, **context)

@views.route('/unanswered')
@login_required
def unanswered():
    if not current_user.expert:
        return redirect(url_for('views.home'))

    unanswered_questions = Question.query\
        .filter_by(expert_id=current_user.id)\
        .filter(Question.answer == None)\
        .all()

    context = {
        'unanswered_questions' : unanswered_questions
    }

    return render_template('unanswered.html', user=current_user, **context)

@views.route('/users')
@login_required
def users():
    if not current_user.admin:
        return redirect(url_for('views.home'))

    users = User.query.filter_by(admin=False).all()

    context = {
        'users' : users
    }

    return render_template('users.html', user=current_user, **context)

@views.route('/promote/<int:user_id>')
@login_required
def promote(user_id):
    if not current_user.admin:
        return redirect(url_for('views.home'))

    user = User.query.get_or_404(user_id)

    user.expert = True
    db.session.commit()

    return redirect(url_for('views.users'))


@views.route('/answers')
@login_required
def answer_page():

    if not current_user.admin:
        questions = Question.query.filter(Question.answer != None, Question.expert_id == current_user.id).all() 
    elif current_user.admin:
        questions = Question.query.filter(Question.answer != None).all() 

    context = {
        'questions' : questions
    }
    
    return render_template("answer_page.html", user=current_user, **context)

@views.route('/todo')
@login_required
def todo():
    todo = Todo.query.all()
    return render_template("todo.html", todo=todo, user=current_user)


@views.route("/add", methods=['POST'])
@login_required
def add():
    if request.method == 'POST':
        title = request.form.get("title")
        new_todo = Todo(title=title, complete=False, user_id=current_user.id)
        db.session.add(new_todo)
        db.session.commit()
        flash('Todo item added!', category='success')
        
    return render_template("todo.html", user=current_user)

    
@views.route("/update/<int:todo_id>")
@login_required
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("views.todo"))


@views.route("/delete/<int:todo_id>")
@login_required
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("views.todo"))
