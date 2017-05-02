PROJECT(SnappyTest)
cmake_minimum_required(VERSION 2.8.12)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

ADD_EXECUTABLE(testapp test.cpp)
TARGET_LINK_LIBRARIES(testapp ${CONAN_LIBS})
