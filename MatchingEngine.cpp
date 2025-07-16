
#include "MatchingEngine.h"
#include <iostream>

MatchingEngine::MatchingEngine(Logger& log, EmailNotifier& notifier)
    : logger(log), emailNotifier(notifier) {}

OrderBook* MatchingEngine::getOrderBook(const std::string& symbol) {
    if (orderBooks.find(symbol) == orderBooks.end()) {
        logger.consoleLog("Creating new order book for symbol: " + symbol);
        orderBooks[symbol] = std::make_unique<OrderBook>(symbol, logger, emailNotifier);
    }
    return orderBooks[symbol].get();
}

std::vector<Trade> MatchingEngine::placeOrder(const Order& order) {
    logger.consoleLog("Placing order: " + order.toString());
    OrderBook* ob = getOrderBook(order.getSymbol());
    return ob->addOrder(order);
}

std::vector<Trade> MatchingEngine::modifyOrder(const std::string& orderId, double newPrice, int newQuantity) {
    logger.consoleLog("Modifying order ID: " + orderId);
    // Find the order in any order book
    for (auto const& [symbol, orderBook] : orderBooks) {
        std::vector<Order> ordersInBook = orderBook->getAllOrders();
        for (const auto& order : ordersInBook) {
            if (order.getOrderId() == orderId) {
                return orderBook->modifyOrder(orderId, newPrice, newQuantity);
            }
        }
    }
    logger.consoleLog("Error: Order ID " + orderId + " not found for modification in any order book.");
    return {}; // Return empty vector if order not found
}

bool MatchingEngine::cancelOrder(const std::string& orderId) {
    logger.consoleLog("Cancelling order ID: " + orderId);
    // Find the order in any order book
    for (auto const& [symbol, orderBook] : orderBooks) {
        std::vector<Order> ordersInBook = orderBook->getAllOrders();
        for (const auto& order : ordersInBook) {
            if (order.getOrderId() == orderId) {
                return orderBook->cancelOrder(orderId);
            }
        }
    }
    logger.consoleLog("Error: Order ID " + orderId + " not found for cancellation in any order book.");
    return false; // Return false if order not found
}

void MatchingEngine::printOrderBook(const std::string& symbol) const {
    auto it = orderBooks.find(symbol);
    if (it != orderBooks.end()) {
        it->second->printOrderBook();
    } else {
        logger.consoleLog("Order book for symbol " + symbol + " does not exist.");
    }
}

std::vector<Order> MatchingEngine::getAllOrders() const {
    std::vector<Order> allCurrentOrders;
    for (auto const& [symbol, orderBook] : orderBooks) {
        std::vector<Order> ordersInBook = orderBook->getAllOrders();
        allCurrentOrders.insert(allCurrentOrders.end(), ordersInBook.begin(), ordersInBook.end());
    }
    return allCurrentOrders;
}


