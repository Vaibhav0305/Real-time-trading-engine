#ifndef CLI_H
#define CLI_H

#include "MatchingEngine.h"
#include "TradeLogger.h"
#include "Logger.h"
#include <string>
#include <memory>

class CLI {
public:
    CLI(MatchingEngine& engine, TradeLogger& logger, Logger& consoleLogger);
    void displayMenu();
    void run();

private:
    MatchingEngine& matchingEngine;
    TradeLogger& tradeLogger;
    Logger& consoleLogger;

    void placeOrder();
    void modifyOrder();
    void cancelOrder();
    void viewOrderBook();
    void exportData();
    std::string generateUniqueOrderId();
};

#endif // CLI_H


