#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include "PolygonProcessor.h"
#include "model/Polygon.h"

namespace py = pybind11;

namespace DTCC_BUILDER
{

} // namespace DTCC_BUILDER

PYBIND11_MODULE(_dtcc_wrangler, m)
{
    py::class_<DTCC_BUILDER::Point2D>(m, "Point2D")
        .def(py::init<>())
        .def("__repr__",
             [](const DTCC_BUILDER::Point3D &p)
             {
                 return "<Point3D (" + DTCC_BUILDER::str(p.x) + ", " +
                        DTCC_BUILDER::str(p.y) + ")>";
             })
        .def_readonly("x", &DTCC_BUILDER::Point2D::x)
        .def_readonly("y", &DTCC_BUILDER::Point2D::y);

    py::class_<DTCC_BUILDER::Polygon>(m, "Polygon")
        .def(py::init<>())
        .def_readonly("vertices", &DTCC_BUILDER::Polygon::Vertices);
}
