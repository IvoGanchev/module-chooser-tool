from flask import render_template, flash, request, redirect, session, url_for, jsonify, json
from flask_mail import Message
from app import app, mail
from .forms import SignUpForm, SignInForm, ChangePasswordForm, ModuleForm, CourseForm, LecturerForm
from app import db, models, bcrypt
from sqlalchemy import Table
import logging, os
from flask_login import LoginManager, login_user,logout_user,current_user,login_required
from flask_admin import Admin
import sys
import requests


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = "strong"

logger = logging.getLogger(__name__)
logging.basicConfig(filename='logging.log', level=logging.INFO)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/', methods=['GET', 'POST'])
def main():
    if current_user.is_authenticated:
        return redirect('/')
    else:
        user = None
        sign_in_form = SignInForm()
        if request.method == 'GET':
            return render_template('/sign_in.html', form=sign_in_form, user = user)

        user = models.Student.query.filter_by(student_email= request.form["student_email"]).first()
        if user is not None and bcrypt.check_password_hash(user.student_password, request.form['student_password']) and user.student_email != "admin@leeds.ac.uk":
            flash("Hello {}".format(user.student_name))
            login_user(user, remember = True)
            logger.info("New user logged in: session[current_user_email] = {}".format(user.student_email))
            return redirect('/home_page')
        elif user is not None and bcrypt.check_password_hash(user.student_password, request.form['student_password']) and user.student_email == "admin@leeds.ac.uk":
            flash("Hello {}".format(user.student_name))
            login_user(user, remember = True)
            logger.info("New user logged in: session[current_user_email] = {}".format(user.student_email))
            return redirect('/display_modules')
        else:
            err_msg = "Invalid email/password!"
            logger.warning("Invalid {} when trying to log in".format(user))
            user = None
            return render_template('/sign_in.html',
                                    title='Sign In',
                                    user = user,
                                    err_msg=err_msg,
                                    form=sign_in_form)

        return render_template('/sign_in.html',
                                title='Sign In',
                                user = user,
                                form=sign_in_form)

# Home Page
@app.route('/home_page', methods=['GET', 'POST'])
def home_page():

    if current_user.is_authenticated:
        user = current_user
        return render_template('/home_page.html',
                                title='Home page',
                                user = user)
    else:
        return redirect('/')

    return render_template('/home_page.html',
                            title='Sign In',
                            user = user)

# Registration page
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    all_courses = models.Course.query.all()
    if current_user.is_authenticated:
        return redirect('/')
    else:
        user = None
        sign_up_form = SignUpForm()

        #when the sign_up button is clicked
        if sign_up_form.validate_on_submit():
            all_users = models.Student.query.all()
            #check if the user already exists
            for user in all_users:
                if request.form["student_email"] == user.student_email:
                        flash("User already exists!")
                        user = None
                        logger.warning("{} already exists".format(user))
                        return redirect('/sign_up')

            # Check if the email and confirm email fields match
            if request.form["confirm_email"] != request.form["student_email"]:
                flash("The two emails need to be the same!")
                logger.warning("Email and confrim email fields do not match")
                return redirect('/sign_up')
            else:
                #add the user to the db
                user = models.Student(sign_up_form.student_email.data, sign_up_form.student_password.data, sign_up_form.student_name.data, sign_up_form.current_year.data)
                selected_course = models.Course.query.filter_by(course_title = sign_up_form.course_id.data).first()
                user.course = selected_course
                db.session.add(user)
                db.session.commit()

                all_modules = selected_course.modules

                for module in all_modules:
                    record = models.Record(user.id, module.id, 0,0)
                    user.record.append(record)
                    module.record.append(record)
                    db.session.commit()

                logger.info("{} added to the database".format(user))
                return redirect('/sign_in')

        return render_template('/sign_up.html',
                                title='Sign Up',
                                user=user,
                                form=sign_up_form,
                                courses=all_courses)


