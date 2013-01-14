#!/usr/bin/env python
import os.path as p
import app.manage_helper as mh

from subprocess import call, check_output
from pprint import pprint

from flask import current_app as app, url_for
from flask.ext.script import Manager
from app import create_app, db

manager = Manager(create_app)
manager.add_option(
	'-m', '--cfgmode', dest='config_mode', default='Development')
manager.add_option('-f', '--cfgfile', dest='config_file', type=p.abspath)


def get_api_endpoint():
	with app.app_context():
		site = url_for('api', _external=True).split('/')

		if site[2] == 'localhost':
			site[2] = 'localhost:%s' % app.config['PORT']

		site = '/'.join(site)
		return site


@manager.command
def checkstage():
	"""Checks staged with git pre-commit hook"""

	path = p.join(p.dirname(__file__), 'app', 'tests', 'test.sh')
	cmd = "sh %s" % path
	return call(cmd, shell=True)


@manager.command
def createdb():
	"""Creates database if it doesn't already exist"""

	with app.app_context():
		db.create_all()
		print 'Database created'


@manager.command
def cleardb():
	"""Removes all content from database"""

	with app.app_context():
		db.drop_all()
		print 'Database cleared'


@manager.command
def resetdb():
	"""Removes all content from database and creates new tables"""

	with app.app_context():
		cleardb()
		createdb()


@manager.command
def initdb():
	"""Removes all content from database and initializes it
		with default values
	"""

	with app.app_context():
		resetdb()
		values = mh.get_init_values()
		content = mh.process(values)
		post(content, mh.get_api_endpoint())
		print 'Database initialized'


@manager.command
def popdb():
	"""Removes all content from database and populates it
		with sample data
	"""

	with app.app_context():
		initdb()
		values = mh.get_pop_values()
		content = mh.process(values)
		post(content, mh.get_api_endpoint())
		print 'Database populated'

if __name__ == '__main__':
	manager.run()
