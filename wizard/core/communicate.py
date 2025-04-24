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

# This module is used to handle third party softwares commands
# For example if you want to save a version within a
# Maya, the software plugin sends a socket signal
# here and waits for a return ( also socket signal )

"""
This module, `communicate.py`, is responsible for handling communication between third-party software and the Wizard application. 
It facilitates the exchange of commands and data using socket-based communication. The module includes a server class 
(`communicate_server`) that listens for incoming JSON signals, processes them, and sends appropriate responses back to the client.

Key Features:
- A threaded server (`communicate_server`) that listens for incoming connections and processes commands.
- Functions to handle various operations such as adding versions, retrieving files, requesting exports, managing references, 
    and more.
- Integration with other Wizard modules like `assets`, `project`, `video`, and `gui_server` to perform specific tasks.
- Support for a wide range of commands, including retrieving project paths, managing work environments, and handling video exports.

The module ensures seamless communication between the Wizard application and external software, enabling efficient 
collaboration and automation of tasks.
"""

# Python modules
from threading import Thread
import traceback
import json
import logging

# Wizard gui modules
from wizard.gui import gui_server

# Wizard modules
from wizard.core import environment
from wizard.core import socket_utils
from wizard.core import assets
from wizard.core import user
from wizard.core import project
from wizard.core import video
from wizard.vars import user_vars
from wizard.vars import ressources

logger = logging.getLogger(__name__)