# Login
@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if current_user.is_authenticated:
        return redirect('/home_page')
    else:
        user = None
        sign_in_form = SignInForm()
        if request.method == 'GET':
            return render_template('/sign_in.html', form=sign_in_form, user = user)

        user = models.Student.query.filter_by(student_email= request.form["student_email"]).first()
        if user is not None and bcrypt.check_password_hash(user.student_password, request.form['student_password']):
            login_user(user, remember = True)
            logger.info("New user logged in: session[current_user_email] = {}".format(user.student_email))
            return redirect('/home_page')
        else:
            err_msg = "Invalid email/password!"
            logger.warning("Invalid {} when trying to log in".format(user))
            user = None
            return render_template('/sign_in.html',
                                    title='Sign In',
                                    user = user,
                                    err_msg=err_msg,
                                    form=sign_in_form)

        return render_template('/sign_in.html',
                                title='Sign In',
                                user = user,
                                form=sign_in_form)

@login_required
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():

    if current_user.is_authenticated:
        user = current_user
        change_password_form = ChangePasswordForm()

        #when the change password button is clicked
        if change_password_form.validate_on_submit():

            #if new password and confirm new password match
            if bcrypt.check_password_hash(user.student_password,request.form["current_password"]):
                if request.form["new_password"] == request.form["confirm_new_password"]:
                #if change_password_form.new_password.data == change_password_form.confirm_new_password.data:

                    #change the current user's password with the new one provided
                    user.password = bcrypt.generate_password_hash(request.form["confirm_new_password"])
                    db.session.commit()

                    flash("Successfully changed password!")
                    logger.info("changed password for {}".format(user))

                    return redirect('/module_chooser')
                else:
                    flash("Passwords do not match")
                    logger.warning("passwords do not match when tried to change it for user {}".format(user))
            else:
                flash("Old password not correct!")
        return render_template("/change_password.html",
                                title="Change Password",
                                user = user,
                                form=change_password_form)
    else:
        return redirect ('/')

@login_required
@app.route('/sign_out', methods=['GET', 'POST'])
def sign_out():
    if current_user.is_authenticated:
        user = current_user
        #sign out the current user
        logout_user()
        logger.info ("Sign out: session['current_user_email'] = []")

        return redirect('/')

@login_required
@app.route('/create_module', methods=['GET', 'POST'])
def create_module():
    # Only allow an admin to create a module
    if current_user.is_authenticated:
        if current_user.student_email == 'admin@leeds.ac.uk':
            user = current_user
            module_form = ModuleForm()

            #when the sign_up button is clicked
            if module_form.validate_on_submit():
                all_modules = models.Module.query.all()

                if all_modules:
                    for module in all_modules:
                        #check if the user already exists
                        if module_form.module_title.data == module.module_title:
                            flash("Module already exists!")
                            logger.warning("{} already exists".format(module))
                            return redirect('/create_module')

                        else:
                            #add the module to db
                            module = models.Module(module_form.module_title.data, module_form.module_code.data,
                                                   module_form.module_credits.data, module_form.module_year.data,
                                                   module_form.module_semester.data, module_form.class_size.data,
                                                   module_form.module_description.data, module_form.module_url.data)
                            teacher = models.Lecturer.query.filter_by(lecturer_name = module_form.lecturer_id.data).first()
                            module.lecturer = teacher
                            db.session.add(module)
                            db.session.commit()
                            flash("Module added successfully!")
                            logger.info("{} added to the database".format(module))
                            #change to display_courses
                            return redirect('/display_modules')
                else:
                    #add the course to db
                    module = models.Module(module_form.module_title.data, module_form.module_code.data,
                                           module_form.module_credits.data, module_form.module_year.data,
                                           module_form.module_semester.data, module_form.class_size.data,
                                           module_form.module_description.data, module_form.prerequisites.data,
                                           module_form.module_url.data)
                    db.session.add(module)
                    db.session.commit()
                    flash("Module added successfully!")
                    logger.info("{} added to the database".format(module))
                    #change to display_courses
                    return redirect('/display_modules')

            return render_template('/create_module.html',
                                    user = user,
                                    title='Create Module',
                                    form=module_form)
    return redirect('/')

# Display modules
@login_required
@app.route('/display_modules', methods=['GET', 'POST'])
def display_modules():
    user = current_user
    all_modules = models.Module.query.all()

    return render_template('/display_modules.html',
                            title='Display Modules',
                            modules = all_modules,
                            user = user)

