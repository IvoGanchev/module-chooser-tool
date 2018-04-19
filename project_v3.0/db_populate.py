from app import app
from app import db, models
from datetime import datetime, timedelta, date
import csv, sys

#Reserve the username admin for the owner who manages the website
admin = models.Student(student_email="admin@leeds.ac.uk", student_password="admin", student_name="admin", current_year = 0)





# record = models.Record(1, student_1.id, module_1.id, 0)
# student_1.record.append(record)
# module_1.record.append(record)
#course_1.class_size+=1
# compulsory = models.CompulsoryModules(1, course_1.id, module_1.id)
# course_1.compulsory.append(compulsory)
# module_1.compulsory.append(compulsory)


db.session.add(admin)


db.session.commit()
with open('csv/ALL_Modules.csv', 'r', newline='', encoding='utf-8-sig') as csv_file:
    reader = csv.DictReader(csv_file, delimiter=',')
    for row in reader:

        title = format(row['Title'])
        code = format(row['Code'])
        credits = int(row['Credits'])
        year = int(row['Year'])
        semester = int(row['Semester'])
        size = int(row['Class size'])
        description = format(row['Description'])
        url = format(row['URL'])

        module = models.Module(module_title=title, module_code=code, module_credits=credits,
        module_year=year, module_semester=semester, class_size=size, module_description=description,
        module_url=url)
        db.session.add(module)

        db.session.commit()

with open('csv/ALL_Lecturers.csv', 'r', newline='', encoding='utf-8-sig') as csv_file:
    reader = csv.DictReader(csv_file, delimiter=',')
    for row in reader:

        degree = format(row['Degree'])
        name = format(row['Name'])
        email = format(row['Email'])

        lecturer = models.Lecturer(lecturer_name=name, lecturer_email=email, lecturer_degree=degree)
        db.session.add(lecturer)

        db.session.commit()
