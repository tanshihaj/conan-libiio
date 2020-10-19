cmake_minimum_required(VERSION 3.0)
project(LibiioTest)

add_executable(example example.c)

find_package(libiio)
target_link_libraries(example libiio::libiio)
set_target_properties(example PROPERTIES RUNTIME_OUTPUT_DIRECTORY_RELEASE "bin")