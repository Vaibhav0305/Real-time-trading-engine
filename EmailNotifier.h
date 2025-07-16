#ifndef EMAIL_NOTIFIER_H
#define EMAIL_NOTIFIER_H

#include <string>
#include <iostream>

class EmailNotifier {
public:
    void sendTradeNotification(const std::string& tradeDetails) {
        printColored("\n--- Mock Email Notification ---\n", 36);
        std::cout << "To: User (mocked)\n";
        std::cout << "Subject: Trade Matched!\n";
        std::cout << "Body:\n" << tradeDetails << "\n";
        std::cout << "-------------------------------\n\n";
        logNotification("Trade Notification: " + tradeDetails);
    }

    void sendOrderPlaced(const std::string& orderDetails) {
        printColored("[Order Placed] ", 32); // Green
        std::cout << orderDetails << std::endl;
        logNotification("Order Placed: " + orderDetails);
    }

    void sendOrderModified(const std::string& orderDetails) {
        printColored("[Order Modified] ", 34); // Blue
        std::cout << orderDetails << std::endl;
        logNotification("Order Modified: " + orderDetails);
    }

    void sendOrderCancelled(const std::string& orderDetails) {
        printColored("[Order Cancelled] ", 31); // Red
        std::cout << orderDetails << std::endl;
        logNotification("Order Cancelled: " + orderDetails);
    }

private:
    void printColored(const std::string& text, int colorCode) {
        std::cout << "\033[" << colorCode << "m" << text << "\033[0m";
    }
    void logNotification(const std::string& msg) {
        std::ofstream notifLog("notifications.log", std::ios::app);
        if (notifLog.is_open()) {
            notifLog << msg << std::endl;
        }
    }
};

#endif // EMAIL_NOTIFIER_H


