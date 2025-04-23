import os
import shutil
import yaml

import logging
logger = logging.getLogger(__name__)

SERVER_DOWNLOAD_PATH = "O:/html/download/"
SERVER_CGI_BIN_PATH = "O:/html/cgi-bin/"
COMPIL_PATH = 'compile/'


def deploy_to_server():
    if not os.path.isdir(SERVER_DOWNLOAD_PATH):
        print(f"{SERVER_DOWNLOAD_PATH} not found.")
        return
    if not os.path.isdir(COMPIL_PATH):
        print(f"{COMPIL_PATH} not found.")
        return

    with open("ressources/version.yaml", 'r') as f:
        build_dic = yaml.load(f, Loader=yaml.Loader)
    build_file = os.path.join(COMPIL_PATH, build_dic['setup_name'])
    if not os.path.isfile(build_file):
        print(f"{build_file} not found.")
        return

    dest_file = os.path.join(SERVER_DOWNLOAD_PATH,
                             os.path.basename(build_file))
    print(f"Copying {build_file} to {dest_file}")
    shutil.copyfile(build_file, dest_file)

    if not os.path.isfile(dest_file):
        print(f"{dest_file} not copied")
        return

    yaml_dest_file = os.path.join(SERVER_CGI_BIN_PATH, "version.yaml")
    print(f"Copying version.yaml to {yaml_dest_file}")
    shutil.copyfile("ressources/version.yaml", yaml_dest_file)

    if not os.path.isfile(yaml_dest_file):
        print(f"{yaml_dest_file} not copied")
        return


if __name__ == '__main__':
    deploy_to_server()
