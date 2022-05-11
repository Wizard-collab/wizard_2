import argparse
import traceback
import logging
from wizard.core import environment
from wizard.core import site
from wizard.core import user
from wizard.core import custom_logger
from wizard.core import db_core
from wizard.core import communicate
from wizard.core import launch

custom_logger.get_root_logger()
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('-psqlDns', dest='psql_dns', type=str, help='PostgreSQL connection DNS')
parser.add_argument('-site', dest='site', type=str, help='Wizard site')
parser.add_argument('-user', dest='user', type=str, help='Wizard user')
parser.add_argument('-project', dest='project', type=str, help='Wizard project')
parser.add_argument('-teamDns', dest='team_dns', type=str, help='Wizard team connection DNS')
parser.add_argument('-pyfile', dest='pyfile', type=str, help='The python file to execute')
args = parser.parse_args()

if not args.psql_dns:
	logging.error("Please provide a PostgreSQL DNS")
if not args.site:
	logging.error("Please provide a site")
if not args.user:
	logging.error("Please provide a user")
if not args.project:
	logging.error("Please provide a project")
if not args.pyfile:
	logging.error("Please provide a python file to execute")

environment.set_psql_dns(args.psql_dns)
db_server = db_core.db_server()
db_server.start()

environment.set_site(args.site)
db_server.site=environment.get_site()

user_row = site.get_user_row_by_name(args.user)
environment.build_user_env(user_row)

project_row = site.get_project_row_by_name(args.project)
environment.build_project_env(project_row['project_name'], project_row['project_path'])

db_server.project_name = environment.get_project_name()

communicate_server = communicate.communicate_server()
communicate_server.start()

softwares_server = launch.softwares_server()
softwares_server.start()

try:
    exec(open(args.pyfile).read())
except:
    logger.error(str(traceback.format_exc()))
finally:
    db_server.stop()
    softwares_server.stop()
    communicate_server.stop()