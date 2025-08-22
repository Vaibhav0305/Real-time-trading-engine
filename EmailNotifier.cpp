#include "EmailNotifier.h"
#include <iostream>
#include <sstream>

EmailNotifier::EmailNotifier() {}

void EmailNotifier::sendOrderPlacedNotification(const Order& order) {
    std::stringstream ss;
    ss << "Order Placed Successfully\n"
       << "Order ID: " << order.getOrderId() << "\n"
       << "Symbol: " << order.getSymbol() << "\n"
       << "Type: " << (order.getType() == BUY ? "BUY" : "SELL") << "\n"
       << "Price: ₹" << order.getPrice() << "\n"
       << "Quantity: " << order.getQuantity();

    simulateSend("Order Placed", ss.str());
}

void EmailNotifier::sendTradeExecutedNotification(const Trade& trade) {
    std::stringstream ss;
    ss << "Trade Executed Successfully\n"
       << "Trade ID: " << trade.getTradeId() << "\n"
       << "Buy Order ID: " << trade.getBuyOrderId() << "\n"
       << "Sell Order ID: " << trade.getSellOrderId() << "\n"
       << "Symbol: " << trade.getSymbol() << "\n"
       << "Price: ₹" << trade.getPrice() << "\n"
       << "Quantity: " << trade.getQuantity();

    simulateSend("Trade Executed", ss.str());
}

void EmailNotifier::sendOrderCancelledNotification(const Order& order) {
    std::stringstream ss;
    ss << "Order Cancelled\n"
       << "Order ID: " << order.getOrderId() << "\n"
       << "Symbol: " << order.getSymbol() << "\n"
       << "Type: " << (order.getType() == BUY ? "BUY" : "SELL") << "\n"
       << "Price: ₹" << order.getPrice() << "\n"
       << "Quantity: " << order.getQuantity();

    simulateSend("Order Cancelled", ss.str());
}

void EmailNotifier::simulateSend(const std::string& subject, const std::string& message) {
    std::cout << "\n📧 [Email Notification] " << subject << "\n";
    std::cout << "-----------------------------------\n";
    std::cout << message << "\n";
    std::cout << "-----------------------------------\n";
}

