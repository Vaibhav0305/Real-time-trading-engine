
#include "Trade.h"
#include <sstream>

Trade::Trade(std::string tId, std::string buyId, std::string sellId, std::string sym, double p, int q)
    : tradeId(tId), buyOrderId(buyId), sellOrderId(sellId), symbol(sym), price(p), quantity(q) {
    timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
}

std::string Trade::toString() const {
    std::stringstream ss;
    ss << "Trade ID: " << tradeId << ", Buy Order ID: " << buyOrderId << ", Sell Order ID: " << sellOrderId
       << ", Symbol: " << symbol << ", Price: " << price
       << ", Quantity: " << quantity << ", Timestamp: " << timestamp;
    return ss.str();
}


