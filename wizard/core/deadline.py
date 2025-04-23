# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This file is part of Wizard

# MIT License

# Copyright (c) 2021 Leo brunel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Python modules
import subprocess
import json

# Wizard modules
from wizard.core import environment
from wizard.core import tools
from wizard.core import project


def submit_job(pycmd, name, priority=50):
    deadline_path = "C:/Program files/Thinkbox/Deadline10/bin/deadlinecommand.exe"
    wizard_cmd = "C:/Program files/wizard/wizard_cmd.exe"

    psql_dns = environment.get_psql_dns()
    repository_name = environment.get_repository()[11:]
    user_name = environment.get_user()
    project_name = environment.get_project_name()
    team_dns = json.dumps(environment.get_team_dns())
    pyfile = tools.shared_temp_file_from_pycmd(
        pycmd, project.get_temp_scripts_folder())

    command = f"{deadline_path} "
    command += "-SubmitCommandLineJob "
    command += f'-executable "{wizard_cmd}" '
    command += f'-name "{name}" '
    command += f'-arguments "-psqlDns <QUOTE>{psql_dns}<QUOTE> '
    command += f'-repository <QUOTE>{repository_name}<QUOTE> '
    command += f'-user <QUOTE>{user_name}<QUOTE> '
    command += f'-project <QUOTE>{project_name}<QUOTE> '
    if team_dns:
        command += f'-teamDns <QUOTE>{team_dns}<QUOTE> '
    command += f'-pyfile <QUOTE>{pyfile}<QUOTE>"'

    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    print(process.stdout)
