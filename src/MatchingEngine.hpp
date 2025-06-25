#ifndef MATCHINGENGINE_HPP
#define MATCHINGENGINE_HPP

#include "OrderBook.hpp"
#include <vector>

class MatchingEngine {
public:
    OrderBook orderBook;

    void processOrder(const Order& order);
};

#endif