#Remove module from admin panel
@login_required
@app.route('/display_modules/<int:id>', methods=['GET', 'POST'])
def remove_module_admin_panel(id):
    if current_user.is_authenticated:
        if current_user.student_email == "admin@leeds.ac.uk":
            #get the id of the trainer and remove it from the db
            module = models.Module.query.get(id)
            db.session.delete(module)
            db.session.commit()

            flash('{} successfully removed a module!'.format(module))
            logger.info('{} successfully removed a module'.format(module))

            return redirect('/display_modules')

    return redirect('/')

#Edit Module
@login_required
@app.route('/edit_module_details/<int:id>', methods=['GET', 'POST'])
def edit_module(id):
    user = current_user
    if current_user.is_authenticated:
        if current_user.student_email == "admin@leeds.ac.uk":
            module = models.Module.query.get(id)
            mod_title = module.module_title

            if module:
                module_form = ModuleForm()
                if request.method == 'POST' and module_form.validate():

                    module.module_title = module_form.module_title.data
                    module.module_code = module_form.module_code.data
                    module.module_credits = module_form.module_credits.data
                    module.module_year = module_form.module_year.data
                    module.module_semester = module_form.module_semester.data
                    module.class_size = module_form.class_size.data
                    module.module_description = module_form.module_description.data
                    module.module_url = module_form.module_url.data

                    db.session.commit()
                    flash('Module updated successfully!')
                    return redirect('/display_modules')
                return render_template('edit_module.html',
                                        user=user,
                                        form=module_form,
                                        module=module)
            else:
                return 'Error loading #{id}'.format(id=id)

