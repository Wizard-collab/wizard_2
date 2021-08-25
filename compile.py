import subprocess
import os
import shutil
import yaml
import sys
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

class compile():
	def __init__(self):
		args = sys.argv
		args.pop(0)
		if len(args) >= 1:
			self.release_type = args.pop(0)
		else:
			self.release_type = None
		self.build_folder = None
		self.get_release_name()
		self.compile()

	def get_release_name(self):
		if self.release_type is not None:
			compil_dir = 'compile'
			if not os.path.isdir(compil_dir):
				os.mkdir(compil_dir)
			compil_data_file = os.path.join(compil_dir, 'compil.yaml')
			if not os.path.isfile(compil_data_file):
				compil_data_dic = dict()
				compil_data_dic['builds'] = 0
				# version name : MAJOR.MINOR.PATCH
				compil_data_dic['MAJOR'] = 2
				compil_data_dic['MINOR'] = 0
				compil_data_dic['PATCH'] = 0
				with open(compil_data_file, 'w') as f:
					yaml.dump(compil_data_dic, f)
			else:
				with open(compil_data_file, 'r') as f:
					compil_data_dic = yaml.load(f, Loader=yaml.Loader)
			build_no = compil_data_dic['builds'] + 1
			MAJOR = compil_data_dic['MAJOR']
			MINOR = compil_data_dic['MINOR']
			PATCH = compil_data_dic['PATCH']
			if self.release_type == 'MAJOR':
				MAJOR += 1
				MINOR = 0
				PATCH = 0
			elif self.release_type == 'MINOR':
				MINOR += 1
				PATCH = 0
			elif self.release_type == 'PATCH':
				PATCH += 1
			elif self.release_type == 'REBUILD':
				pass
			else:
				logger.error(f"{self.release_type} is not a valid release type")
				MAJOR = None
				MINOR = None
				PATCH = None
			if (MAJOR and MINOR and PATCH) is not None:
				release_name = f"{MAJOR}.{MINOR}.{PATCH}"
				self.build_folder = os.path.join(compil_dir, f"{release_name}_{str(build_no).zfill(6)}")
				compil_data_dic['MAJOR'] = MAJOR
				compil_data_dic['MINOR'] = MINOR
				compil_data_dic['PATCH'] = PATCH
				compil_data_dic['builds'] = build_no
				with open(compil_data_file, 'w') as f:
					yaml.dump(compil_data_dic, f)
				logger.info(f"Release name : {release_name}")
				logger.info(f"Build : {build_no}")
		else:
			logger.error(f"please provide a release type")

	def compile(self):
		if self.build_folder is not None:
			self.clean_pycache()
			if os.path.isdir('dist'):
				shutil.rmtree('dist')
			if os.path.isdir('build'):
				shutil.rmtree('build')
			command_line = "PyInstaller app.spec"
			p = subprocess.Popen(command_line)
			p.wait()
			folders_list = ['ressources']
			dist_folder = 'dist/wizard'
			for folder in folders_list:
				destination = os.path.join(dist_folder, folder)
				shutil.copytree(folder, destination)
			shutil.copytree(dist_folder, self.build_folder)
			if os.path.isdir('dist'):
				shutil.rmtree('dist')
			if os.path.isdir('build'):
				shutil.rmtree('build')
			self.clean_pycache()

	def clean_pycache(self):
		total_chars = 0
		total_files = 0
		for root, dirs, files in os.walk(os.path.abspath(""), topdown=False):
		    for directory in dirs:
		    	if directory == '__pycache__':
		    		dir_name = os.path.join(root, directory)
		    		logger.info(f"Deleting {dir_name}...")
		    		shutil.rmtree(dir_name)

if __name__ == '__main__':
	compile()