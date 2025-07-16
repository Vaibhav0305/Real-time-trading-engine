#ifndef ORDER_BOOK_H
#define ORDER_BOOK_H

#include "Order.h"
#include "Trade.h"
#include "Logger.h"
#include "EmailNotifier.h"
#include <queue>
#include <map>
#include <string>
#include <vector>
#include <memory>

// Custom comparator for BUY orders (max-heap: highest price, then oldest timestamp)
struct CompareBuyOrders {
    bool operator()(const Order& a, const Order& b) {
        if (a.getPrice() != b.getPrice()) {
            return a.getPrice() < b.getPrice(); // Max-heap for price
        }
        return a.getTimestamp() > b.getTimestamp(); // Min-heap for timestamp (oldest first)
    }
};

// Custom comparator for SELL orders (min-heap: lowest price, then oldest timestamp)
struct CompareSellOrders {
    bool operator()(const Order& a, const Order& b) {
        if (a.getPrice() != b.getPrice()) {
            return a.getPrice() > b.getPrice(); // Min-heap for price
        }
        return a.getTimestamp() > b.getTimestamp(); // Min-heap for timestamp (oldest first)
    }
};

class OrderBook {
public:
    OrderBook(const std::string& symbol, Logger& logger, EmailNotifier& notifier);

    std::vector<Trade> addOrder(Order order);
    std::vector<Trade> modifyOrder(const std::string& orderId, double newPrice, int newQuantity);
    bool cancelOrder(const std::string& orderId);
    void printOrderBook() const;

    // For persistence
    std::vector<Order> getAllOrders() const;

private:
    std::string symbol;
    Logger& logger;
    EmailNotifier& emailNotifier;

    std::priority_queue<Order, std::vector<Order>, CompareBuyOrders> buyOrders;
    std::priority_queue<Order, std::vector<Order>, CompareSellOrders> sellOrders;
    std::map<std::string, Order> allOrders; // For quick access by orderId

    std::vector<Trade> matchOrders();
    void removeOrderFromQueues(const std::string& orderId, OrderType type);
};

#endif // ORDER_BOOK_H


