from flask_wtf import Form
from wtforms import StringField, PasswordField, TextField, IntegerField, DateField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired,Email
from app import db, models
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app import db, models

def modules_select():
    return models.Module.query.filter_by(module_title="Databases").first()

class SignUpForm(Form):
    student_email = StringField('student_email', validators=[DataRequired(),Email()], render_kw={"placeholder": "Email"})
    confirm_email = StringField('confirm_email', validators=[DataRequired(),Email()], render_kw={"placeholder": "Confirm Email"})
    student_password = PasswordField('student_password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    student_name = StringField('student_name', validators=[DataRequired()], render_kw={"placeholder": "Full Name"})
    current_year = IntegerField('current_year', validators=[DataRequired()], render_kw={"placeholder": "Current Year of Study"})
    course_id = TextField('course_id', validators=[DataRequired()], render_kw={"placeholder": "Course"})

class SignInForm(Form):
    student_email = StringField('student_email', validators=[DataRequired(),Email()], render_kw={"placeholder": "Email"})
    student_password = PasswordField('student_password', validators=[DataRequired()], render_kw={"placeholder": "Password"})

class ChangePasswordForm(Form):
    current_password = PasswordField('current_password', validators=[DataRequired()], render_kw={"placeholder": "Current Password"})
    new_password = PasswordField('new_password', validators=[DataRequired()], render_kw={"placeholder": "New Password"})
    confirm_new_password = PasswordField('confirm_new_password', validators=[DataRequired()], render_kw={"placeholder": "Confirm New Password"})

class CourseForm(Form):
    course_title = StringField('course_title', validators=[DataRequired()], render_kw={"placeholder": "Title"})
    course_degree_bach = StringField('course_degree_bach', validators=[DataRequired()], render_kw={"placeholder": "Bachelor Degree"})
    course_degree_mast = StringField('course_degree_mast', validators=[DataRequired()], render_kw={"placeholder": "Masters Degree"})
    course_1y_credits = IntegerField('course_1y_credits', validators=[DataRequired()], render_kw={"placeholder": "1st Year Credits"})
    course_2y_credits = IntegerField('course_2y_credits', validators=[DataRequired()], render_kw={"placeholder": "2nd Year Credits"})
    course_3y_credits = IntegerField('course_3y_credits', validators=[DataRequired()], render_kw={"placeholder": "3rd Year Credits"})
    course_4y_credits = IntegerField('course_4y_credits', validators=[DataRequired()], render_kw={"placeholder": "4th Year Credits"})

class ModuleForm(Form):
    module_title = StringField('module_title',validators=[DataRequired()], render_kw={"placeholder": "Title"})
    module_code = StringField('module_code',validators=[DataRequired()], render_kw={"placeholder": "Code"})
    module_credits = IntegerField('module_credits',validators=[DataRequired()], render_kw={"placeholder": "Credits"})
    module_year = IntegerField('module_year',validators=[DataRequired()], render_kw={"placeholder": "Level"})
    module_semester = IntegerField('module_semester',validators=[DataRequired()], render_kw={"placeholder": "Semester"})
    class_size = IntegerField('room_capacity',validators=[DataRequired()], render_kw={"placeholder": "Class Size"})
    module_description = StringField('module_description', render_kw={"placeholder": "Description"})
    module_url = StringField('module_url',validators=[DataRequired()], render_kw={"placeholder": "URL"})
    lecturer_id = TextField('lecturer_id', render_kw={"placeholder": "Lecturer"})

class LecturerForm(Form):
    lecturer_name = StringField('lecturer_name', validators=[DataRequired()], render_kw={"placeholder": "Name"})
    lecturer_email = StringField('lecturer_email', validators=[DataRequired()], render_kw={"placeholder": "Email"})
    lecturer_degree = StringField('lecturer_degree', validators=[DataRequired()], render_kw={"placeholder": "Degree"})
