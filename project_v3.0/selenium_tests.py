from selenium import webdriver
from app import app, db, models
from datetime import datetime, timedelta, date

import unittest
import selenium
import time

from flask_login import LoginManager, login_user,logout_user,current_user,login_required
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.common.keys import Keys

class TestCase(unittest.TestCase):

	def login_user(self, email, password):
		time.sleep(0.5)
		self.driver.find_element_by_id("student_email").send_keys(email)
		self.driver.find_element_by_id("student_password").send_keys(password)
		time.sleep(1)
		self.driver.find_element_by_id("sign_in_button").click()
		time.sleep(1)

	def logout_and_login(self, email, password):
		try:
			self.driver.find_element_by_id("sign_out_link").click()
			self.login_user(email, password)
		except NoSuchElementException:
			self.login_user(email, password)

	def setUp(self):
		self.driver = webdriver.Firefox()
		self.addCleanup(self.driver.quit)
		self.driver.get('http://localhost:5000')

	def test_create_course(self):
		self.logout_and_login("admin@leeds.ac.uk", "admin")
		courses = len(models.Course.query.all())
		self.driver.find_element_by_id("create_dropdown_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("create_course_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("course_title").send_keys("Selenium Course")
		self.driver.find_element_by_id("course_degree_bach").send_keys("BSc")
		self.driver.find_element_by_id("course_degree_mast").send_keys("MEng")
		self.driver.find_element_by_id("course_1y_credits").send_keys("120")
		self.driver.find_element_by_id("course_2y_credits").send_keys("120")
		self.driver.find_element_by_id("course_3y_credits").send_keys("120")
		self.driver.find_element_by_id("course_4y_credits").send_keys("120")
		time.sleep(3)
		self.driver.find_element_by_id("create_course_button").click()
		courses = courses + 1
		time.sleep(1)
		assert len(models.Course.query.all()) == courses
		time.sleep(3)

	def test_create_module(self):
		self.logout_and_login("admin@leeds.ac.uk", "admin")
		modules = len(models.Module.query.all())
		self.driver.find_element_by_id("create_dropdown_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("create_module_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("module_code").send_keys("Selenium Code")
		self.driver.find_element_by_id("module_title").send_keys("Selenium Title")
		self.driver.find_element_by_id("module_credits").send_keys("10")
		self.driver.find_element_by_id("module_year").send_keys("1")
		self.driver.find_element_by_id("module_semester").send_keys("1")
		self.driver.find_element_by_id("class_size").send_keys("200")
		self.driver.find_element_by_id("module_description").send_keys("Selenium Description")
		self.driver.find_element_by_id("module_url").send_keys("Selenium Url")
		time.sleep(3)
		self.driver.find_element_by_id("create_module_button").click()
		modules = modules + 1
		time.sleep(1)
		assert len(models.Module.query.all()) == modules
		time.sleep(3)

	def test_create_lecturer(self):
		self.logout_and_login("admin@leeds.ac.uk", "admin")
		lecturers = len(models.Lecturer.query.all())
		self.driver.find_element_by_id("create_dropdown_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("create_lecturer_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("lecturer_degree").send_keys("Dr")
		self.driver.find_element_by_id("lecturer_name").send_keys("Selenium Name")
		self.driver.find_element_by_id("lecturer_email").send_keys("Selenium Email")
		time.sleep(3)
		self.driver.find_element_by_id("create_lecturer_button").click()
		lecturers = lecturers + 1
		time.sleep(1)
		assert len(models.Lecturer.query.all()) == lecturers
		time.sleep(3)

	def test_assign_trainer(self):
		self.logout_and_login("admin@leeds.ac.uk", "admin")
		self.driver.find_element_by_id("display_dropdown_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("display_module_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("module2code").click()
		time.sleep(1)
		self.driver.find_element_by_id("module2edit").click()
		time.sleep(1)
		self.driver.find_element_by_id("select_lecturer_menu").click()
		time.sleep(1)
		self.driver.find_element_by_id("lecturer1").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("lecturer1").send_keys(Keys.ENTER)
		time.sleep(1)
		self.driver.find_element_by_id("assign_lecturer_button").click()
		time.sleep(4)

	def test_add_prerequisite(self):
		self.logout_and_login("admin@leeds.ac.uk", "admin")
		self.driver.find_element_by_id("display_dropdown_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("display_module_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("module2code").click()
		time.sleep(1)
		self.driver.find_element_by_id("module2edit").click()
		time.sleep(1)
		self.driver.find_element_by_id("select_prerequisite_menu").click()
		time.sleep(1)
		self.driver.find_element_by_id("premodule4").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("premodule4").send_keys(Keys.ENTER)
		time.sleep(1)
		self.driver.find_element_by_id("assign_prerequisite_button").click()
		time.sleep(4)

	def test_add_compulsory_module(self):
		self.logout_and_login("admin@leeds.ac.uk", "admin")
		self.driver.find_element_by_id("display_dropdown_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("display_course_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("course1title").click()
		time.sleep(1)
		self.driver.find_element_by_id("course1edit").click()
		time.sleep(1)
		self.driver.find_element_by_id("select_compulsory_modules_menu").click()
		time.sleep(1)
		self.driver.find_element_by_id("module2").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("module2").send_keys(Keys.ENTER)
		time.sleep(1)
		self.driver.find_element_by_id("save_compulsory_modules_button").click()
		time.sleep(4)

	def test_add_optional_module(self):
		self.logout_and_login("admin@leeds.ac.uk", "admin")
		self.driver.find_element_by_id("display_dropdown_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("display_course_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("course1title").click()
		time.sleep(1)
		self.driver.find_element_by_id("course1edit").click()
		time.sleep(1)
		self.driver.find_element_by_id("select_optional_modules_menu").click()
		time.sleep(1)
		self.driver.find_element_by_id("optmodule2").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("optmodule2").send_keys(Keys.ENTER)
		time.sleep(1)
		self.driver.find_element_by_id("save_optional_modules_button").click()
		time.sleep(4)

	def test_edit_module(self):
		self.logout_and_login("admin@leeds.ac.uk", "admin")
		self.driver.find_element_by_id("display_dropdown_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("display_module_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("edit_module_link").click()
		time.sleep(1)
		self.driver.find_element_by_id("module_code").send_keys("Edit")
		self.driver.find_element_by_id("module_title").send_keys("Selenium Title")
		self.driver.find_element_by_id("module_credits").send_keys("20")
		self.driver.find_element_by_id("module_year").send_keys("2")
		self.driver.find_element_by_id("module_semester").send_keys("2")
		self.driver.find_element_by_id("class_size").send_keys("100")
		self.driver.find_element_by_id("module_description").send_keys("Selenium Description")
		self.driver.find_element_by_id("module_url").send_keys("Selenium Url")
		time.sleep(3)
		self.driver.find_element_by_id("edit_module_button").click()
		time.sleep(3)

	def test_edit_course(self):
		self.logout_and_login("admin@leeds.ac.uk", "admin")
		self.driver.find_element_by_id("display_dropdown_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("display_course_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("edit_course_link").click()
		time.sleep(1)
		self.driver.find_element_by_id("course_title").send_keys("Selenium Course Edit")
		self.driver.find_element_by_id("course_degree_bach").send_keys("BSc")
		self.driver.find_element_by_id("course_degree_mast").send_keys("MEng")
		self.driver.find_element_by_id("course_1y_credits").send_keys("100")
		self.driver.find_element_by_id("course_2y_credits").send_keys("120")
		self.driver.find_element_by_id("course_3y_credits").send_keys("120")
		self.driver.find_element_by_id("course_4y_credits").send_keys("140")
		time.sleep(3)
		self.driver.find_element_by_id("edit_course_button").click()
		time.sleep(3)

	def test_edit_lecturer(self):
		self.logout_and_login("admin@leeds.ac.uk", "admin")
		self.driver.find_element_by_id("display_dropdown_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("display_lecturer_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("edit_lecturer_link").click()
		time.sleep(1)
		self.driver.find_element_by_id("lecturer_degree").send_keys("Dr")
		self.driver.find_element_by_id("lecturer_name").send_keys("Selenium Name")
		self.driver.find_element_by_id("lecturer_email").send_keys("Selenium Email")
		time.sleep(3)
		self.driver.find_element_by_id("edit_lecturer_button").click()
		time.sleep(3)

	def test_module_assign(self):
		self.logout_and_login("aaa@leeds.ac.uk", "1111")
		self.driver.find_element_by_id("module_chooser_link").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("module8id").click()
		time.sleep(0.5)

		self.driver.find_element_by_id("mod_assign_btn").click()
		time.sleep(0.5)
		self.driver.find_element_by_id("module8remove").click()
		time.sleep(4)

if __name__ == '__main__':
    unittest.main()
