// Copyright (C) 2023 Dag Wästberg
// Licensed under the MIT License

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <pybind11/stl.h>

#include "model/Point.h"
#include "model/Vector.h"
#include "model/Polygon.h"

#include "PointCloudProcessor.h"

namespace py = pybind11;

namespace DTCC_WRANGLER
{
    std::vector<size_t> PyStatisticalOutlierFinder(py::array_t<double> pts,
                                                   size_t neighbours,
                                                   double outlierMargin)
    {
        auto pts_r = pts.unchecked<2>();
        auto pt_count = pts_r.shape(0);
        std::vector<DTCC_BUILDER::Point3D> points(pt_count);
        for (size_t i = 0; i < pt_count; i++)
        {
            points[i] = DTCC_BUILDER::Point3D(pts_r(i, 0), pts_r(i, 1), pts_r(i, 2));
        }
        return DTCC_BUILDER::PointCloudProcessor::StatisticalOutlierFinder(points, neighbours, outlierMargin, false);
    }

}

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

    py::class_<DTCC_BUILDER::Point3D>(m, "Point3D")
        .def(py::init<>())
        .def("__repr__",
             [](const DTCC_BUILDER::Point3D &p)
             {
                 return "<Point3D (" + DTCC_BUILDER::str(p.x) + ", " +
                        DTCC_BUILDER::str(p.y) + ", " + DTCC_BUILDER::str(p.z) +
                        ")>";
             })
        .def_readonly("x", &DTCC_BUILDER::Point3D::x)
        .def_readonly("y", &DTCC_BUILDER::Point3D::y)
        .def_readonly("z", &DTCC_BUILDER::Point3D::z);

    py::class_<DTCC_BUILDER::Vector3D>(m, "Vector3D")
        .def(py::init<>())
        .def_readonly("x", &DTCC_BUILDER::Vector3D::x)
        .def_readonly("y", &DTCC_BUILDER::Vector3D::y)
        .def_readonly("z", &DTCC_BUILDER::Vector3D::z);

    m.def("statisitical_outlier_finder", &DTCC_WRANGLER::PyStatisticalOutlierFinder, "find statistical outliers in a point cloud");
}