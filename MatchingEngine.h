#ifndef MATCHING_ENGINE_H
#define MATCHING_ENGINE_H

#include "OrderBook.h"
#include "Trade.h"
#include "Logger.h"
#include "EmailNotifier.h"
#include <map>
#include <string>
#include <vector>
#include <memory>

class MatchingEngine {
public:
    MatchingEngine(Logger& logger, EmailNotifier& notifier);

    std::vector<Trade> placeOrder(const Order& order);
    std::vector<Trade> modifyOrder(const std::string& orderId, double newPrice, int newQuantity);
    bool cancelOrder(const std::string& orderId);
    void printOrderBook(const std::string& symbol) const;
    
    // For persistence
    std::vector<Order> getAllOrders() const;

private:
    Logger& logger;
    EmailNotifier& emailNotifier;
    std::map<std::string, std::unique_ptr<OrderBook>> orderBooks;

    OrderBook* getOrderBook(const std::string& symbol);
};

#endif // MATCHING_ENGINE_H


