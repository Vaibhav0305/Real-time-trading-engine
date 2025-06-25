#include "MatchingEngine.hpp"
#include <iostream>

void MatchingEngine::processOrder(const Order& order) {
    if (order.type == OrderType::BUY) {
        // Try to match with lowest SELL orders
        auto& sellMap = orderBook.sellOrders;
        for (auto it = sellMap.begin(); it != sellMap.end();) {
            if (order.price >= it->first && order.quantity > 0) {
                while (!it->second.empty() && order.quantity > 0) {
                    Order sellOrder = it->second.front();
                    int tradedQty = std::min(order.quantity, sellOrder.quantity);

                    std::cout << "Trade Executed: BUY " << tradedQty 
                              << " @ ₹" << it->first << "\n";

                    order.quantity -= tradedQty;
                    sellOrder.quantity -= tradedQty;

                    if (sellOrder.quantity == 0) {
                        it->second.pop();
                    }

                    if (order.quantity == 0)
                        break;
                }

                if (it->second.empty()) {
                    it = sellMap.erase(it);
                } else {
                    ++it;
                }
            } else {
                break;
            }
        }

        if (order.quantity > 0) {
            orderBook.addOrder(order);
        }

    } else { // SELL order
        auto& buyMap = orderBook.buyOrders;
        for (auto it = buyMap.begin(); it != buyMap.end();) {
            if (order.price <= it->first && order.quantity > 0) {
                while (!it->second.empty() && order.quantity > 0) {
                    Order buyOrder = it->second.front();
                    int tradedQty = std::min(order.quantity, buyOrder.quantity);

                    std::cout << "Trade Executed: SELL " << tradedQty 
                              << " @ ₹" << it->first << "\n";

                    order.quantity -= tradedQty;
                    buyOrder.quantity -= tradedQty;

                    if (buyOrder.quantity == 0) {
                        it->second.pop();
                    }

                    if (order.quantity == 0)
                        break;
                }

                if (it->second.empty()) {
                    it = buyMap.erase(it);
                } else {
                    ++it;
                }
            } else {
                break;
            }
        }

        if (order.quantity > 0) {
            orderBook.addOrder(order);
        }
    }
}
