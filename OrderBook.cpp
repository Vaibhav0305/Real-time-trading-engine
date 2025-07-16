#include "OrderBook.h"
#include <iostream>
#include <algorithm>

OrderBook::OrderBook(const std::string& sym, Logger& log, EmailNotifier& notifier)
    : symbol(sym), logger(log), emailNotifier(notifier) {}

std::vector<Trade> OrderBook::addOrder(Order newOrder) {
    try {
        logger.consoleLog("Attempting to add order: " + newOrder.toString());
        std::vector<Trade> trades;

        if (allOrders.count(newOrder.getOrderId())) {
            logger.consoleLog("Error: Order with ID " + newOrder.getOrderId() + " already exists.");
            std::ofstream errLog("error.log", std::ios::app); errLog << "Duplicate order ID: " << newOrder.getOrderId() << "\n";
            return trades;
        }

        allOrders.emplace(newOrder.getOrderId(), newOrder);

        if (newOrder.getType() == BUY) {
            buyOrders.push(newOrder);
        } else {
            sellOrders.push(newOrder);
        }

        trades = matchOrders();
        return trades;
    } catch (const std::exception& ex) {
        logger.consoleLog(std::string("Exception in addOrder: ") + ex.what());
        std::ofstream errLog("error.log", std::ios::app); errLog << "Exception in addOrder: " << ex.what() << "\n";
        return {};
    }
}

std::vector<Trade> OrderBook::modifyOrder(const std::string& orderId, double newPrice, int newQuantity) {
    try {
        logger.consoleLog("Attempting to modify order ID: " + orderId);
        std::vector<Trade> trades;

        if (allOrders.find(orderId) == allOrders.end()) {
            logger.consoleLog("Error: Order ID " + orderId + " not found for modification.");
            std::ofstream errLog("error.log", std::ios::app); errLog << "Order ID not found for modification: " << orderId << "\n";
            return trades;
        }

        Order oldOrder = allOrders.at(orderId);
        // Remove old order from queues and map
        removeOrderFromQueues(orderId, oldOrder.getType());
        allOrders.erase(orderId);

        // Create new order with updated details, keeping original timestamp and ID
        Order modifiedOrder(orderId, oldOrder.getSymbol(), oldOrder.getType(), newPrice, newQuantity);
        modifiedOrder.timestamp = oldOrder.getTimestamp(); // Preserve original timestamp

        allOrders.emplace(modifiedOrder.getOrderId(), modifiedOrder);

        if (modifiedOrder.getType() == BUY) {
            buyOrders.push(modifiedOrder);
        } else {
            sellOrders.push(modifiedOrder);
        }

        logger.consoleLog("Order " + orderId + " modified to: " + modifiedOrder.toString());
        trades = matchOrders();
        return trades;
    } catch (const std::exception& ex) {
        logger.consoleLog(std::string("Exception in modifyOrder: ") + ex.what());
        std::ofstream errLog("error.log", std::ios::app); errLog << "Exception in modifyOrder: " << ex.what() << "\n";
        return {};
    }
}

bool OrderBook::cancelOrder(const std::string& orderId) {
    try {
        logger.consoleLog("Attempting to cancel order ID: " + orderId);

        if (allOrders.find(orderId) == allOrders.end()) {
            logger.consoleLog("Error: Order ID " + orderId + " not found for cancellation.");
            std::ofstream errLog("error.log", std::ios::app); errLog << "Order ID not found for cancellation: " << orderId << "\n";
            return false;
        }

        Order orderToCancel = allOrders.at(orderId);
        removeOrderFromQueues(orderId, orderToCancel.getType());
        allOrders.erase(orderId);
        logger.consoleLog("Order " + orderId + " cancelled.");
        return true;
    } catch (const std::exception& ex) {
        logger.consoleLog(std::string("Exception in cancelOrder: ") + ex.what());
        std::ofstream errLog("error.log", std::ios::app); errLog << "Exception in cancelOrder: " << ex.what() << "\n";
        return false;
    }
}

