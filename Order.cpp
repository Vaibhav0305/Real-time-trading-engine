
#include "Order.h"
#include <sstream>

Order::Order(std::string id, std::string sym, OrderType t, double p, int q)
    : orderId(id), symbol(sym), type(t), price(p), quantity(q) {
    timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
}

std::string Order::toString() const {
    std::stringstream ss;
    ss << "Order ID: " << orderId << ", Symbol: " << symbol
       << ", Type: " << (type == BUY ? "BUY" : "SELL")
       << ", Price: " << price << ", Quantity: " << quantity
       << ", Timestamp: " << timestamp;
    return ss.str();
}


