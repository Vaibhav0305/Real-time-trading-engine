#ifndef LOGGER_H
#define LOGGER_H

#include <string>
#include <fstream>
#include <iostream>
#include <chrono>
#include <iomanip>

class Logger {
public:
    Logger(const std::string& filename = "logs.txt");
    ~Logger();

    void log(const std::string& message);
    void consoleLog(const std::string& message);

private:
    std::ofstream logFile;
    std::string getTimestamp();
};

#endif // LOGGER_H


