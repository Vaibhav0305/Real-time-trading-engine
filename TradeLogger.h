#ifndef TRADE_LOGGER_H
#define TRADE_LOGGER_H

#include "Order.h"
#include "Trade.h"
#include "Logger.h"
#include <fstream>
#include <string>
#include <vector>
#include <mutex>

class TradeLogger {
public:
    TradeLogger(Logger& logger, const std::string& ordersFile = "orders.csv",
                const std::string& tradesFile = "trades.csv",
                const std::string& cancelledFile = "cancelled.csv");

    void logTrade(const Trade& trade);
    void logOrder(const Order& order);
    void logCancelledOrder(const Order& order);
    void saveAllOrders(const std::vector<Order>& orders);

private:
    Logger& logger;
    std::string ordersFilePath;
    std::string tradesFilePath;
    std::string cancelledFilePath;
    std::mutex mtx;

    void writeHeader(std::ofstream& file, const std::string& header);
};

#endif // TRADE_LOGGER_H


