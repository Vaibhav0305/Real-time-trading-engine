
#include "MatchingEngine.h"
#include "TradeLogger.h"
#include "CLI.h"
#include "Logger.h"
#include "EmailNotifier.h"
#include <iomanip>

// Utility for colored CLI output
void printColored(const std::string& text, int colorCode) {
    std::cout << "\033[" << colorCode << "m" << text << "\033[0m";
}


int main() {
    Logger consoleLogger("vittcott_log.txt");
    EmailNotifier emailNotifier;
    MatchingEngine matchingEngine(consoleLogger, emailNotifier);
    TradeLogger tradeLogger(consoleLogger);

    while (true) {
        // Main CLI menu
        printColored("\n1. Place Order\n", 36);
        printColored("2. Modify Order\n", 36);
        printColored("3. Cancel Order\n", 36);
        printColored("4. Print Order Book\n", 36);
        printColored("5. Exit\n", 36);
        printColored("Enter your choice: ", 33);
        int choice;
        std::cin >> choice;
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

        if (choice == 1) {
            try {
                std::string symbol, typeStr;
                double price;
                int quantity;
                std::cout << "Enter Symbol (e.g., AAPL): ";
                std::getline(std::cin, symbol);
                std::cout << "Enter Type (BUY/SELL): ";
                std::getline(std::cin, typeStr);
                OrderType type;
                if (typeStr == "BUY" || typeStr == "buy") type = BUY;
                else if (typeStr == "SELL" || typeStr == "sell") type = SELL;
                else {
                printColored("Invalid order type.\n", 31);
                    continue;
                }
                std::cout << "Enter Price: ";
                std::cin >> price;
                if (std::cin.fail() || price <= 0) {
                    printColored("Invalid price.\n", 31);
                    std::cin.clear();
                    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
                    continue;
                }
                std::cout << "Enter Quantity: ";
                std::cin >> quantity;
                if (std::cin.fail() || quantity <= 0) {
                    printColored("Invalid quantity.\n", 31);
                    std::cin.clear();
                    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
                    continue;
                }
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
                // Generate unique orderId and check for duplicates
                std::string orderId;
                bool unique = false;
                int attempts = 0;
                do {
                    orderId = "ORD-" + std::to_string(std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count()) + std::to_string(rand() % 10000);
                    auto allOrders = matchingEngine.getAllOrders();
                    unique = std::none_of(allOrders.begin(), allOrders.end(), [&](const Order& o) { return o.getOrderId() == orderId; });
                    attempts++;
                } while (!unique && attempts < 5);
                if (!unique) {
                printColored("Error: Could not generate unique order ID. Try again.\n", 31);
                    std::ofstream errLog("error.log", std::ios::app); errLog << "Failed to generate unique order ID after 5 attempts.\n";
                    continue;
                }
                Order order(orderId, symbol, type, price, quantity);
                tradeLogger.logOrder(order);
                emailNotifier.sendOrderPlaced(order.toString());
                auto trades = matchingEngine.placeOrder(order);
                for (const auto& trade : trades) {
                    tradeLogger.logTrade(trade);
                    emailNotifier.sendTradeNotification(trade.toString());
                }
                printColored("Order placed with ID: ", 32);
                std::cout << orderId << "\n";
            } catch (const std::exception& ex) {
                printColored("Exception: ", 31);
                std::cout << ex.what() << "\n";
                std::ofstream errLog("error.log", std::ios::app); errLog << "Exception in Place Order: " << ex.what() << "\n";
            }
        } else if (choice == 2) {
            std::string orderId;
            double newPrice;
            int newQuantity;
            std::cout << "Enter Order ID to modify: ";
            std::getline(std::cin, orderId);
            std::cout << "Enter New Price: ";
            std::cin >> newPrice;
            if (std::cin.fail() || newPrice <= 0) {
                printColored("Invalid price.\n", 31);
                std::cin.clear();
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
                continue;
            }
            std::cout << "Enter New Quantity: ";
            std::cin >> newQuantity;
            if (std::cin.fail() || newQuantity <= 0) {
                printColored("Invalid quantity.\n", 31);
                std::cin.clear();
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
                continue;
            }
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            try {
                auto trades = matchingEngine.modifyOrder(orderId, newPrice, newQuantity);
                emailNotifier.sendOrderModified("Order ID: " + orderId + ", New Price: " + std::to_string(newPrice) + ", New Quantity: " + std::to_string(newQuantity));
                for (const auto& trade : trades) {
                    tradeLogger.logTrade(trade);
                    emailNotifier.sendTradeNotification(trade.toString());
                }
                printColored("Order modified.\n", 32);
            } catch (const std::exception& ex) {
                printColored("Exception: ", 31);
                std::cout << ex.what() << "\n";
                std::ofstream errLog("error.log", std::ios::app); errLog << "Exception in Modify Order: " << ex.what() << "\n";
            }
        } else if (choice == 3) {
            std::string orderId;
            std::cout << "Enter Order ID to cancel: ";
            std::getline(std::cin, orderId);
            try {
                if (matchingEngine.cancelOrder(orderId)) {
                    emailNotifier.sendOrderCancelled("Order ID: " + orderId);
                printColored("Order ", 32);
                std::cout << orderId << " cancelled.\n";
                } else {
                printColored("Order not found or already matched.\n", 31);
                }
            } catch (const std::exception& ex) {
                printColored("Exception: ", 31);
                std::cout << ex.what() << "\n";
                std::ofstream errLog("error.log", std::ios::app); errLog << "Exception in Cancel Order: " << ex.what() << "\n";
            }
        } else if (choice == 4) {
            std::string symbol;
            printColored("Enter Symbol to view: ", 33);
            std::getline(std::cin, symbol);
            try {
                matchingEngine.printOrderBook(symbol);
            } catch (const std::exception& ex) {
                printColored("Exception: ", 31);
                std::cout << ex.what() << "\n";
                std::ofstream errLog("error.log", std::ios::app); errLog << "Exception in Print Order Book: " << ex.what() << "\n";
            }
        } else if (choice == 5) {
            // Export all orders to CSV
            try {
                auto allOrders = matchingEngine.getAllOrders();
                tradeLogger.saveAllOrders(allOrders);
            printColored("All orders exported. Exiting.\n", 32);
                break;
            } catch (const std::exception& ex) {
            printColored("Exception: ", 31);
            std::cout << ex.what() << "\n";
                std::ofstream errLog("error.log", std::ios::app); errLog << "Exception in Export Orders: " << ex.what() << "\n";
            }
        } else {
            printColored("Invalid choice.\n", 31);
        }
    }
    return 0;
}


