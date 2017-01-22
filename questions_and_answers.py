# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect
from flask import g
from peewee import *

app = Flask(__name__)

database_sqlite = SqliteDatabase("try3.db")

MARKS = {
    'neud': {
       'color': '#FF0F55',
       'text': u'Отвратительно'
    },
    'udvl': {
       'color': '#ff990a',
       'text': u'Ну такое...'
    },
    'hor': {
       'color': '#87ff2a',
        'text': u'Красавчик'
    },
    'otl': {
       'color': '#1BA43E',
        'text': u'Капитальный красавчик'
    }
}


class BaseModel(Model):
    class Meta:
        database = database_sqlite


class Question(BaseModel):
    question = TextField(default='', null=False)
    correct_answer = TextField(default='', null=False)


class TestQuestion(Question):
    answer_one = TextField(default='', null=False)
    answer_two = TextField(default='', null=False)
    answer_three = TextField(default='', null=False)
    answer_four = TextField(default='', null=False)


class WordQuestion(Question):
    hint = TextField(default='lol', null=False)


def initialize():
    database_sqlite.connect()
    database_sqlite.create_tables([TestQuestion, WordQuestion], safe=True)
    database_sqlite.close()


def get_mark(result):
    if result < 50:
        return MARKS['neud']
    if result > 49 and result < 71:
        return MARKS['udvl']
    if result > 70 and result < 85:
        return MARKS['hor']
    else:
        return MARKS['otl']


@app.before_request
def before_request():
    g.db = database_sqlite
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/test_q/create', methods=['GET', 'POST'])
def create_test_question():

    if request.method == "GET":
        return render_template('test_question_detail.html', action='/test_q/create')

    if request.method == "POST":
        question = request.form['title']
        correct_answer = request.form['correct']
        answer_one = request.form['uncorrect1']
        answer_two = request.form['uncorrect2']
        answer_three = request.form['uncorrect3']
        answer_four = correct_answer
        with database_sqlite.transaction():
            TestQuestion.create(
                question=question,
                correct_answer=correct_answer,
                answer_one=answer_one,
                answer_two=answer_two,
                answer_three=answer_three,
                answer_four=answer_four
            )
        return redirect('/edit')




@app.route('/test_q/delete/<question>', methods=['POST'])
def delete_test_question(question):
    question = int(question)
    TestQuestion.delete().where(
        TestQuestion.id == question
    ).execute()
    return redirect('/edit')


@app.route('/test_q/edit/<question>',  methods=['GET', 'POST'])
def edit_test_question(question):
    if request.method == "GET":
        question_data = TestQuestion.select().where(TestQuestion.id == int(question))[0]
        return render_template('test_question_detail.html',
                               action='/test_q/edit/'+question,
                               question_data = question_data)

    if request.method == "POST":
        question_title = request.form['title']
        correct_answer = request.form['correct']
        answer_one = request.form['uncorrect1']
        answer_two = request.form['uncorrect2']
        answer_three = request.form['uncorrect3']
        answer_four = correct_answer
        with database_sqlite.transaction():
            question = TestQuestion.select().where(TestQuestion.id == int(question))[0]
            question.question = question_title
            question.correct_answer = correct_answer
            question.answer_one = answer_one
            question.answer_two = answer_two
            question.answer_three = answer_three
            question.answer_four = answer_four
            question.save()
        return redirect('/edit')
    return 1


@app.route('/ans_q/create', methods=["GET", "POST"])
def create_ans_qustion():
    if request.method == "GET":
        return render_template('word_question_detail.html', action='/ans_q/create')

    if request.method == "POST":
        question = request.form['title']
        correct_answer = request.form['correct']
        hint = request.form['hint']
        with database_sqlite.transaction():
            WordQuestion.create(
                question=question,
                correct_answer=correct_answer,
                hint=hint
            )
        return redirect('/edit')


@app.route('/ans_q/delete/<question>', methods=["POST"])
def delete_ans_qustion(question):
    question = int(question)
    WordQuestion.delete().where(
        WordQuestion.id == question
    ).execute()
    return redirect('/edit')


@app.route('/ans_q/edit/<question>', methods=["GET", "POST"])
def edit_ans_qustion(question):
    if request.method == "GET":
        question_data = WordQuestion.select().where(WordQuestion.id == int(question))[0]
        return render_template('word_question_detail.html',
                               action='/ans_q/edit/'+question,
                               question_data=question_data)

    if request.method == "POST":
        question_title = request.form['title']
        correct_answer = request.form['correct']
        hint = request.form['hint']
        with database_sqlite.transaction():
            question = WordQuestion.select().where(WordQuestion.id == int(question))[0]
            question.question = question_title
            question.correct_answer = correct_answer
            question.hint = hint
            question.save()
        return redirect('/edit')
    return 1



@app.route('/ans_q/quiz')
def create_ans_quiz():
    question_data = WordQuestion.select()
    return render_template('answers.html', question_data=question_data)


@app.route('/test_q/quiz')
def create_test_quiz():
    question_data = TestQuestion.select()
    return render_template('test.html', question_data=question_data)


@app.route('/test_q/result', methods=['POST'])
def count_test_result():
    list_answers = {k.split('_')[-1]:v for k,v in request.form.items() if k.startswith('answers')}
    correct_answers_counter = 0
    for id,answer in list_answers.items():
        correct_answer = TestQuestion.select(TestQuestion.correct_answer).where(TestQuestion.id == id).get().correct_answer
        if answer == correct_answer: correct_answers_counter += 1
    result = float(correct_answers_counter)/len(list_answers)*100
    mark = get_mark(result)
    return render_template('result.html', mark = mark)


@app.route('/ans_q/result', methods=['POST'])
def count_ans_result():
    list_answers = {k.split('_')[-1]: v for k, v in request.form.items() if k.startswith('answers')}
    correct_answers_counter = 0
    for id, answer in list_answers.items():
        correct_answer = WordQuestion.select(WordQuestion.correct_answer).where(
            WordQuestion.id == id).get().correct_answer
        if answer == correct_answer: correct_answers_counter += 1
    result = float(correct_answers_counter) / len(list_answers) * 100
    mark = get_mark(result)
    return render_template('result.html', mark=mark)


@app.route('/edit')
def edit_page():
    test_questions = []
    word_questions = []
    try:
        for question in TestQuestion.select():
            test_questions.append({
                'id': question.id,
                'title': question.question
            })
        for question in WordQuestion.select():
            word_questions.append({
                'id': question.id,
                'title': question.question
            })
    except:
        pass
    return render_template('edit_questions.html',
                           test_questions=test_questions,
                           word_questions=word_questions)
if __name__ == '__main__':
    initialize()
    app.run(host='0.0.0.0',port='5000')
