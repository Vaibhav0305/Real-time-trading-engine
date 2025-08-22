#include <pybind11/pybind11.h>
namespace py = pybind11;

PYBIND11_MODULE(matching_engine, m) {
    m.doc() = "Minimal pybind11 matching engine module";
}