@login_required
@app.route('/module_chooser', methods=['GET', 'POST'])
def module_chooser():
    user = current_user
    user_id = user.id
    user_course = user.course_id

    records = models.Record.query.filter_by(student_id=user_id).all()
    course_id = models.Course.query.get(user_course)
    user_compul_modules = course_id.modules

    credits_1y = course_id.course_1y_credits
    credits_2y = course_id.course_2y_credits
    credits_3y = course_id.course_3y_credits
    credits_4y = 0
    if course_id.course_4y_credits:
        credits_4y = course_id.course_4y_credits


    all_modules = course_id.optional_modules
    sel_mod_prereq_list = []
    chosen_mod_prereq_list = []
    list_modules = []
    chosen_list_modules = []
    future_choices = []
    calculated_credits = {}


    all_user_modules = []
    for record in records:
        user_module = models.Module.query.get(record.module_id)
        all_user_modules.append(user_module)

    calculated_credits = calculate_credits(user)


    needed_1y = calculated_credits['cr_1y']
    needed_2y = calculated_credits['cr_2y']
    needed_3y = calculated_credits['cr_3y']
    needed_4y = calculated_credits['cr_4y']


    if request.method == 'POST':
        data = request.get_json()
        mod_id = ""
        mod_code = ""
        for item in data:
            if item == "id":
                mod_id = data['id']
            elif item == "code":
                mod_code = data['code']

        if mod_id != "":
            selected_module = models.Module.query.get(mod_id)

            if selected_module.lecturer:
                lecturer = selected_module.lecturer
                lecturer_name = lecturer.lecturer_degree + " " + lecturer.lecturer_name
            else:
                lecturer_name = "Lecturer is not assigned"

            sel_mod_prereq_list = selected_module.prerequisites.split("|")
            future_choices = find_future_modules(mod_id)
            list_taken_mod = []

            #Check if prerequisite is taken
            if selected_module.prerequisites:
                for mod in sel_mod_prereq_list:
                    sel_mod = models.Module.query.filter_by(module_title = mod).first()
                    for record in records:
                        user_mod = models.Module.query.filter_by(id=record.module_id).first()
                        if sel_mod.module_title == user_mod.module_title:
                            list_taken_mod.append(sel_mod.module_title)

                for mod in sel_mod_prereq_list:
                    sel_mod = models.Module.query.filter_by(module_title = mod).first()

                    sel_mod_dict = {}
                    sel_mod_dict['prereq_id'] = sel_mod.id
                    sel_mod_dict['prereq_title'] = sel_mod.module_title
                    sel_mod_dict['prereq_code'] = sel_mod.module_code
                    if sel_mod.module_title in list_taken_mod:
                        sel_mod_dict['taken'] = "<span class=\"fa fa-check-circle\"></span>"
                    else:
                        sel_mod_dict['taken'] = "<span class=\"fa fa-times-circle\"></span>"

                    list_modules.append(sel_mod_dict)

                if future_choices:
                    return jsonify({"title": selected_module.module_title, "code": selected_module.module_code,
                    "lecturer": lecturer_name, "size": selected_module.class_size, "credits": selected_module.module_credits,
                    "description": selected_module.module_description, "url": selected_module.module_url,
                    "prerequisites": list_modules, "future_choices": future_choices })
                else:
                    return jsonify({"title": selected_module.module_title, "code": selected_module.module_code,
                    "lecturer": lecturer_name, "size": selected_module.class_size, "credits": selected_module.module_credits,
                    "description": selected_module.module_description, "url": selected_module.module_url,
                    "prerequisites": list_modules })
            else:
                if future_choices:
                    return jsonify({"title": selected_module.module_title, "code": selected_module.module_code,
                    "lecturer": lecturer_name, "size": selected_module.class_size, "credits": selected_module.module_credits,
                    "description": selected_module.module_description, "url": selected_module.module_url,
                    "future_choices": future_choices })
                else:
                    return jsonify({"title": selected_module.module_title, "code": selected_module.module_code,
                    "lecturer": lecturer_name, "size": selected_module.class_size, "credits": selected_module.module_credits,
                    "description": selected_module.module_description, "url": selected_module.module_url,  })
        elif mod_code != "":
            mod_code = data['code']
            chosen_module = models.Module.query.filter_by(module_code=mod_code).first()
            chosen_mod_prereq_list = chosen_module.prerequisites.split("|")
            list_of_records = []
            year_chosen_mod = chosen_module.module_year
            if year_chosen_mod == 1 and needed_1y == 0:
                return jsonify({"title": "", "code": "", "err_message": "You cannot exceed 120 credits!", "suc_message": "", "info_message": ""})
            elif year_chosen_mod == 2 and needed_2y == 0:
                return jsonify({"title": "", "code": "", "err_message": "You cannot exceed 120 credits!", "suc_message": "", "info_message": ""})
            elif year_chosen_mod == 3 and needed_3y == 0:
                return jsonify({"title": "", "code": "", "err_message": "You cannot exceed 120 credits!", "suc_message": "", "info_message": ""})
            elif year_chosen_mod == 4 and needed_4y == 0:
                return jsonify({"title": "", "code": "", "err_message": "You cannot exceed 120 credits!", "suc_message": "", "info_message": ""})
            else:
                assigned = update_optional_mod(user,chosen_module)

                if assigned == True:
                    return jsonify({"title": "", "code": "", "err_message": "You cannot assign this module. It is already assigned.", "suc_message": "", "info_message": ""})
                else:
                    #check if module has prerequisites
                    if chosen_module.prerequisites:
                        #Check if user has the required prerequisites
                        for mod in chosen_mod_prereq_list:
                            prereq_mod = models.Module.query.filter_by(module_title = mod).first()
                            for record in records:
                                user_mod = models.Module.query.filter_by(id=record.module_id).first()

                                if prereq_mod.module_title == user_mod.module_title:
                                    list_of_records.append(user_mod.module_title)

                        #If all prerequisites are taken then assgin module
                        if chosen_mod_prereq_list == list_of_records:
                            new_record = models.Record(user_id, chosen_module.id, 0,0)
                            user.record.append(new_record)
                            chosen_module.record.append(new_record)
                            db.session.commit()
                            return jsonify({"title": chosen_module.module_title, "code": chosen_module.module_code, "err_message": "", "suc_message": "Successfully assigned: ", "info_message": ""})

                        else:
                            for mod in chosen_mod_prereq_list:
                                if mod not in list_of_records:
                                    prereq = models.Module.query.filter_by(module_title=mod).first()
                            return jsonify({"title": prereq.module_title, "code": prereq.module_code, "err_message": "", "suc_message": "", "info_message": "First you need to take: "})
                    else:
                        new_record = models.Record(user_id, chosen_module.id, 0,0)
                        user.record.append(new_record)
                        chosen_module.record.append(new_record)
                        db.session.commit()
                        return jsonify({"title": chosen_module.module_title, "code": chosen_module.module_code,"err_message": "", "suc_message": "Successfully assigned: ", "info_message": ""})
        return redirect('/module_chooser')

    return render_template('/module_chooser.html',
                            title='Display Modules in Module Chooser',
                            modules = all_modules,
                            all_user_modules=all_user_modules,
                            user_compul_modules=user_compul_modules,
                            credits_1y=credits_1y,
                            credits_2y=credits_2y,
                            credits_3y=credits_3y,
                            credits_4y=credits_4y,
                            needed_1y=needed_1y,
                            needed_2y=needed_2y,
                            needed_3y=needed_3y,
                            needed_4y=needed_4y,
                            user = user)


