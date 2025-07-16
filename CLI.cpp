
#include "CLI.h"
#include <iostream>
#include <limits>
#include <random>

CLI::CLI(MatchingEngine& engine, TradeLogger& tLogger, Logger& cLogger)
    : matchingEngine(engine), tradeLogger(tLogger), consoleLogger(cLogger) {}

void CLI::displayMenu() {
    consoleLogger.consoleLog("\n--- VittCott Trading Engine CLI ---");
    consoleLogger.consoleLog("1. Place Order (BUY/SELL)");
    consoleLogger.consoleLog("2. Modify Order");
    consoleLogger.consoleLog("3. Cancel Order");
    consoleLogger.consoleLog("4. View Order Book");
    consoleLogger.consoleLog("5. Export All Current Orders");
    consoleLogger.consoleLog("6. Exit");
    consoleLogger.consoleLog("-----------------------------------");
    std::cout << "Enter your choice: ";
}

void CLI::run() {
    int choice;
    do {
        displayMenu();
        std::cin >> choice;
        // Clear the input buffer
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

        switch (choice) {
            case 1:
                placeOrder();
                break;
            case 2:
                modifyOrder();
                break;
            case 3:
                cancelOrder();
                break;
            case 4:
                viewOrderBook();
                break;
            case 5:
                exportData();
                break;
            case 6:
                consoleLogger.consoleLog("Exiting VittCott. Saving all current orders...");
                tradeLogger.saveAllOrders(matchingEngine.getAllOrders());
                consoleLogger.consoleLog("Goodbye!");
                break;
            default:
                consoleLogger.consoleLog("Invalid choice. Please try again.");
                break;
        }
    } while (choice != 6);
}

void CLI::placeOrder() {
    std::string symbol, typeStr;
    double price;
    int quantity;

    consoleLogger.consoleLog("\n--- Place New Order ---");
    std::cout << "Enter Symbol (e.g., AAPL): ";
    std::getline(std::cin, symbol);

    std::cout << "Enter Type (BUY/SELL): ";
    std::getline(std::cin, typeStr);
    OrderType type;
    if (typeStr == "BUY" || typeStr == "buy") {
        type = BUY;
    } else if (typeStr == "SELL" || typeStr == "sell") {
        type = SELL;
    } else {
        consoleLogger.consoleLog("Invalid order type. Must be BUY or SELL.");
        return;
    }

    std::cout << "Enter Price: ";
    std::cin >> price;
    if (std::cin.fail() || price <= 0) {
        consoleLogger.consoleLog("Invalid price. Please enter a positive number.");
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        return;
    }

    std::cout << "Enter Quantity: ";
    std::cin >> quantity;
    if (std::cin.fail() || quantity <= 0) {
        consoleLogger.consoleLog("Invalid quantity. Please enter a positive integer.");
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        return;
    }
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // Clear buffer after numeric input

    std::string orderId = generateUniqueOrderId();
    Order newOrder(orderId, symbol, type, price, quantity);
    matchingEngine.placeOrder(newOrder);
    consoleLogger.consoleLog("Order placed successfully with ID: " + orderId);
}

void CLI::modifyOrder() {
    std::string orderId;
    double newPrice;
    int newQuantity;

    consoleLogger.consoleLog("\n--- Modify Existing Order ---");
    std::cout << "Enter Order ID to modify: ";
    std::getline(std::cin, orderId);

    std::cout << "Enter New Price: ";
    std::cin >> newPrice;
    if (std::cin.fail() || newPrice <= 0) {
        consoleLogger.consoleLog("Invalid price. Please enter a positive number.");
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        return;
    }

    std::cout << "Enter New Quantity: ";
    std::cin >> newQuantity;
    if (std::cin.fail() || newQuantity <= 0) {
        consoleLogger.consoleLog("Invalid quantity. Please enter a positive integer.");
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        return;
    }
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // Clear buffer

    matchingEngine.modifyOrder(orderId, newPrice, newQuantity);
}

void CLI::cancelOrder() {
    std::string orderId;
    consoleLogger.consoleLog("\n--- Cancel Order ---");
    std::cout << "Enter Order ID to cancel: ";
    std::getline(std::cin, orderId);

    if (matchingEngine.cancelOrder(orderId)) {
        consoleLogger.consoleLog("Order " + orderId + " cancelled successfully.");
    } else {
        consoleLogger.consoleLog("Failed to cancel order " + orderId + ". It might not exist or already be matched.");
    }
}

void CLI::viewOrderBook() {
    std::string symbol;
    consoleLogger.consoleLog("\n--- View Order Book ---");
    std::cout << "Enter Symbol to view (e.g., AAPL): ";
    std::getline(std::cin, symbol);
    matchingEngine.printOrderBook(symbol);
}

void CLI::exportData() {
    consoleLogger.consoleLog("\n--- Exporting All Current Orders ---");
    tradeLogger.saveAllOrders(matchingEngine.getAllOrders());
    consoleLogger.consoleLog("All current orders exported to orders.csv.");
}

std::string CLI::generateUniqueOrderId() {
    static std::random_device rd;
    static std::mt19937 generator(rd());
    static std::uniform_int_distribution<long long unsigned> distribution(1, std::numeric_limits<long long unsigned>::max());
    return "ORD-" + std::to_string(distribution(generator));
}


