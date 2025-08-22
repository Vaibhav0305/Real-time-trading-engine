// 🔗 binding.cpp - Exposes C++ engine to Python via pybind11

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "OrderBook.h"
#include "Logger.h"
#include "Trade.h"
#include "Order.h"
#include "EmailNotifier.h"
#include "MatchingEngine.h"

namespace py = pybind11;

PYBIND11_MODULE(trading_engine, m) {
    // Order class
    py::class_<Order>(m, "Order")
        .def(py::init<const std::string&, const std::string&, OrderType, double, int>())
        .def("getOrderId", &Order::getOrderId)
        .def("getSymbol", &Order::getSymbol)
        .def("getType", &Order::getType)
        .def("getPrice", &Order::getPrice)
        .def("getQuantity", &Order::getQuantity)
        .def("setPrice", &Order::setPrice)
        .def("setQuantity", &Order::setQuantity)
        .def("toString", &Order::toString);

    // OrderType enum
    py::enum_<OrderType>(m, "OrderType")
        .value("BUY", OrderType::BUY)
        .value("SELL", OrderType::SELL)
        .export_values();

    // Trade class
    py::class_<Trade>(m, "Trade")
        .def(py::init<const std::string&, const std::string&, const std::string&, const std::string&, double, int>())
        .def("getTradeId", &Trade::getTradeId)
        .def("getBuyOrderId", &Trade::getBuyOrderId)
        .def("getSellOrderId", &Trade::getSellOrderId)
        .def("getSymbol", &Trade::getSymbol)
        .def("getPrice", &Trade::getPrice)
        .def("getQuantity", &Trade::getQuantity)
        .def("getTimestamp", &Trade::getTimestamp)
        .def("toString", &Trade::toString)
        .def("toCSV", &Trade::toCSV);

    // Logger class
    py::class_<Logger>(m, "Logger")
        .def(py::init<const std::string&>())
        .def("log", &Logger::log);

    // EmailNotifier class
    py::class_<EmailNotifier>(m, "EmailNotifier")
        .def(py::init<>())
        .def("sendOrderPlacedNotification", &EmailNotifier::sendOrderPlacedNotification)
        .def("sendOrderCancelledNotification", &EmailNotifier::sendOrderCancelledNotification)
        .def("sendTradeExecutedNotification", &EmailNotifier::sendTradeExecutedNotification);

    // OrderBook class
    py::class_<OrderBook>(m, "OrderBook")
        .def(py::init<const std::string&, Logger&, EmailNotifier&>())
        .def("addOrder", &OrderBook::addOrder)
        .def("cancelOrder", &OrderBook::cancelOrder)
        .def("modifyOrder", &OrderBook::modifyOrder)
        .def("getAllOrders", &OrderBook::getAllOrders)
        .def("matchOrders", &OrderBook::matchOrders);

    // MatchingEngine class - Main interface for Python
    py::class_<MatchingEngine>(m, "MatchingEngine")
        .def(py::init<Logger&, EmailNotifier&>())
        .def("placeOrder", &MatchingEngine::placeOrder)
        .def("cancelOrder", &MatchingEngine::cancelOrder)
        .def("modifyOrder", &MatchingEngine::modifyOrder)
        .def("getAllOrders", &MatchingEngine::getAllOrders)
        .def("matchOrders", &MatchingEngine::matchOrders);
}