def find_future_modules(id):
    module = models.Module.query.get(id)
    module_title = module.module_title
    mod_prereq_list = []
    list_modules = []

    all_modules = models.Module.query.all()

    for mod in all_modules:
        mod_prereq_list = mod.prerequisites.split("|")
        for prereq_title in mod_prereq_list:
            if module_title == prereq_title:
                mod_dict = {}
                mod_dict['future_id'] = mod.id
                mod_dict['future_title'] = mod.module_title
                mod_dict['future_code'] = mod.module_code
                list_modules.append(mod_dict)

    return list_modules

def calculate_credits(user):
    user_id = user.id
    user_course = user.course_id
    records = models.Record.query.filter_by(student_id=user_id).all()
    course_id = models.Course.query.get(user_course)
    tot_credits_1y = course_id.course_1y_credits
    tot_credits_2y = course_id.course_2y_credits
    tot_credits_3y = course_id.course_3y_credits
    tot_credits_4y = 0
    mod_cr_1y = 0
    mod_cr_2y = 0
    mod_cr_3y = 0
    mod_cr_4y = 0
    credits = {}
    if course_id.course_4y_credits:
        tot_credits_4y = course_id.course_4y_credits

    for record in records:
        user_module = models.Module.query.get(record.module_id)
        user_module_yr = user_module.module_year
        user_module_cr = user_module.module_credits
        if user_module_yr == 1:
            mod_cr_1y = mod_cr_1y + int(user_module_cr)
        elif user_module_yr == 2:
            mod_cr_2y = mod_cr_2y + int(user_module_cr)
        elif user_module_yr == 3:
            mod_cr_3y = mod_cr_3y + int(user_module_cr)
        elif user_module_yr == 4:
            mod_cr_4y = mod_cr_4y + int(user_module_cr)
    remaining_1y = int(tot_credits_1y) - int(mod_cr_1y)
    remaining_2y = int(tot_credits_2y) - int(mod_cr_2y)
    remaining_3y = int(tot_credits_3y) - int(mod_cr_3y)
    remaining_4y = int(tot_credits_4y) - int(mod_cr_4y)

    credits['cr_1y'] = remaining_1y
    credits['cr_2y'] = remaining_2y
    credits['cr_3y'] = remaining_3y
    credits['cr_4y'] = remaining_4y

    return credits

def update_optional_mod(user,chosen_mod):
    user_id = user.id
    user_course = user.course_id
    records = models.Record.query.filter_by(student_id=user_id).all()
    course_id = models.Course.query.get(user_course)

    assigned = False

    all_modules = course_id.optional_modules
    not_assigned_modules = []
    for record in records:
        user_module = models.Module.query.get(record.module_id)
        if user_module.id == chosen_mod.id:
            assigned = True
            return assigned
        else:
            assigned = False

# Remove module
@login_required
@app.route('/module_chooser/<int:id>', methods=['GET', 'POST'])
def remove_module(id):
    user = current_user
    course_id = user.course_id

    user_course = models.Course.query.get(course_id)
    compul_modules = user_course.modules
    compul = False

    if current_user.is_authenticated:
        #get the id of the module and remove it from the db
        module = models.Record.query.filter_by(module_id = id).first()
        actual_mod = models.Module.query.get(id)
        for compul_mod in compul_modules:
            if compul_mod.module_title == actual_mod.module_title:
                compul = True
        if compul == False:
            db.session.delete(module)
            db.session.commit()

            flash('{} successfully removed a module!'.format(actual_mod.module_title))
            logger.info('{} successfully removed a module'.format(module))
            return redirect('/module_chooser')
        else:
            flash('Compulsory module {} cannot be removed!'.format(actual_mod.module_title))
            logger.info('Compulsory module {} cannot be removed!'.format(actual_mod.module_title))

            return redirect('/module_chooser')

    return redirect('/')

