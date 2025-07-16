#include <sstream>
#include "Logger.h"

Logger::Logger(const std::string& filename) {
    logFile.open(filename, std::ios_base::app);
    if (!logFile.is_open()) {
        std::cerr << "Error: Could not open log file " << filename << std::endl;
    }
}

Logger::~Logger() {
    if (logFile.is_open()) {
        logFile.close();
    }
}

void Logger::log(const std::string& message) {
    if (logFile.is_open()) {
        logFile << getTimestamp() << " - " << message << std::endl;
    }
}

void Logger::consoleLog(const std::string& message) {
    std::cout << getTimestamp() << " - " << message << std::endl;
}

std::string Logger::getTimestamp() {
    auto now = std::chrono::system_clock::now();
    auto in_time_t = std::chrono::system_clock::to_time_t(now);
    std::stringstream ss;
    ss << std::put_time(std::localtime(&in_time_t), "%Y-%m-%d %H:%M:%S");
    return ss.str();
}


