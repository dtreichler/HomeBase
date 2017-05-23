import yaml
import os
import shutil


default_config_file = os.path.join(os.path.dirname(__file__), 'default_config.yaml')

home_dir = os.path.expanduser('~')
config_file = os.path.join(home_dir, 'homebase.yaml')

if not os.path.exists(config_file):
	shutil.copyfile(default_config_file, config_file)

with open(config_file, 'r') as fid:
	config = yaml.load(fid)