@login_required
@app.route('/display_module_details/<int:id>', methods=['GET', 'POST'])
def display_module_details(id):
    user = current_user
    module= models.Module.query.get(id)
    lecturers = models.Lecturer.query.all()

    all_modules = models.Module.query.all()
    prerequisites = []
    module_prereq_list = []

    # Check if a module has been removed and update prerequisites
    if module.prerequisites and module.prerequisites != "":
        module_prereq_list = module.prerequisites.split("|")
        module.prerequisites = update_prerequisites(module_prereq_list)
        db.session.commit()

    # Make sure the current module doesn't appear on the prerequisites
    for prereq_module in all_modules:
        if prereq_module.module_title != module.module_title:
            unique=True
            for cur_module_prereq in module_prereq_list:
                if prereq_module.module_title == cur_module_prereq:
                    unique = False
            if unique == True:
                prerequisites.append(prereq_module)


    return render_template('/module_details.html',
                            title='Display Module Details',
                            user = user,
                            lecturers=lecturers,
                            module=module,
                            prerequisites=prerequisites,
                            module_prereq_list=module_prereq_list)

# Removes a module from the prerequisities of another module
@login_required
@app.route('/remove_prereq_from_module/<int:module_id>/<string:prereq>', methods=['GET', 'POST'])
def remove_prereq_from_module(module_id, prereq):
    if current_user.is_authenticated:
        if current_user.student_email == "admin@leeds.ac.uk":
            module = models.Module.query.get(module_id)

            prerequisites = module.prerequisites
            prereq_list = prerequisites.split("|")
            for i in range(len(prereq_list)):
                if prereq_list[i] == prereq:
                    del prereq_list[i]
                    break

            prerequisites = "|".join(prereq_list)
            module.prerequisites = prerequisites
            db.session.commit()

            return redirect('/display_module_details/' + str(module_id))

    return redirect ('/')

@login_required
@app.route('/add_lecturer_to_module', methods=['GET', 'POST'])
def add_lecturer_to_module():
    # Get the lecturer and module based on the admin's choice
    lecturer_id = request.form['lecturer_select']
    module_id = request.form['module']

    # Assign the lecturer to the module
    module = models.Module.query.get(module_id)
    module.lecturer_id = lecturer_id

    db.session.commit()
    return redirect('/display_module_details/' + module_id)

# Adds a prerequisite to a course's prerequisities
@login_required
@app.route('/assign_prerequisites_to_module', methods=['GET', 'POST'])
def assign_prerequisites_to_module():
    if current_user.is_authenticated:
        if current_user.student_email == "admin@leeds.ac.uk":
            prereq = request.form['prereq']
            module_id = request.form.get('module')
            module = models.Module.query.get(module_id)
            old_prereq = module.prerequisites

            if prereq == "" or prereq == None or prereq == "--None--":
                old_prereq = str(prereq)
            else:
                old_prereq = old_prereq + "|" + str(prereq)
                module.prerequisites = old_prereq
                db.session.commit()
            return redirect('/display_module_details/' + module_id)

    return redirect('/')


def update_prerequisites(prereq_list):
    all_modules = models.Module.query.all()
    module_titles = []
    for module in all_modules:
        module_titles.append(module.module_title)

    for title in prereq_list:
        if title not in module_titles:
            prereq_list.remove(title)

    new_modules = "|".join(prereq_list)
    return new_modules

@login_required
@app.route('/create_course', methods=['GET', 'POST'])
def create_course():
    # Only allow an admin to create a course
    if current_user.is_authenticated:
        if current_user.student_email == 'admin@leeds.ac.uk':
            user = current_user
            course_form = CourseForm()

            #when the create button is clicked
            if course_form.validate_on_submit():
                all_courses = models.Course.query.all()

                if all_courses:
                    for course in all_courses:
                        #check if the course already exists
                        if course_form.course_title.data == course.course_title:
                            flash("Course already exists!")
                            logger.warning("{} already exists".format(course))
                            return redirect('/create_course')

                        else:
                            #add the course to db
                            course = models.Course(course_form.course_title.data, course_form.course_degree_bach.data,
                                                   course_form.course_degree_mast.data, course_form.course_1y_credits.data,
                                                   course_form.course_2y_credits.data, course_form.course_3y_credits.data,
                                                   course_form.course_4y_credits.data)
                            db.session.add(course)
                            db.session.commit()
                            flash("Course added successfully!")
                            logger.info("{} added to the database".format(course))
                            #change to display_courses
                            return redirect('/display_courses')

            return render_template('/create_course.html',
                                    user = user,
                                    title='Create Course',
                                    form=course_form)
    return redirect('/')


