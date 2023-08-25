#include "KDTreeVectorOfVectorsAdaptor.h"
#include "nanoflann.hpp"

#include "model/Point.h"
#include "model/Vector.h"

/// Returns the Distance to the K nearest neighbors for each point in
/// points
std::vector<std::vector<double>>
KNNNearestNeighboursDist(const std::vector<DTCC_BUILDER::Point3D> &points, size_t neighbours)
{
    size_t pc_size = points.size();
    std::vector<std::vector<double>> neighbourDist(pc_size);

    if (neighbours <= 0 or neighbours > pc_size)
    {
        neighbours = pc_size;
    }
    neighbours++; // N neighbours other than ourselves

    typedef KDTreeVectorOfVectorsAdaptor<std::vector<DTCC_BUILDER::Point3D>, double,
                                         3 /* dims */>
        my_kd_tree_t;
    my_kd_tree_t pc_index(3 /*dim*/, points, 10 /* max leaf */);
    pc_index.index->buildIndex();
    std::vector<size_t> ret_indexes(neighbours);
    std::vector<double> out_dists_sqr(neighbours);
    nanoflann::KNNResultSet<double> resultSet(neighbours);
    resultSet.init(&ret_indexes[0], &out_dists_sqr[0]);

    size_t idx = 0;
    for (auto const &pt : points)
    {
        std::vector<double> query_pt{pt.x, pt.y, pt.z};
        pc_index.query(&query_pt[0], neighbours, &ret_indexes[0],
                       &out_dists_sqr[0]);
        for (size_t i = 1; i < neighbours;
             i++) // start from 1 since 0 is the query point
        {
            neighbourDist[idx].push_back(std::sqrt(out_dists_sqr[i]));
        }
        idx++;
    }

    return neighbourDist;
}

/// Returns the index of the K nearest neighbors for each point in
/// points
std::vector<std::vector<size_t>>
KNNNearestNeighboursIdx(const std::vector<DTCC_BUILDER::Point3D> &points, size_t neighbours)
{
    size_t pc_size = points.size();
    std::vector<std::vector<size_t>> neighbourIdx(pc_size);

    if (neighbours <= 0 or neighbours > pc_size)
    {
        neighbours = pc_size;
    }
    neighbours++; // N neighbours other than ourselves

    typedef KDTreeVectorOfVectorsAdaptor<std::vector<DTCC_BUILDER::Point3D>, double,
                                         3 /* dims */>
        my_kd_tree_t;
    my_kd_tree_t pc_index(3 /*dim*/, points, 10 /* max leaf */);
    pc_index.index->buildIndex();
    std::vector<size_t> ret_indexes(neighbours);
    std::vector<double> out_dists_sqr(neighbours);
    nanoflann::KNNResultSet<double> resultSet(neighbours);
    resultSet.init(&ret_indexes[0], &out_dists_sqr[0]);
    size_t idx = 0;
    for (auto const &pt : points)
    {
        std::vector<double> query_pt{pt.x, pt.y, pt.z};
        pc_index.query(&query_pt[0], neighbours, &ret_indexes[0],
                       &out_dists_sqr[0]);
        for (size_t i = 1; i < neighbours;
             i++) // start from 1 since 0 is the query point
        {
            neighbourIdx[idx].push_back(ret_indexes[i]);
        }
        idx++;
    }

    return neighbourIdx;
}
