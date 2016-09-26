cmake_minimum_required(VERSION 3.5.0 FATAL_ERROR)


set(CPM_MODULE_NAME cpm_unity)

#-----------------------------------------------------------------------
# Required CPM Setup - no need to modify - See: https://github.com/iauns/cpm
#-----------------------------------------------------------------------
set(CPM_LIB_TARGET_NAME ${CPM_MODULE_NAME})

if ((DEFINED CPM_DIR) AND (DEFINED CPM_UNIQUE_ID) AND (DEFINED CPM_TARGET_NAME))
    set(CPM_LIB_TARGET_NAME ${CPM_TARGET_NAME})
    set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CPM_DIR})
    include(CPM)
else()
    set (CPM_DIR "${CMAKE_CURRENT_BINARY_DIR}/cpm-packages" CACHE TYPE STRING)
    find_package(Git)
    if(NOT GIT_FOUND)
        message(FATAL_ERROR "CPM requires Git.")
    endif()
    if (NOT EXISTS ${CPM_DIR}/CPM.cmake)
        message(STATUS "Cloning repo (https://github.com/iauns/cpm)")
        execute_process(
            COMMAND "${GIT_EXECUTABLE}" clone https://github.com/iauns/cpm ${CPM_DIR}
            RESULT_VARIABLE error_code
            OUTPUT_QUIET ERROR_QUIET)
        if(error_code)
            message(FATAL_ERROR "CPM failed to get the hash for HEAD")
        endif()
    endif()
    include(${CPM_DIR}/CPM.cmake)
endif()

#-----------------------------------------------------------------------
# Project sources / settings
#-----------------------------------------------------------------------

add_definitions(-DTEST)

# this is required because this is an 'external' module
CPM_ForceOnlyOneModuleVersion()

set(SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/external/Unity")
CPM_EnsureRepoIsCurrent(
    TARGET_DIR ${SOURCE_DIR}
    GIT_REPOSITORY "https://github.com/ThrowTheSwitch/Unity.git"
    GIT_TAG "7053ef7523d84748750f354b87173cbcdbb96d92"
    USE_CACHING TRUE
    )

set(UNITY_INC_DIR "${SOURCE_DIR}/src")
CPM_ExportAdditionalIncludeDir("${UNITY_INC_DIR}")
file(GLOB SOURCES 
    "${SOURCE_DIR}/src/*.c"
    )

add_library(${CPM_LIB_TARGET_NAME} ${SOURCES})
target_link_libraries(${CPM_LIB_TARGET_NAME} ${CPM_LIBRARIES})


CPM_InitModule(${CPM_MODULE_NAME})

#------------------------------------------------------------------------------
# Build tests
#------------------------------------------------------------------------------

# Depends on variables:
#
# TEST_NORMAL_SOURCE_DIR
# TEST_TESTS_SOURCE_DIR
# TEST_SHARED_SOURCES
# TEST_MAIN_SOURCES
# 

include_directories("${UNITY_INC_DIR}")
include_directories("${TEST_NORMAL_SOURCE_DIR}")
set(extra_src_prefix "${TEST_NORMAL_SOURCE_DIR}")

set(main_src_prefix "${TEST_TESTS_SOURCE_DIR}")
set(shared_src_prefix "${TEST_TESTS_SOURCE_DIR}")

# remove test main sources
if(TEST_SHARED_SOURCES)
    list(REMOVE_ITEM TEST_SHARED_SOURCES ${TEST_MAIN_SOURCES})
endif()
# check if any sources are remaining
if(TEST_SHARED_SOURCES)
    string(REGEX REPLACE "([^;]+)" "${shared_src_prefix}/\\1" TEST_SHARED_SOURCES_F "${TEST_SHARED_SOURCES}")

    message(STATUS "adding shared_test_lib library.. '${TEST_SHARED_SOURCES}'")
    add_library(shared_test_lib ${TEST_SHARED_SOURCES_F})
    set(SHARED_TEST_LIB_EXISTS TRUE)
    message(STATUS "adding shared_test_lib library DONE")
endif()

# build all tests
set(ALL_TESTS "")

foreach( main_source ${TEST_MAIN_SOURCES} )
    string( REPLACE ".c" "" main_file ${main_source})
    string( REPLACE ".test" "" main_name ${main_file})

    string(REGEX REPLACE "([^;]+)" "${main_src_prefix}/\\1" main_src_f "${main_source}")
    if(test_${main_name}_src)
        set(extra_src "${test_${main_name}_src}")
        message(STATUS "test '${main_file}': adding extra sources '${extra_src}'")
        string(REGEX REPLACE "([^;]+)" "${extra_src_prefix}/\\1" extra_src_f "${extra_src}")
        list(APPEND main_src_f ${extra_src_f})
    else(test_${main_name}_src)
        message(STATUS "test '${main_file}': no extra sources")
    endif(test_${main_name}_src)

    add_executable("${main_file}" "${main_src_f}")
    target_link_libraries(${main_file} ${CPM_LIBRARIES})
    target_link_libraries(${main_file} ${CPM_LIB_TARGET_NAME})

    if(SHARED_TEST_LIB_EXISTS)
        target_link_libraries( ${main_file} shared_test_lib )
    endif()

    set(main_path "${CMAKE_CURRENT_BINARY_DIR}/${main_file}")
    add_custom_command(TARGET ${main_file}
    POST_BUILD
    COMMAND ${main_path} > "\"${main_path}.txt\""
    )
    list(APPEND ALL_TESTS ${main_path})

endforeach()

set(text_files "${CMAKE_CURRENT_BINARY_DIR}/*.test.txt")
add_custom_target(tests
    DEPENDS ${ALL_TESTS}

    # color blue: header
    COMMAND tput setaf 4
    COMMAND echo "[Test] ================"
    COMMAND echo "[Test] = Test Results ="
    COMMAND echo "[Test] ================"
    COMMAND echo " "

    # color blue: header
    COMMAND tput setaf 4
    COMMAND echo `grep -qs IGNORE ${text_files} && echo "[Test] Ignores:" `
    # color orange: ignores
    COMMAND tput setaf 3
    COMMAND echo `grep -s IGNORE ${text_files}`

    # color blue: header
    COMMAND tput setaf 4
    COMMAND echo `grep -qs FAIL: ${text_files} && echo "[Test] Failures:" `
    # color red: errors
    COMMAND tput setaf 1
    COMMAND echo `grep -s FAIL: ${text_files}`

    # color blue: header
    COMMAND tput setaf 4
    COMMAND echo "[Test] Summary:"

    # color green as default
    # color orange if ignores found
    # color red if errors found
    COMMAND echo `tput setaf 2 `
    COMMAND echo `grep -qs IGNORE ${text_files} && tput setaf 3 `
    COMMAND echo `grep -qs FAIL: ${text_files} && tput setaf 1 `
    COMMAND tput cuu 3 && tput el
    COMMAND echo `grep -s Failures ${text_files} `
    COMMAND echo " "
    
    # color default
    COMMAND tput sgr0
)

