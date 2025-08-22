#include <winsock2.h>
#include <ws2tcpip.h>
#include <iostream>
#include <string>
#include <sstream>
#include <chrono>
#include "MatchingEngine.h"
#include "Logger.h"
#include "EmailNotifier.h"
#include "Order.h"
#include "Trade.h"
#pragma comment(lib, "ws2_32.lib")

#define PORT 8080
#define BUFFER_SIZE 1024

// Global engine objects
Logger logger("engine.log");
EmailNotifier notifier;
MatchingEngine engine(logger, notifier);

// Example: parse CSV order: "ORDER,orderId,symbol,BUY,100.5,10"
void handleRequest(const std::string& request, SOCKET clientSocket) {
    std::istringstream iss(request);
    std::string type, orderId, symbol, side;
    double price;
    int quantity;

    getline(iss, type, ',');
    if (type == "ORDER") {
        getline(iss, orderId, ',');
        getline(iss, symbol, ',');
        getline(iss, side, ',');
        iss >> price;
        iss.ignore(1); // skip comma
        iss >> quantity;

        OrderType orderType = (side == "BUY") ? BUY : SELL;
        Order order;
        order.orderId = orderId;
        order.symbol = symbol;
        order.type = orderType;
        order.price = price;
        order.quantity = quantity;
        order.timestamp = std::chrono::system_clock::now().time_since_epoch().count();

        auto trades = engine.placeOrder(order);

        std::ostringstream oss;
        oss << "Order placed: " << order.toString() << "\n";
        for (const auto& trade : trades) {
            oss << "Trade: " << trade.toString() << "\n";
        }
        std::string response = oss.str();
        send(clientSocket, response.c_str(), static_cast<int>(response.length()), 0);
    } else {
        std::string response = "Unknown request type.\n";
        send(clientSocket, response.c_str(), static_cast<int>(response.length()), 0);
    }
}

int main() {
    WSADATA wsaData;
    SOCKET serverSocket, clientSocket;
    struct sockaddr_in serverAddr, clientAddr;
    int addrLen = sizeof(clientAddr);
    char buffer[BUFFER_SIZE] = {0};

    // Initialize Winsock
    if (WSAStartup(MAKEWORD(2,2), &wsaData) != 0) {
        std::cerr << "WSAStartup failed.\n";
        return 1;
    }

    // Create socket
    serverSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (serverSocket == INVALID_SOCKET) {
        std::cerr << "Socket creation failed.\n";
        WSACleanup();
        return 1;
    }

    // Bind
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(PORT);
    if (bind(serverSocket, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        std::cerr << "Bind failed.\n";
        closesocket(serverSocket);
        WSACleanup();
        return 1;
    }

    // Listen
    if (listen(serverSocket, SOMAXCONN) == SOCKET_ERROR) {
        std::cerr << "Listen failed.\n";
        closesocket(serverSocket);
        WSACleanup();
        return 1;
    }

    std::cout << "C++ Matching Engine Server listening on port " << PORT << "...\n";

    while (true) {
        clientSocket = accept(serverSocket, (struct sockaddr*)&clientAddr, &addrLen);
        if (clientSocket == INVALID_SOCKET) {
            std::cerr << "Accept failed.\n";
            continue;
        }
        int bytesReceived = recv(clientSocket, buffer, BUFFER_SIZE, 0);
        if (bytesReceived > 0) {
            std::string received(buffer, bytesReceived);
            std::cout << "Received Order: " << received << std::endl;
             handleRequest(received, clientSocket);
        }
        closesocket(clientSocket);
        memset(buffer, 0, sizeof(buffer));
    }

    closesocket(serverSocket);
    WSACleanup();
    return 0;
}