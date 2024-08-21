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

    // Create a STARTUPINFO structure
    STARTUPINFO siStartInfo;
    PROCESS_INFORMATION piProcInfo;
    ZeroMemory(&siStartInfo, sizeof(STARTUPINFO));
    ZeroMemory(&piProcInfo, sizeof(PROCESS_INFORMATION));
    siStartInfo.cb = sizeof(STARTUPINFO);
    siStartInfo.dwFlags |= STARTF_USESHOWWINDOW;
    siStartInfo.wShowWindow = SW_HIDE; // Hide the window

    // Create the process
    BOOL bSuccess = CreateProcess(
        NULL,
        const_cast<char*>(batchFile.c_str()),
        NULL,
        NULL,
        FALSE,
        CREATE_NO_WINDOW, // No console window
        NULL,
        NULL,
        &siStartInfo,
        &piProcInfo
    );

    if (!bSuccess) {
        std::cerr << "Error creating process: " << GetLastError() << std::endl;
        return EXIT_FAILURE;
    }

    // Wait for the process to complete
    WaitForSingleObject(piProcInfo.hProcess, INFINITE);

    // Close handles
    CloseHandle(piProcInfo.hProcess);
    CloseHandle(piProcInfo.hThread);

    /*system("pause");*/
    return EXIT_SUCCESS;
}
