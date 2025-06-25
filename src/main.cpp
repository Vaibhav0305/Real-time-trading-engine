#include "MatchingEngine.hpp"
#include <iostream>

int main() {
    MatchingEngine engine;

    Order buy1(1, "XYZ", OrderType::BUY, 100, 50);
    Order sell1(2, "XYZ", OrderType::SELL, 95, 30);
    Order sell2(3, "XYZ", OrderType::SELL, 100, 40);

    engine.processOrder(sell1);
    engine.processOrder(sell2);
    engine.processOrder(buy1);

    return 0;
}
