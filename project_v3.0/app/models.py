from app import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import date, datetime, timedelta
from app import bcrypt

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), primary_key=True)
    remaining_credits = db.Column(db.Integer)
    approved = db.Column(db.Boolean)

    def __init__(self, id, student_id, module_id, remaining_credits, approved=False):
        self.id = id
        self.student_id = student_id
        self.module_id = module_id
        self.remaining_credits = remaining_credits
        self.approved = approved

    def __repr__(self):
        return '<Record for: (id, student, module): {}, {}, {}, {}, {}>'.format(self.id, self.student_id, self.module_id, self.remaining_credits, self.approved)


compulsory_modules=db.Table('compulsory_modules',
                             db.Column('course_id', db.Integer,db.ForeignKey('courses.id'), nullable=False),
                             db.Column('module_id',db.Integer,db.ForeignKey('modules.id'),nullable=False),
                             db.PrimaryKeyConstraint('course_id', 'module_id') )

class CompulsoryModules():
    def __init__(self,course_id,module_id):
      self.course_id=course_id
      self.module_id=module_id

db.mapper(CompulsoryModules, compulsory_modules)

optional_modules=db.Table('optional_modules',
                             db.Column('course_id', db.Integer,db.ForeignKey('courses.id'), nullable=False),
                             db.Column('module_id',db.Integer,db.ForeignKey('modules.id'),nullable=False),
                             db.PrimaryKeyConstraint('course_id', 'module_id') )

class OptionalModules():
    def __init__(self,course_id,module_id):
      self.course_id=course_id
      self.module_id=module_id

db.mapper(OptionalModules, optional_modules)


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_email = db.Column(db.String(50), index=True)
    student_password = db.Column(db.String(50))
    student_name = db.Column(db.String(50))
    current_year = db.Column(db.Integer)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    course = relationship("Course", backref="course")
    record = relationship('Record', backref='student', primaryjoin=id == Record.student_id, cascade="save-update, merge, delete, delete-orphan")

    def __init__(self, student_email, student_password, student_name, current_year):
        self.student_email = student_email
        self.student_password = bcrypt.generate_password_hash(student_password)
        self.student_name = student_name
        self.current_year = current_year


    def __repr__(self):
        return '<Student {}>'.format(self.student_name)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Module(db.Model):
    __tablename__ = 'modules'
    id = db.Column(db.Integer, primary_key=True)
    module_title = db.Column(db.String(100), index=True)
    module_code = db.Column(db.String(10))
    module_credits = db.Column(db.Integer)
    module_year = db.Column(db.Integer)
    module_semester = db.Column(db.Integer)
    class_size = db.Column(db.Integer)
    module_description = db.Column(db.String(4000))
    module_url = db.Column(db.String(1000))
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturers.id'))
    prerequisites = db.Column(db.String, default="")
    record = relationship('Record', backref='module', primaryjoin=id == Record.module_id, cascade="save-update, merge, delete, delete-orphan")
    #compulsory = relationship('CompulsoryModules', backref='modules', primaryjoin=id == CompulsoryModules.module_id, cascade="save-update, merge, delete, delete-orphan")


    def __init__(self, module_title, module_code, module_credits, module_year, module_semester, class_size, module_description, module_url):
        self.module_title = module_title
        self.module_code = module_code
        self.module_credits = module_credits
        self.module_year = module_year
        self.module_semester = module_semester
        self.class_size = class_size
        self.module_description = module_description
        self.module_url = module_url

    def __repr__(self):
        return self.module_title

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer,primary_key=True)
    course_title = db.Column(db.String(50))
    course_degree_bach = db.Column(db.String(5))
    course_degree_mast = db.Column(db.String(5))
    course_1y_credits = db.Column(db.Integer)
    course_2y_credits = db.Column(db.Integer)
    course_3y_credits = db.Column(db.Integer)
    course_4y_credits = db.Column(db.Integer)
    #compulsory = relationship('CompulsoryModules',backref='courses', uselist=False, primaryjoin=id == CompulsoryModules.course_id, cascade="save-update, merge, delete, delete-orphan")
    modules=db.relationship('Module', secondary=compulsory_modules, backref='compulsory_for_courses' )
    optional_modules=db.relationship('Module', secondary=optional_modules, backref='optional_for_courses' )


    def __init__(self, course_title, course_degree_bach, course_degree_mast, course_1y_credits, course_2y_credits,
                 course_3y_credits, course_4y_credits):
        self.course_title = course_title
        self.course_degree_bach = course_degree_bach
        self.course_degree_mast = course_degree_mast
        self.course_1y_credits = course_1y_credits
        self.course_2y_credits = course_2y_credits
        self.course_3y_credits = course_3y_credits
        self.course_4y_credits = course_4y_credits

    def __repr__(self):
        return 'Course: {}'.format(self.course_title)

class Lecturer(db.Model):
    __tablename__ = 'lecturers'
    id = db.Column(db.Integer, primary_key=True)
    lecturer_name = db.Column(db.String(50), index=True)
    lecturer_email = db.Column(db.String(50))
    lecturer_degree = db.Column(db.String(20))
    modules = db.relationship('Module', backref='lecturer', lazy='dynamic')

    def __init__(self, lecturer_name, lecturer_email, lecturer_degree):
        self.lecturer_name = lecturer_name
        self.lecturer_email = lecturer_email
        self.lecturer_degree = lecturer_degree

    def __repr__(self):
        return self.lecturer_name