class communicate_server(Thread):
    """
    A server class that handles communication between a client and the server 
    using sockets. This class runs in a separate thread and listens for incoming 
    connections to process various commands sent as JSON signals.
    Attributes:
        port (int): The port number on which the server listens.
        server (socket.socket): The server socket instance.
        server_address (str): The address of the server.
        running (bool): A flag indicating whether the server is running.
    Methods:
        __init__():
            Initializes the server, sets up the socket, and binds it to a port.
        run():
            Starts the server loop to accept incoming connections and process 
            signals until the server is stopped.
        stop():
            Stops the server by closing the socket and setting the running flag 
            to False.
        analyse_signal(signal_as_str, conn):
            Analyzes the incoming JSON signal, executes the corresponding 
            function, and sends the result back to the client.
    """

    def __init__(self):
        """
        Initializes the communicate_server instance.

        This constructor sets up a communication server by performing the following:
        - Calls the parent class initializer.
        - Retrieves an available port on 'localhost' using `socket_utils.get_port`.
        - Sets the retrieved port in the environment using `environment.set_communicate_server_port`.
        - Creates a server and its address using `socket_utils.get_server` with the specified host and port.
        - Initializes the `running` attribute to True, indicating the server is active.

        Attributes:
            port (int): The port number assigned to the server.
            server (object): The server instance created for communication.
            server_address (tuple): The address of the server (host, port).
            running (bool): A flag indicating whether the server is running.
        """
        super(communicate_server, self).__init__()
        self.port = socket_utils.get_port('localhost')
        environment.set_communicate_server_port(self.port)
        self.server, self.server_address = socket_utils.get_server(
            ('localhost', self.port))
        self.running = True

    def run(self):
        """
        Continuously listens for incoming connections and processes signals.

        This method runs in a loop while the `self.running` flag is set to True.
        It accepts incoming connections from the server socket, verifies the
        address of the connection, and processes the received signal if valid.

        Exceptions:
            - OSError: Silently ignored to allow the loop to continue running.
            - Any other exception: Logged with a traceback for debugging purposes.

        Workflow:
            1. Accepts a connection from the server socket.
            2. Verifies if the connection's address matches the expected server address.
            3. Receives the signal as a string from the connection.
            4. If a signal is received, it is analyzed using the `analyse_signal` method.
        """
        while self.running:
            try:
                conn, addr = self.server.accept()
                if addr[0] == self.server_address:
                    signal_as_str = socket_utils.recvall(conn)
                    if signal_as_str:
                        self.analyse_signal(signal_as_str.decode('utf8'), conn)
            except OSError:
                pass
            except:
                logger.error(str(traceback.format_exc()))
                continue

    def stop(self):
        """
        Stops the server by closing the connection and setting the running flag to False.

        This method ensures that the server is properly shut down by closing the server
        socket and updating the running state to indicate that the server is no longer active.
        """
        self.server.close()
        self.running = False

    def analyse_signal(self, signal_as_str, conn):
        """
        Analyse and process a signal received as a JSON string, and send the result back through the connection.
        Args:
            signal_as_str (str): The incoming signal as a JSON string. It must be decoded from UTF-8 and contain
                                 a dictionary with a 'function' key specifying the operation to perform.
            conn: The connection object used to send the response back to the caller.
        Raises:
            json.JSONDecodeError: If the signal_as_str is not a valid JSON string.
            KeyError: If the required keys are missing in the signal dictionary.
        Supported Functions:
            - 'add_version': Add a version with the specified work environment ID and comment.
            - 'get_file': Retrieve a file using the specified version ID.
            - 'request_export': Request an export with the specified work environment ID and export name.
            - 'get_export_format': Retrieve the export format for the specified work environment ID.
            - 'request_render': Request a render with the specified version ID, work environment ID, export name, and comment.
            - 'add_export_version': Add an export version with the specified parameters.
            - 'get_frame_range': Retrieve the frame range for the specified work environment ID.
            - 'get_image_format': Retrieve the image format.
            - 'get_frame_rate': Retrieve the frame rate.
            - 'get_user_folder': Retrieve the user folder path.
            - 'get_references': Retrieve references for the specified work environment ID.
            - 'modify_reference_LOD': Modify the Level of Detail (LOD) for references in the specified work environment ID.
            - 'create_or_get_camera_work_env': Create or retrieve a camera work environment for the specified work environment ID.
            - 'create_or_get_rendering_work_env': Create or retrieve a rendering work environment for the specified work environment ID.
            - 'get_hooks_folder': Retrieve the hooks folder path.
            - 'get_plugins_folder': Retrieve the plugins folder path.
            - 'get_string_variant_from_work_env_id': Retrieve a string variant from the specified work environment ID.
            - 'get_local_path': Retrieve the local path.
            - 'get_project_path': Retrieve the project path.
            - 'request_video': Request a video for the specified work environment ID.
            - 'get_export_name_from_reference_namespace': Retrieve the export name from the reference namespace and work environment ID.
            - 'add_video': Add a video with the specified parameters.
            - 'screen_over_version': Perform a screen operation over the specified version ID.
            - 'get_stylesheet': Retrieve the stylesheet.
        Note:
            The function sends the result of the operation back to the caller using the provided connection object.
        """
        # The signal_as_str is already decoded ( from utf8 )
        # The incoming signal needs to be a json string
        returned = None
        signal_dic = json.loads(signal_as_str)

        if signal_dic['function'] == 'add_version':
            returned = add_version(signal_dic['work_env_id'],
                                   signal_dic['comment'])
        elif signal_dic['function'] == 'get_file':
            returned = get_file(signal_dic['version_id'])
        elif signal_dic['function'] == 'request_export':
            returned = request_export(signal_dic['work_env_id'],
                                      signal_dic['export_name'])
        elif signal_dic['function'] == 'get_export_format':
            returned = get_export_format(signal_dic['work_env_id'])
        elif signal_dic['function'] == 'request_render':
            returned = request_render(signal_dic['version_id'],
                                      signal_dic['work_env_id'],
                                      signal_dic['export_name'],
                                      signal_dic['comment'])
        elif signal_dic['function'] == 'add_export_version':
            returned = add_export_version(signal_dic['export_name'],
                                          signal_dic['files'],
                                          signal_dic['work_env_id'],
                                          signal_dic['version_id'],
                                          signal_dic['comment'])
        elif signal_dic['function'] == 'get_frame_range':
            returned = get_frame_range(signal_dic['work_env_id'])
        elif signal_dic['function'] == 'get_image_format':
            returned = get_image_format()
        elif signal_dic['function'] == 'get_frame_rate':
            returned = get_frame_rate()
        elif signal_dic['function'] == 'get_user_folder':
            returned = get_user_folder()
        elif signal_dic['function'] == 'get_references':
            returned = get_references(signal_dic['work_env_id'])
        elif signal_dic['function'] == 'modify_reference_LOD':
            returned = modify_reference_LOD(signal_dic['work_env_id'],
                                            signal_dic['LOD'],
                                            signal_dic['namespaces_list'])
        elif signal_dic['function'] == 'create_or_get_camera_work_env':
            returned = create_or_get_camera_work_env(signal_dic['work_env_id'])
        elif signal_dic['function'] == 'create_or_get_rendering_work_env':
            returned = create_or_get_rendering_work_env(
                signal_dic['work_env_id'])
        elif signal_dic['function'] == 'get_hooks_folder':
            returned = project.get_hooks_folder()
        elif signal_dic['function'] == 'get_plugins_folder':
            returned = project.get_plugins_folder()
        elif signal_dic['function'] == 'get_string_variant_from_work_env_id':
            returned = get_string_variant_from_work_env_id(
                signal_dic['work_env_id'])
        elif signal_dic['function'] == 'get_local_path':
            returned = get_local_path()
        elif signal_dic['function'] == 'get_project_path':
            returned = get_project_path()
        elif signal_dic['function'] == 'request_video':
            returned = request_video(signal_dic['work_env_id'])
        elif signal_dic['function'] == 'get_export_name_from_reference_namespace':
            returned = get_export_name_from_reference_namespace(
                signal_dic['reference_namespace'], signal_dic['work_env_id'])
        elif signal_dic['function'] == 'add_video':
            returned = add_video(signal_dic['work_env_id'],
                                 signal_dic['temp_dir'],
                                 signal_dic['frange'],
                                 signal_dic['version_id'],
                                 signal_dic['focal_lengths_dic'],
                                 signal_dic['comment'])
        elif signal_dic['function'] == 'screen_over_version':
            returned = screen_over_version(signal_dic['version_id'])
        elif signal_dic['function'] == 'get_stylesheet':
            returned = get_stylesheet()

        socket_utils.send_signal_with_conn(conn, returned)