std::vector<Trade> OrderBook::matchOrders() {
    std::vector<Trade> trades;
    while (!buyOrders.empty() && !sellOrders.empty()) {
        Order buyOrder = buyOrders.top(); // Get a copy
        Order sellOrder = sellOrders.top(); // Get a copy

        if (buyOrder.getPrice() >= sellOrder.getPrice()) {
            // Match found
            int tradedQuantity = std::min(buyOrder.getQuantity(), sellOrder.getQuantity());
            double tradePrice = (buyOrder.getTimestamp() < sellOrder.getTimestamp()) ? buyOrder.getPrice() : sellOrder.getPrice();

            Trade newTrade(buyOrder.getOrderId(), sellOrder.getOrderId(), symbol, tradePrice, tradedQuantity);
            trades.push_back(newTrade);
            logger.consoleLog("Trade executed: " + newTrade.toString());
            emailNotifier.sendTradeNotification(newTrade.toString());

            // Pop old orders
            buyOrders.pop();
            sellOrders.pop();

            // Update quantities and push back if remaining
            if (buyOrder.getQuantity() - tradedQuantity > 0) {
                buyOrder.setQuantity(buyOrder.getQuantity() - tradedQuantity);
                buyOrders.push(buyOrder);
            }
            if (sellOrder.getQuantity() - tradedQuantity > 0) {
                sellOrder.setQuantity(sellOrder.getQuantity() - tradedQuantity);
                sellOrders.push(sellOrder);
            }

            // Update allOrders map
            allOrders.erase(buyOrder.getOrderId());
            allOrders.erase(sellOrder.getOrderId());
            if (buyOrder.getQuantity() > 0) {
                allOrders.emplace(buyOrder.getOrderId(), buyOrder);
            }
            if (sellOrder.getQuantity() > 0) {
                allOrders.emplace(sellOrder.getOrderId(), sellOrder);
            }

        } else {
            // No match, break loop
            break;
        }
    }
    return trades;
}

void OrderBook::printOrderBook() const {
    logger.consoleLog("\n--- Order Book for " + symbol + " ---");
    logger.consoleLog("Buy Orders (Price | Quantity | ID | Timestamp):");
    std::priority_queue<Order, std::vector<Order>, CompareBuyOrders> tempBuyOrders = buyOrders;
    while (!tempBuyOrders.empty()) {
        const Order& order = tempBuyOrders.top();
        logger.consoleLog("  " + std::to_string(order.getPrice()) + " | " + std::to_string(order.getQuantity()) + " | " + order.getOrderId() + " | " + std::to_string(order.getTimestamp()));
        tempBuyOrders.pop();
    }

    logger.consoleLog("Sell Orders (Price | Quantity | ID | Timestamp):");
    std::priority_queue<Order, std::vector<Order>, CompareSellOrders> tempSellOrders = sellOrders;
    while (!tempSellOrders.empty()) {
        const Order& order = tempSellOrders.top();
        logger.consoleLog("  " + std::to_string(order.getPrice()) + " | " + std::to_string(order.getQuantity()) + " | " + order.getOrderId() + " | " + std::to_string(order.getTimestamp()));
        tempSellOrders.pop();
    }
    logger.consoleLog("---------------------------");
}

void OrderBook::removeOrderFromQueues(const std::string& orderId, OrderType type) {
    // Rebuild the priority queue without the order to be removed
    if (type == BUY) {
        std::priority_queue<Order, std::vector<Order>, CompareBuyOrders> newBuyOrders;
        while (!buyOrders.empty()) {
            Order currentOrder = buyOrders.top();
            buyOrders.pop();
            if (currentOrder.getOrderId() != orderId) {
                newBuyOrders.push(currentOrder);
            }
        }
        buyOrders = newBuyOrders;
    } else { // SELL
        std::priority_queue<Order, std::vector<Order>, CompareSellOrders> newSellOrders;
        while (!sellOrders.empty()) {
            Order currentOrder = sellOrders.top();
            sellOrders.pop();
            if (currentOrder.getOrderId() != orderId) {
                newSellOrders.push(currentOrder);
            }
        }
        sellOrders = newSellOrders;
    }
}

std::vector<Order> OrderBook::getAllOrders() const {
    std::vector<Order> orders;
    for (const auto& pair : allOrders) {
        orders.push_back(pair.second);
    }
    return orders;
}


