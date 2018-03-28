# post-build steps

# copy built module to bin directory
add_custom_command(TARGET ${CMAKE_PROJECT_NAME}
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${CMAKE_PROJECT_NAME}> ../../.bin/${CMAKE_BUILD_TYPE}/cpp/$<TARGET_FILE_NAME:${CMAKE_PROJECT_NAME}>
)