#Remove module from admin panel
@login_required
@app.route('/display_courses/<int:id>', methods=['GET', 'POST'])
def remove_course_admin_panel(id):
    if current_user.is_authenticated:
        if current_user.student_email == "admin@leeds.ac.uk":
            #get the id of the trainer and remove it from the db
            course = models.Course.query.get(id)
            db.session.delete(course)
            db.session.commit()

            flash('{} successfully removed a course!'.format(course))
            logger.info('{} successfully removed a course'.format(course))

            return redirect('/display_courses')

    return redirect('/')

#Edit Course Details
@login_required
@app.route('/edit_course_details/<int:id>', methods=['GET', 'POST'])
def edit_course_details(id):
    user = current_user
    if current_user.is_authenticated:
        if current_user.student_email == "admin@leeds.ac.uk":
            course = models.Course.query.get(id)

            if course:
                course_form = CourseForm()
                if request.method == 'POST' and course_form.validate():

                    course.course_title = course_form.course_title.data
                    course.course_degree_bach = course_form.course_degree_bach.data
                    course.course_degree_mast = course_form.course_degree_mast.data
                    course.course_1y_credits = course_form.course_1y_credits.data
                    course.course_2y_credits = course_form.course_2y_credits.data
                    course.course_3y_credits = course_form.course_3y_credits.data
                    course.course_4y_credits = course_form.course_4y_credits.data


                    db.session.commit()
                    flash('Course updated successfully!')
                    return redirect('/display_courses')
                return render_template('edit_course.html',
                                        user=user,
                                        form=course_form,
                                        course=course)
            else:
                return 'Error loading #{id}'.format(id=id)


@login_required
@app.route('/display_courses', methods=['GET', 'POST'])
def display_courses():
    user = current_user
    all_courses = models.Course.query.all()

    return render_template('/display_courses.html',
                            title='Display Courses',
                            courses = all_courses,
                            user = user
                            )

@login_required
@app.route('/display_course_details/<int:id>', methods=['GET', 'POST'])
def display_course_details(id):
    user = current_user
    course = models.Course.query.get(id) #post
    all_modules = models.Module.query.all()
    #compulsory_modules = course.compulsory
    compulsory_modules_list = [] #post_terms
    optional_modules_list = [] #post_terms

    #post = Posts.query.get_or_404(id)
    #post_terms=[]
    for module in course.modules:
        compulsory_modules_list.append(module.id)
    all_modules = models.Module.query.all()
    if request.method == 'POST':
            new_compulsory_module=request.form.getlist('module_id')
            #Add new compulsory module
            for module_id in new_compulsory_module:
                if module_id not in compulsory_modules_list:
                  module=models.Module.query.get(module_id)
                  course.modules.append(module)
            #Remove old post terms which are not included in the update.
            for course_module_id in new_compulsory_module:
                if course_module_id not in new_compulsory_module:
                      module=models.Module.query.get(course_module_id)
                      course.modules.remove(module)

            db.session.commit()

    for module in course.optional_modules:
        optional_modules_list.append(module.id)
    all_modules = models.Module.query.all()
    if request.method == 'POST':
            new_optional_module=request.form.getlist('module_op_id')
            #Add new compulsory module
            for module_id in new_optional_module:
                if module_id not in optional_modules_list:
                  module=models.Module.query.get(module_id)
                  course.optional_modules.append(module)
            #Remove old post terms which are not included in the update.
            for course_module_id in new_optional_module:
                if course_module_id not in new_optional_module:
                      module=models.Module.query.get(course_module_id)
                      course.optional_modules.remove(module)

            db.session.commit()

    return render_template('/course_details.html',
                            title='Display Courses Details',
                            user = user,
                            course=course,
                            modules=all_modules,
                            compulsory_modules_list=compulsory_modules_list,
                            optional_modules_list=optional_modules_list)

