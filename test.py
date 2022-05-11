import sys
import subprocess

deadline = "C:\\Program Files\\Thinkbox\\Deadline10\\bin\\deadlinecommand.exe"

pywi = "C:\\Program Files\\wizard\\pywizard.exe"
file = "D:\\SCRIPT\\wizard_2\\benchmark.py"

command = f'"{deadline}" -SubmitCommandLineJob -executable "{pywi}" -arguments "<QUOTE>D:/SCRIPT/wizard_2/benchmark.py<QUOTE>" -name "PyWizard batch export"'
#command = f'"{deadline}" "job_info.job" "plugin_info.job"'

process = subprocess.Popen(command, stdout=subprocess.PIPE)
lines_iterator = iter(process.stdout.readline, b"")
for line in lines_iterator:
    print(line)
    sys.stdout.flush()