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
    GIT_TAG "v2.5.0"
    USE_CACHING TRUE
    )

set(UNITY_INC_DIR "${SOURCE_DIR}/src")
CPM_ExportAdditionalIncludeDir("${UNITY_INC_DIR}")
file(GLOB SOURCES 
    "${SOURCE_DIR}/src/*.c"
    )

add_library(${CPM_LIB_TARGET_NAME} ${SOURCES})
target_link_libraries(${CPM_LIB_TARGET_NAME} ${CPM_LIBRARIES})

#------------------------------------------------------------------------------
# Dependencies
#------------------------------------------------------------------------------

if(EXISTS "${TEST_TESTS_SOURCE_DIR}/dependencies.cmake")
    message(STATUS "dependencies.cmake found: including dependencies...")
    include("${TEST_TESTS_SOURCE_DIR}/dependencies.cmake")
endif()

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

    # Add target for running a sigle test manually, e.g. 'make test-something'
    add_custom_target("test-${main_name}"
        COMMAND echo "Running 'test-${main_name}':" && ${main_path}.bak VERBATIM
        DEPENDS ${main_path}.bak
    )

    # Add target for running as part of all tests ('make tests')
    add_custom_command(TARGET ${main_file}
    POST_BUILD
    COMMAND cp ${main_path} ${main_path}.bak VERBATIM
    COMMAND ${main_path} > "${main_path}.txt" || echo "Test '${main_name}': FAILED" VERBATIM
    COMMAND echo "DONE '${main_path}'" VERBATIM
    )
    list(APPEND ALL_TESTS ${main_path})

endforeach()

set(result_cmd "${CMAKE_CURRENT_SOURCE_DIR}/result.py")
set(text_files_folder "${CMAKE_CURRENT_BINARY_DIR}")

add_custom_target(tests
    DEPENDS ${ALL_TESTS}
    
    COMMAND ${result_cmd} "${text_files_folder}" "\${TEST}"
)

