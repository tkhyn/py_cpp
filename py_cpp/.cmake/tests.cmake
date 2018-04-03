# tests configuration

# retrieves all test C++ files
file(GLOB_RECURSE TEST_FILES LIST_DIRECTORIES false ${TESTS_DIR}/test_*.cpp)

# Generate a test executable
add_executable("${PROJECT_NAME}_test"
        ${SRC_FILES}
        "tests.cpp"
        ${TEST_FILES}
)
