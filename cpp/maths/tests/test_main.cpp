/**
 * Tests for main.cpp functions
 *
 * Example tests only. C++ tests should really be only used to unit test
 * internal bits not accessible from python.
 */

#include <catch.hpp>

#include "main.h"


TEST_CASE("main functions") {

    REQUIRE(add(1000, 1) == 1001);
    REQUIRE(sub(1000, 1) == 999);

}
