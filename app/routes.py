from app import app
from flask import render_template, session, redirect, url_for, flash, Response, json
from app.models import Student, Course, Enrollment
from app.forms import RegisterForm, LoginForm

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index=True)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('username'):
        return redirect(url_for('iindex'))

    form = LoginForm()
    if form.validate_on_submit():
        email       = form.email.data
        password    = form.password.data
    
        student = Student.objects(email=email).first()
        if student and student.get_password(password):
            flash(f"{student.first_name}, you are successfully logged in!", "success")
            session['user_id'] = student.user_id
            session['username'] = student.first_name
            return redirect("/index")
        else:
            flash("Sorry, something went wrong.","danger")
    
    return render_template("login.html", title="Login", form=form, login=True )


@app.route("/logout")
def logout():
    session['user_id']=False
    session.pop('username',None)
    return redirect(url_for('index'))


@app.route("/courses/")
@app.route("/courses/<term>")
def courses(term = None):
    if term is None:
        term = "Spring 2019"
    classes = Course.objects.order_by("-courseID")
    return render_template("courses.html", courseData=classes, courses = True, term=term)


@app.route("/register", methods=['POST', 'GET'])
def register():
    if session.get('username'):
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user_id = Student.objects.count()
        user_id += 1

        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        student = Student(user_id=user_id, email=email, first_name=first_name, last_name=last_name)
        student.set_password(self, password)
        student.save()
        flash("You are successfully registered!","success")
        return redirect(url_for('index'))

    return render_template("register.html", title="Register", form=form, register=True)



@app.route("/enrollment", methods=["GET","POST"])
def enrollment():

    if not session.get('username'):
        return redirect(url_for('login'))

    courseID = request.form.get('courseID')
    courseTitle = request.form.get('title')
    user_id = session.get('user_id')

    if courseID:
        if Enrollment.objects(user_id=user_id,courseID=courseID):
            flash(f"Oops! You are already registered in this course {courseTitle}!", "danger")
            return redirect(url_for("courses"))
        else:
            Enrollment(user_id=user_id,courseID=courseID).save()
            flash(f"You are enrolled in {courseTitle}!", "success")

    classes = list( Student.objects.aggregate(*[
            {
                '$lookup': {
                    'from': 'enrollment', 
                    'localField': 'user_id', 
                    'foreignField': 'user_id', 
                    'as': 'r1'
                }
            }, {
                '$unwind': {
                    'path': '$r1', 
                    'includeArrayIndex': 'r1_id', 
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$lookup': {
                    'from': 'course', 
                    'localField': 'r1.courseID', 
                    'foreignField': 'courseID', 
                    'as': 'r2'
                }
            }, {
                '$unwind': {
                    'path': '$r2', 
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$match': {
                    'user_id': user_id
                }
            }, {
                '$sort': {
                    'courseID': 1
                }
            }
        ]))

    return render_template("enrollment.html", enrollment=True, title="Enrollment", classes=classes) 