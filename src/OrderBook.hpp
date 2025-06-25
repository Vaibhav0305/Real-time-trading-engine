#ifndef ORDERBOOK_HPP
#define ORDERBOOK_HPP

#include "Order.hpp"
#include <map>
#include <queue>
#include <functional>

class OrderBook {
public:
    std::map<double, std::queue<Order>, std::greater<double>> buyOrders;
    std::map<double, std::queue<Order>> sellOrders;

    void addOrder(const Order& order);
};

#endif
