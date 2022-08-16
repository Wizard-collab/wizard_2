import os
import importlib.util
import sys


modules = os.listdir('modules_test')
print(modules)

for module in modules:
	if module.endswith('.py'):
		MODULE_NAME = 'modules.'+module.split('.py')[0]
		MODULE_PATH = "modules_test/{0}".format(module)
		spec = importlib.util.spec_from_file_location(MODULE_NAME, MODULE_PATH)
		module = importlib.util.module_from_spec(spec)
		sys.modules[spec.name] = module 
		spec.loader.exec_module(module)

sys.modules['modules.b'].caca()
print(sys.modules)