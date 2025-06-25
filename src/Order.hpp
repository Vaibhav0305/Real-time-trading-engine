#ifndef ORDER_HPP
#define ORDER_HPP

#include <string>
#include <chrono>

enum class OrderType { BUY, SELL };

struct Order {
    int orderId;
    std::string symbol; // e.g., "XYZ"
    OrderType type;
    double price;
    int quantity;
    std::chrono::high_resolution_clock::time_point timestamp;

    Order(int id, const std::string& sym, OrderType t, double p, int q)
        : orderId(id), symbol(sym), type(t), price(p), quantity(q),
          timestamp(std::chrono::high_resolution_clock::now()) {}
};

#endif // ORDER_HPP
