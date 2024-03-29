import secrets
import os
from PIL import Image
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Question, User, Todo
from .forms import UpdateAccountForm
from . import db
import json

views = Blueprint('views', __name__)

# Diary entry feature
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 2:
            flash('Entry is too short! Your diary entry must be at least 2 characters ', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Entry added!', category='success')

    return render_template("home.html", user=current_user)

# Delete diary entry feature
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

# Q&A ask a question feature
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

    
# Q&A answer a question faeture
@views.route('/answer/<int:question_id>', methods=['GET', 'POST'])
@login_required
def answer(question_id):
    if not current_user.expert:
        return redirect(url_for('views.home'))

    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        question.answer = request.form['answer']
        db.session.commit()
        flash('Your have answered the question!', category='success')

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

# To-do list feature
@views.route('/todo')
@login_required
def todo():
    todo = Todo.query.all()
    return render_template("todo.html", todo=todo, user=current_user)


# Add items to to-do list
@views.route("/add", methods=['POST'])
@login_required
def add():
    if request.method == 'POST':
        title = request.form.get("title")
    if len(title) < 2:
        flash('Entry is too short! Your diary entry must be at least 2 characters ', category='error')
    else:
        new_todo = Todo(title=title, complete=False, user_id=current_user.id)
        db.session.add(new_todo)
        db.session.commit()
        flash('Todo item added!', category='success')
        
    return render_template("todo.html", user=current_user)

# Update to-do list feature
@views.route("/update/<int:todo_id>")
@login_required
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("views.todo"))

# Delete to-do item feature
@views.route("/delete/<int:todo_id>")
@login_required
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("views.todo"))

# Account profile image feature
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(views.root_path, 'static/img', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@views.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            db.session.commit()
    image_file = url_for('static', filename='img/' + current_user.image_file)
    return render_template('account.html', user=current_user, 
                            image_file=image_file, form=form)


@views.route("/about")
def about():
    return render_template('about.html', user=current_user)