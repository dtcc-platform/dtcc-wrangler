
#include "model/Point.h"
#include "model/Vector.h"
#include "NearestNeighbours.h"
#include "Logging.h"

namespace DTCC_BUILDER
{

    class PointCloudProcessor
    {
    public:
        /// Finds outliers from vector of points by removing all points more than a
        /// given number of standard deviations from the mean distance to their N
        /// nearest neighbours
        ///
        /// @param points The vector of points
        /// @param neighbours Number of neighbours to consider. If less than 1 or
        /// greater than the number of points in the point cloud use all points
        /// @param outlierMargin Number of standard deviations
        /// @return Vector of indices of outlier points
        static std::vector<size_t>
        StatisticalOutlierFinder(const std::vector<Point3D> &points,
                                 size_t neighbours,
                                 double outlierMargin,
                                 bool verbose = false)
        {
            // Check that we have enough points
            if (points.size() <= neighbours)
                return std::vector<size_t>();

            std::vector<size_t> outliers;

            auto neighbourDist = KNNNearestNeighboursDist(points, neighbours);
            std::vector<double> u_dist_i;

            for (size_t i = 0; i < points.size(); i++)
            {
                double dsum = 0;
                for (auto &d : neighbourDist[i])
                {
                    dsum += d;
                }
                u_dist_i.push_back(dsum / neighbours);
            }

            // Compute mean
            double mean{0};
            for (auto p : u_dist_i)
                mean += p;
            mean /= u_dist_i.size();

            // Compute standard deviation
            double std{0};
            for (auto p : u_dist_i)
                std += (p - mean) * (p - mean);
            std /= u_dist_i.size() - 1;
            std = std::sqrt(std);

            double T = mean + outlierMargin * std;

            info("T: " + str(T));
            for (size_t i = 0; i < u_dist_i.size(); i++)
            {
                if (u_dist_i[i] > T)
                    outliers.push_back(i);
            }

            return outliers;
        }
    };
} // namespace DTCC_BUILDER