def get_string_variant_from_work_env_id(work_env_id):
    """
    Retrieve the string representation of a variant associated with a given work environment ID.

    Args:
        work_env_id (int): The ID of the work environment.

    Returns:
        str: The string representation of the variant associated with the work environment.
    """
    work_env_row = project.get_work_env_data(work_env_id)
    string_variant = assets.instance_to_string(
        ('variant', work_env_row['variant_id']))
    return string_variant


def get_file(version_id):
    """
    Retrieves the file path associated with a specific version ID.

    Args:
        version_id (str): The unique identifier for the version.

    Returns:
        str: The file path corresponding to the given version ID.
    """
    version_path = project.get_version_data(version_id, 'file_path')
    return version_path


def screen_over_version(version_id):
    """
    Checks and processes the screen overlay for a specific version.

    Args:
        version_id (int): The identifier of the version to process.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    success = assets.screen_over_version(version_id)
    return success


def add_version(work_env_id, comment):
    """
    Add a new version for a given work environment ID with an optional comment.

    This function uses the 'assets' module to create a new version and returns
    the file path and version ID of the newly created version. It also refreshes
    the UI and displays a save popup for the new version.

    Args:
        work_env_id (int): The ID of the work environment where the version is being added.
        comment (str): An optional comment to associate with the new version. If None or empty,
                       the comment will not be analyzed.

    Returns:
        tuple: A tuple containing:
            - version_path (str): The file path of the newly created version.
            - version_id (int): The ID of the newly created version.
            If the version creation fails, returns (None, None).
    """
    # Determine whether to analyze the comment based on its content
    analyse_comment = False if comment is None or comment == '' else True

    # Add a new version using the 'assets' module
    version_id = assets.add_version(
        work_env_id, comment=comment, analyse_comment=analyse_comment)
    if not version_id:
        return (None, None)

    # Retrieve the file path of the newly created version
    version_path = project.get_version_data(version_id, 'file_path')

    # Refresh the UI and display a save popup for the new version
    gui_server.refresh_ui()
    gui_server.save_popup(version_id)

    return (version_path, version_id)


def request_export(work_env_id, export_name):
    """
    Requests the export of a file based on the given work environment ID and export name.

    Args:
        work_env_id (str): The identifier of the work environment from which the export is requested.
        export_name (str): The name of the export to be retrieved.

    Returns:
        str: The file path of the requested export.
    """
    file_path = assets.request_export(work_env_id, export_name)
    return file_path


def get_export_format(work_env_id):
    """
    Retrieves the default file extension for a given work environment.

    Args:
        work_env_id (str): The identifier of the work environment.

    Returns:
        str: The default file extension associated with the specified work environment.
    """
    extension = assets.get_default_extension(work_env_id)
    return extension


def request_video(work_env_id):
    """
    Requests a video path for a specific work environment.

    This function retrieves the variant ID associated with the given work environment ID
    and uses it to request a video through the `video` module.

    Args:
        work_env_id (int): The ID of the work environment for which the video is requested.

    Returns:
        str: The file path of the requested video.
    """
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    return video.request_video(variant_id)


def add_video(work_env_id, temp_dir, frange, version_id, focal_lengths_dic=None, comment=''):
    """
    Adds a video to the project for a specific work environment.

    This function associates a video with a given work environment by using the 
    provided parameters such as the temporary directory, frame range, version ID, 
    and optional focal lengths dictionary and comment.

    Args:
        work_env_id (int): The ID of the work environment where the video is being added.
        temp_dir (str): The temporary directory containing the video files.
        frange (tuple): The frame range of the video (start_frame, end_frame).
        version_id (int): The ID of the version associated with the video.
        focal_lengths_dic (dict, optional): A dictionary containing focal length data. Defaults to None.
        comment (str, optional): An optional comment to associate with the video. Defaults to an empty string.

    Returns:
        str: The file path of the added video.

    Behavior:
        1. Retrieve the variant ID associated with the given work environment ID.
        2. Determine whether to analyze the comment based on its content.
        3. Convert the version ID into a string representation of the asset.
        4. Add the video using the `video.add_video` function with the provided parameters.
        5. Refresh the UI to reflect the changes.
        6. Return the file path of the added video.
    """
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    if comment is None or comment == '':
        analyse_comment = False
    else:
        analyse_comment = True
    string_asset = assets.instance_to_string(('work_version', version_id))
    video_path = video.add_video(variant_id, temp_dir, frange, string_asset,
                                 focal_lengths_dic, comment=comment, analyse_comment=analyse_comment)
    gui_server.refresh_ui()
    return video_path


def request_render(version_id, work_env_id, export_name, comment=''):
    """
    Requests the rendering of a specific version in a given work environment.

    This function interacts with the 'assets' module to generate a temporary 
    render directory based on the provided parameters. It also refreshes the 
    user interface via the 'gui_server' module.

    Args:
        version_id (int): The ID of the version to be rendered.
        work_env_id (int): The ID of the work environment where the rendering will occur.
        export_name (str): The name of the export file to be generated.
        comment (str, optional): Additional comments or notes for the rendering request. 
                                 Defaults to an empty string.

    Returns:
        str: The path to the temporary render directory.
    """
    render_directory = assets.request_render(
        version_id, work_env_id, export_name, comment=comment)
    gui_server.refresh_ui()
    return render_directory


def add_export_version(export_name, files, work_env_id, version_id, comment):
    """
    Adds a new export version for a given work environment and version.

    Args:
        export_name (str): The name of the export to be created.
        files (list): A list of file paths to be included in the export.
        work_env_id (int): The ID of the work environment associated with the export.
        version_id (int): The ID of the version to associate with the export.
        comment (str): A comment or description for the export. If None or empty, 
                       the comment will not be analyzed.

    Returns:
        str: The file path to the directory of the created export version.

    Notes:
        - The function retrieves the variant ID and stage ID associated with the 
          given work environment.
        - If a comment is provided, it is analyzed during the export creation.
        - The UI is refreshed after the export version is created.
    """
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    variant_row = project.get_variant_data(variant_id)
    if comment is None or comment == '':
        analyse_comment = False
    else:
        analyse_comment = True
    export_version_id = assets.add_export_version(
        export_name, files, variant_row['stage_id'], version_id, comment, analyse_comment=analyse_comment)
    export_dir = assets.get_export_version_path(export_version_id)
    gui_server.refresh_ui()
    return export_dir


def get_references(work_env_id):
    """
    Retrieve the scene reference files associated with a specific work environment.

    Args:
        work_env_id (str): The identifier of the work environment.

    Returns:
        list: A dictionary containing the reference files associated with the work environment.
    """
    return assets.get_references_files(work_env_id)


def get_frame_range(work_env_id):
    """
    Retrieve the frame range for a given work environment ID.

    This function fetches asset data associated with the provided work 
    environment ID and extracts the frame range information, including 
    preroll, inframe, outframe, and postroll values.

    Args:
        work_env_id (str): The identifier of the work environment.

    Returns:
        list[int] or None: A list containing the frame range values 
        [preroll, inframe, outframe, postroll] if the asset data is found, 
        otherwise None.
    """
    asset_row = assets.get_asset_data_from_work_env_id(work_env_id)
    if not asset_row:
        return
    return [asset_row['preroll'],
            asset_row['inframe'],
            asset_row['outframe'],
            asset_row['postroll']]


def modify_reference_LOD(work_env_id, LOD, namespaces_list):
    """
    Modifies the Level of Detail (LOD) for specific references in a given work environment 
    and updates the team user interface.

    Args:
        work_env_id (str): The identifier of the work environment where the references are located.
        LOD (str): The desired Level of Detail to set for the references.
        namespaces_list (list of str): A list of namespaces corresponding to the references to be modified.

    Returns:
        None
    """
    assets.modify_reference_LOD(work_env_id, LOD, namespaces_list)
    gui_server.refresh_team_ui()
    return


def get_image_format():
    """
    Retrieve the image format used in the project.

    This function fetches the image format setting from the project configuration.

    Returns:
        str: The image format used in the project.
    """
    return project.get_image_format()


def get_frame_rate():
    """
    Retrieve the frame rate of the project.

    This function fetches the frame rate setting from the project configuration.

    Returns:
        int: The frame rate of the project.
    """
    return project.get_frame_rate()


def get_user_folder():
    """
    Retrieve the path to the user's folder.

    This function returns the user-specific folder path stored in the 
    `user_vars` module.

    Returns:
        str: The path to the user's folder.
    """
    return user_vars._user_path_


def create_or_get_camera_work_env(work_env_id):
    """
    Create or retrieve a camera work environment for a given work environment ID.

    This function interacts with the `assets` module to either create a new 
    camera work environment or retrieve an existing one associated with the 
    specified work environment ID.

    Args:
        work_env_id (int): The ID of the work environment.

    Returns:
        dict: A dictionary containing details of the camera work environment.
    """
    return assets.create_or_get_camera_work_env(work_env_id)


def create_or_get_rendering_work_env(work_env_id):
    """
    Create or retrieve a rendering work environment for a given work environment ID.

    This function interacts with the `assets` module to either create a new 
    rendering work environment or retrieve an existing one associated with the 
    specified work environment ID.

    Args:
        work_env_id (int): The ID of the work environment.

    Returns:
        dict: A dictionary containing details of the rendering work environment.
    """
    return assets.create_or_get_rendering_work_env(work_env_id)


def get_local_path():
    """
    Retrieve the local path for the current user.

    This function fetches the local path associated with the current user 
    by interacting with the `user` module.

    Returns:
        str: The local path of the current user.
    """
    return user.user().get_local_path()


def get_project_path():
    """
    Retrieves the project path from the environment configuration.

    Returns:
        str: The absolute path to the project directory as defined in the environment.
    """
    return environment.get_project_path()


def get_export_name_from_reference_namespace(reference_namespace, work_env_id):
    """
    Retrieve the export name associated with a given reference namespace and work environment ID.

    Args:
        reference_namespace (str): The namespace of the reference to look up.
        work_env_id (int): The ID of the work environment where the reference resides.

    Returns:
        str: The name of the export associated with the reference namespace.
    """
    reference_row = project.get_reference_by_namespace(
        work_env_id, reference_namespace)
    export_name = project.get_export_data(reference_row['export_id'], 'name')
    return export_name


def get_stylesheet():
    """
    Retrieves the current stylesheet used by the application.

    Returns:
        str: The stylesheet as a string, typically defined in the `ressources._stylesheet_` variable.
    """
    return ressources._stylesheet_
