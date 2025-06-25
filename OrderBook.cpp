#include "OrderBook.hpp"

void OrderBook::addOrder(const Order& order) {
    if (order.type == OrderType::BUY) {
        buyOrders[order.price].push(order);
    } else {
        sellOrders[order.price].push(order);
    }
}
