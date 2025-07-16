#ifndef ORDER_H
#define ORDER_H

#include <string>
#include <chrono>

enum OrderType { BUY, SELL };

class Order {
public:
    std::string orderId;
    std::string symbol;
    OrderType type;
    double price;
    int quantity;
    long long timestamp;

    Order(std::string orderId, std::string symbol, OrderType type, double price, int quantity);

    // Getters
    std::string getOrderId() const { return orderId; }
    std::string getSymbol() const { return symbol; }
    OrderType getType() const { return type; }
    double getPrice() const { return price; }
    int getQuantity() const { return quantity; }
    long long getTimestamp() const { return timestamp; }

    void setQuantity(int qty) { quantity = qty; }

    std::string toString() const;
};

#endif // ORDER_H


