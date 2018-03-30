# tests configuration

# Generate a test executable
add_executable("${PROJECT_NAME}_test"
        ${CPP_FILES}
        "tests.cpp"
        "${TEST_DIR}/test_main.cpp"
)
