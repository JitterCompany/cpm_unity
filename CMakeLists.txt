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

CPM_InitModule(${CPM_MODULE_NAME})

#-----------------------------------------------------------------------
# Project sources / settings
#-----------------------------------------------------------------------

# this is required because this is an 'external' module
CPM_ForceOnlyOneModuleVersion()

set(SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/external/Unity")
CPM_EnsureRepoIsCurrent(
    TARGET_DIR ${SOURCE_DIR}
    GIT_REPOSITORY "https://github.com/ThrowTheSwitch/Unity.git"
    GIT_TAG "7053ef7523d84748750f354b87173cbcdbb96d92"
    USE_CACHING TRUE
    )

CPM_ExportAdditionalIncludeDir("${SOURCE_DIR}/src")
file(GLOB SOURCES 
    "${SOURCE_DIR}/src/*.c"
    )

add_library(${CPM_LIB_TARGET_NAME} ${SOURCES})
target_link_libraries(${CPM_LIB_TARGET_NAME} ${CPM_LIBRARIES})
