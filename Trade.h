#ifndef TRADE_H
#define TRADE_H

#include <string>
#include <chrono>

class Trade {
public:
    std::string tradeId;
    std::string buyOrderId;
    std::string sellOrderId;
    std::string symbol;
    double price;
    int quantity;
    long long timestamp;

    Trade(std::string tradeId, std::string buyId, std::string sellId, std::string sym, double p, int q);

    // Getters
    std::string getTradeId() const { return tradeId; }
    std::string getBuyOrderId() const { return buyOrderId; }
    std::string getSellOrderId() const { return sellOrderId; }
    std::string getSymbol() const { return symbol; }
    double getPrice() const { return price; }
    int getQuantity() const { return quantity; }
    long long getTimestamp() const { return timestamp; }

    std::string toString() const;
};

#endif // TRADE_H


