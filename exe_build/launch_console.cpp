#pragma GCC diagnostic ignored "-Wcast-function-type"

#include <windows.h>
#include <iostream>
#include <string>

int main(int argc, char *argv[])
{
    std::string filepath = argv[0];
    std::string directory = filepath.substr(0, filepath.find_last_of("\\/"));
    std::string filename = filepath.substr(filepath.find_last_of("\\/") + 1);

    // Remove the ".exe" extension to get the base name
    std::string baseName = filename.substr(0, filename.find_last_of('.'));

    // Construct the batch file name
    std::string batchFile = directory + "\\" + baseName + ".bat";

    // Construct the command to execute the batch file
    std::string command = batchFile;

    // Execute the batch file
    system(command.c_str());

    /*system("pause");*/
    return EXIT_SUCCESS;
}