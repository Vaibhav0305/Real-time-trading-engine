
#include "TradeLogger.h"
#include <iostream>
#include <sstream>

TradeLogger::TradeLogger(Logger& log, const std::string& ordersFile, const std::string& tradesFile, const std::string& cancelledFile)
    : logger(log), ordersFilePath(ordersFile), tradesFilePath(tradesFile), cancelledFilePath(cancelledFile) {
    
    // Ensure headers are written if files are new or empty
    std::ofstream ofs;
    ofs.open(ordersFilePath, std::ios::out | std::ios::app);
    if (ofs.tellp() == 0) { // Check if file is empty
        writeHeader(ofs, "orderId,symbol,type,price,quantity,timestamp\n");
    }
    ofs.close();

    ofs.open(tradesFilePath, std::ios::out | std::ios::app);
    if (ofs.tellp() == 0) {
        writeHeader(ofs, "tradeId,buyOrderId,sellOrderId,symbol,price,quantity,timestamp\n");
    }
    ofs.close();

    ofs.open(cancelledFilePath, std::ios::out | std::ios::app);
    if (ofs.tellp() == 0) {
        writeHeader(ofs, "orderId,symbol,type,price,quantity,timestamp\n");
    }
    ofs.close();
}

void TradeLogger::writeHeader(std::ofstream& file, const std::string& header) {
    file << header;
}

void TradeLogger::logTrade(const Trade& trade) {
    std::lock_guard<std::mutex> lock(mtx);
    std::ofstream ofs(tradesFilePath, std::ios::app);
    if (ofs.is_open()) {
        ofs << trade.getTradeId() << ","
            << trade.getBuyOrderId() << ","
            << trade.getSellOrderId() << ","
            << trade.getSymbol() << ","
            << trade.getPrice() << ","
            << trade.getQuantity() << ","
            << trade.getTimestamp() << "\n";
        ofs.close();
        logger.log("Logged trade: " + trade.toString());
    } else {
        logger.consoleLog("Error: Unable to open trades.csv for writing.");
    }
}

void TradeLogger::logOrder(const Order& order) {
    std::lock_guard<std::mutex> lock(mtx);
    std::ofstream ofs(ordersFilePath, std::ios::app);
    if (ofs.is_open()) {
        ofs << order.getOrderId() << ","
            << order.getSymbol() << ","
            << (order.getType() == BUY ? "BUY" : "SELL") << ","
            << order.getPrice() << ","
            << order.getQuantity() << ","
            << order.getTimestamp() << "\n";
        ofs.close();
        logger.log("Logged order: " + order.toString());
    } else {
        logger.consoleLog("Error: Unable to open orders.csv for writing.");
    }
}

void TradeLogger::logCancelledOrder(const Order& order) {
    std::lock_guard<std::mutex> lock(mtx);
    std::ofstream ofs(cancelledFilePath, std::ios::app);
    if (ofs.is_open()) {
        ofs << order.getOrderId() << ","
            << order.getSymbol() << ","
            << (order.getType() == BUY ? "BUY" : "SELL") << ","
            << order.getPrice() << ","
            << order.getQuantity() << ","
            << order.getTimestamp() << "\n";
        ofs.close();
        logger.log("Logged cancelled order: " + order.toString());
    } else {
        logger.consoleLog("Error: Unable to open cancelled.csv for writing.");
    }
}

void TradeLogger::saveAllOrders(const std::vector<Order>& orders) {
    std::lock_guard<std::mutex> lock(mtx);
    std::ofstream ofs(ordersFilePath, std::ios::out | std::ios::trunc); // Overwrite file
    if (ofs.is_open()) {
        writeHeader(ofs, "orderId,symbol,type,price,quantity,timestamp\n");
        for (const auto& order : orders) {
            ofs << order.getOrderId() << ","
                << order.getSymbol() << ","
                << (order.getType() == BUY ? "BUY" : "SELL") << ","
                << order.getPrice() << ","
                << order.getQuantity() << ","
                << order.getTimestamp() << "\n";
        }
        ofs.close();
        logger.log("Saved all current orders to " + ordersFilePath);
    } else {
        logger.consoleLog("Error: Unable to open orders.csv for saving all orders.");
    }
}