# Remove compulsory module form course
@login_required
@app.route('/remove_compul_from_course/<int:course_id>/<int:compul>', methods=['GET', 'POST'])
def remove_compul_from_course(course_id, compul):
    if current_user.is_authenticated:
        if current_user.student_email == "admin@leeds.ac.uk":
            course = models.Course.query.get(course_id)
            module_d = models.Module.query.get(compul)
            course.modules.remove(module_d)
            db.session.commit()

            return redirect('/display_course_details/' + str(course_id))

    return redirect ('/')

# Remove optional module form course
@login_required
@app.route('/remove_optional_from_course/<int:course_id>/<int:optional>', methods=['GET', 'POST'])
def remove_optional_from_course(course_id, optional):
    if current_user.is_authenticated:
        if current_user.student_email == "admin@leeds.ac.uk":
            course = models.Course.query.get(course_id)
            module_d = models.Module.query.get(optional)
            course.optional_modules.remove(module_d)
            db.session.commit()

            return redirect('/display_course_details/' + str(course_id))

    return redirect ('/')


@login_required
@app.route('/create_lecturer', methods=['GET', 'POST'])
def create_lecturer():
    if current_user.is_authenticated:
        if current_user.student_email == 'admin@leeds.ac.uk':
            user = current_user
            lecturer_form = LecturerForm()

            if lecturer_form.validate_on_submit():
                #request the data that is typed in the form
                lecturer = models.Lecturer(lecturer_form.lecturer_name.data, lecturer_form.lecturer_email.data,
                                            lecturer_form.lecturer_degree.data)

                #adds the lecturer to the database
                db.session.add(lecturer)
                db.session.commit()
                flash("Lecturer added successfully!")
                logger.info("{} added to the database".format(lecturer))
                #change to display_trainers
                return redirect('/display_lecturers')

            return render_template('/create_lecturer.html',
                                title='Create Lecturer',
                                user = user,
                                form=lecturer_form)

    return redirect('/')

#Remove lecturer from admin panel
@login_required
@app.route('/display_lecturers/<int:id>', methods=['GET', 'POST'])
def remove_lecturer_admin_panel(id):
    if current_user.is_authenticated:
        if current_user.student_email == "admin@leeds.ac.uk":
            #get the id of the trainer and remove it from the db
            lecturer = models.Lecturer.query.get(id)
            db.session.delete(lecturer)
            db.session.commit()

            flash('{} successfully removed a lecturer!'.format(lecturer))
            logger.info('{} successfully removed a lecturer'.format(lecturer))

            return redirect('/display_lecturers')

    return redirect('/')

#Edit Lecturer Details
@login_required
@app.route('/edit_lecturer_details/<int:id>', methods=['GET', 'POST'])
def edit_lecturer_details(id):
    user = current_user
    if current_user.is_authenticated:
        if current_user.student_email == "admin@leeds.ac.uk":
            lecturer = models.Lecturer.query.get(id)

            if lecturer:
                lecturer_form = LecturerForm()
                if request.method == 'POST' and lecturer_form.validate():

                    lecturer.lecturer_name = lecturer_form.lecturer_name.data
                    lecturer.lecturer_degree = lecturer_form.lecturer_degree.data
                    lecturer.lecturer_email = lecturer_form.lecturer_email.data


                    db.session.commit()
                    flash('Lecturer updated successfully!')
                    return redirect('/display_lecturers')
                return render_template('edit_lecturer.html',
                                        user=user,
                                        form=lecturer_form,
                                        lecturer=lecturer)
            else:
                return 'Error loading #{id}'.format(id=id)


@login_required
@app.route('/display_lecturers', methods=['GET', 'POST'])
def display_lecturers():
    user = current_user
    #retrieve all trainers from db
    all_lecturers = models.Lecturer.query.all()

    return render_template('/display_lecturers.html',
                            title='Display Lecturers',
                            user = user,
                            lecturers=all_lecturers)

@login_manager.user_loader
def load_user(id):
  return models.Student.query.get(int(id))

@app.before_request
def before_request():
   guest = current_user
