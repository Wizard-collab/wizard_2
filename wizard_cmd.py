import argparse
import traceback
import json
import logging
from wizard.core import application
from wizard.core import environment
from wizard.core import site
from wizard.core import user
from wizard.core import project
from wizard.core import assets
from wizard.core import custom_logger
from wizard.core import db_core
from wizard.core import communicate
from wizard.core import launch
from wizard.core import launch_batch

custom_logger.get_root_logger()
logger = logging.getLogger(__name__)

application.log_app_infos()
print('Wizard CMD')

parser = argparse.ArgumentParser()
parser.add_argument('-psqlDns', dest='psql_dns', type=str, help='PostgreSQL connection DNS')
parser.add_argument('-site', dest='site', type=str, help='Wizard site')
parser.add_argument('-user', dest='user', type=str, help='Wizard user')
parser.add_argument('-project', dest='project', type=str, help='Wizard project')
parser.add_argument('-teamDns', dest='team_dns', type=str, help='Wizard team connection DNS')
parser.add_argument('-pyfile', dest='pyfile', type=str, help='The python file to execute')
args = parser.parse_args()

if not args.psql_dns:
	logger.error("Please provide a PostgreSQL DNS")
else:
	logger.info(f"PostgreSQL DNS : {args.psql_dns}")

if not args.site:
	logger.error("Please provide a site")
else:
	logger.info(f"Site : {args.site}")

if not args.user:
	logger.error("Please provide a user")
else:
	logger.info(f"User : {args.user}")

if not args.project:
	logger.error("Please provide a project")
else:
	logger.info(f"Project : {args.project}")

if not args.team_dns:
	logger.error("No team DNS defined")
else:
	logger.info(f"Team DNS : {args.team_dns}")

if not args.pyfile:
	logger.error("Please provide a python file to execute")
else:
	logger.info(f"Pyfile : {args.pyfile}")

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

if args.team_dns:
	environment.set_team_dns(args.team_dns)

try:
    exec(open(args.pyfile).read())
except:
    logger.error(str(traceback.format_exc()))
finally:
    db_server.stop()
    softwares_server.stop()
    communicate_server.stop()