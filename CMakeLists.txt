cmake_minimum_required(VERSION 3.10)

project(VittCott)

set(CMAKE_CXX_STANDARD 17)
# Source files
set(SOURCE_FILES
    Order.cpp
    Trade.cpp
    Logger.cpp
    OrderBook.cpp
    MatchingEngine.cpp
    TradeLogger.cpp
    CLI.cpp
    main.cpp
)

# Include directories
include_directories(.)

# Add the executable
add_executable(VittCott ${SOURCE_FILES})


