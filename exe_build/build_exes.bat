windres exe_infos.rc -O coff -o exe_infos.o
g++ -o launch_noconsole.exe -mwindows launch.cpp exe_infos.o
g++ -o launch_console.exe launch_console.cpp exe_infos.o
del exe_infos.o