// Copyright (C) 2019-2023 Anders Logg, Dag Wästberg
// Licensed under the MIT License

#ifndef DTCC_MERGE_POLYGONS_H
#define DTCC_MERGE_POLYGONS_H

#include <vector>
#include <queue>
#include <tuple>

#include <model/Polygon.h>
#include <BoundingBox.h>
#include <model/Point.h>
#include <Constants.h>
#include <Grid.h>
#include <GEOS.h>

namespace DTCC_BUILDER
{
  class PolygonProcessor
  {
  public:
    typedef std::vector<std::vector<size_t>> MergedIndices;
    typedef std::tuple<std::vector<Polygon>, MergedIndices> MergedPolygonResult;
    // Merge polygons
    static MergedPolygonResult MergePolygons(const std::vector<Polygon> &polygons,
                                             double minimalDistance,
                                             std::vector<Polygon> &mergedPolygons)
    {
      GEOS::Init();
      const double tol2 = minimalDistance * minimalDistance;
      MergedIndices mergedIndices{};
      mergedPolygons = polygons;
      // Counters
      size_t numMerged = 0;
      size_t numCompared = 0;

      // Initialize grid
      // Note: Grid size needs to be *at least* minimal distance
      // Note: Factor 4 seems to be a good choice (tested using dtcc-bench-run)
      double h = 4.0 * ComputeMeanPolygonSize(polygons);
      BoundingBox2D bbox = ComputeBoundingBox(polygons);
      h = std::max(h, minimalDistance + Constants::Epsilon);
      size_t nX = static_cast<size_t>((bbox.Q.x - bbox.P.x) / h) + 1;
      size_t nY = static_cast<size_t>((bbox.Q.y - bbox.P.y) / h) + 1;
      if (nX <= 1 || nY <= 1)
      {
        // needed for meshing small areas
        nX = static_cast<size_t>((bbox.Q.x - bbox.P.x) / (h / 4)) + 1;
        nY = static_cast<size_t>((bbox.Q.y - bbox.P.y) / (h / 4)) + 1;
      }
      Grid grid(bbox, nX, nY);

      // Initialize bins
      std::vector<std::unordered_set<size_t>> polygons2bins{polygons.size()};
      std::vector<std::unordered_set<size_t>> bin2polygons{grid.NumVertices()};
      for (size_t i = 0; i < polygons.size(); i++)
        UpdateBinning(polygons2bins, bin2polygons, i, polygons[i], grid);
      // Create queue of indices to check
      std::queue<size_t> indices{};
      for (size_t i = 0; i < polygons.size(); i++)
        indices.push(i);
      // Process queue until empty
      while (!indices.empty())
      {
        std::vector<size_t> merged{};
        // Pop index of next building to check
        const size_t i = indices.front();
        indices.pop();

        // Get neighbor indices
        std::unordered_set<size_t> neighbors{
            GetNeighbors(i, polygons2bins, bin2polygons)};

        // Iterate over neighbors
        for (size_t j : neighbors)
        {
          // Skip building itself
          if (i == j)
            continue;

          // Skip if merged with other building (size set to 0)
          if (polygons[j].Vertices.empty())
            continue;

          // Compute distance
          const Polygon &Pi = mergedPolygons[i];
          const Polygon &Pj = mergedPolygons[j];
          const double d2 = Geometry::SquaredDistance2D(Pi, Pj);
          numCompared++;

          // Merge if distance is small
          if (d2 < tol2)
          {
            debug("CityBuilder: Buildings " + str(i) + " and " + str(j) +
                  " are too close, merging");

            // Merge buildings
            // MergedIndices.push_back({i, j});
            // buildings[i].AttachedUUIDs.push_back(buildings[j].UUID);
            Polygon mergedPolygon = GEOS::MergePolygons(
                Pi, Pj, minimalDistance);
            mergedPolygons[i] = mergedPolygon;
            // MergeBuildings(buildings[i], buildings[j], minimalBuildingDistance);
            numMerged++;

            // Update binning
            UpdateBinning(polygons2bins, bin2polygons, i, mergedPolygons[i], grid);

            // Add building back to queue
            indices.push(i);
          }
        }
      }
      GEOS::Finish();
      MergedPolygonResult result{mergedPolygons, mergedIndices};
      return result;
    }

  private:
    static double ComputeMeanPolygonSize(const std::vector<Polygon> &polygons)
    {
      double meanSize = 0.0;
      double min_x, min_y, max_x, max_y;
      constexpr double max = std::numeric_limits<double>::max();

      for (const auto &polygon : polygons)
      {
        min_x = min_y = max;
        max_x = max_y = -max;
        for (auto vertex : polygon.Vertices)
        {
          min_x = std::min(min_x, vertex.x);
          min_y = std::min(min_y, vertex.y);
          max_x = std::max(max_x, vertex.x);
          max_y = std::max(max_y, vertex.y);
        }
        meanSize += std::max(max_x - min_x, max_y - min_y);
      }
      return meanSize / polygons.size();
    }

    static BoundingBox2D ComputeBoundingBox(const std::vector<Polygon> &polygons)
    {
      double min_x = std::numeric_limits<double>::max();
      double min_y = std::numeric_limits<double>::max();
      double max_x = -std::numeric_limits<double>::max();
      double max_y = -std::numeric_limits<double>::max();

      for (const auto &polygon : polygons)
      {
        for (auto vertex : polygon.Vertices)
        {
          min_x = std::min(min_x, vertex.x);
          min_y = std::min(min_y, vertex.y);
          max_x = std::max(max_x, vertex.x);
          max_y = std::max(max_y, vertex.y);
        }
      }
      return BoundingBox2D(Point2D(min_x, min_y), Point2D(max_x, max_y));
    }
    // Update binning for for building
    static void
    UpdateBinning(std::vector<std::unordered_set<size_t>> &polygons2bins,
                  std::vector<std::unordered_set<size_t>> &bin2polygons,
                  size_t buildingIndex,
                  const Polygon &polygon,
                  const Grid &grid)
    {
      // Compute bounding box of building
      BoundingBox2D bbox(polygon.Vertices);

      // Get grid cell size
      const double hx = grid.XStep;
      const double hy = grid.YStep;

      // Get grid indices for bounding box
      long int ixMin{}, iyMin{};
      long int ixMax{}, iyMax{};
      grid.Point2Index(ixMin, iyMin, bbox.P);
      grid.Point2Index(ixMax, iyMax, bbox.Q);

      // Check margin
      double xMin = grid.BoundingBox.P.x + ixMin * hx;
      double yMin = grid.BoundingBox.P.y + iyMin * hy;
      double xMax = grid.BoundingBox.P.x + ixMax * hx;
      double yMax = grid.BoundingBox.P.y + iyMax * hy;
      if (xMin - bbox.P.x + Constants::Epsilon > 0.0)
        ixMin -= 1;
      if (yMin - bbox.P.y + Constants::Epsilon > 0.0)
        iyMin -= 1;
      if (bbox.Q.x - xMax + Constants::Epsilon > 0.0)
        ixMax += 1;
      if (bbox.Q.y - yMax + Constants::Epsilon > 0.0)
        iyMax += 1;

      // Check overflow
      if (ixMin < 0)
        ixMin = 0;
      if (iyMin < 0)
        iyMin = 0;
      if (ixMax >= grid.XSize)
        ixMax = grid.XSize - 1;
      if (iyMax >= grid.YSize)
        iyMax = grid.YSize - 1;

      // Add to bins
      for (long int ix = ixMin; ix <= ixMax; ix++)
      {
        for (long int iy = iyMin; iy <= iyMax; iy++)
        {
          const long int binIndex = grid.Index2Index(ix, iy);
          polygons2bins[buildingIndex].insert(binIndex);
          bin2polygons[binIndex].insert(buildingIndex);
        }
      }

      // Sanity check: These numbers should never be larger
      // than 0 and only rarely smaller than -0.5
      const long int minIndex = grid.Index2Index(ixMin, iyMin);
      const long int maxIndex = grid.Index2Index(ixMax, iyMax);
      const Point2D P = grid.Index2Point(minIndex);
      const Point2D Q = grid.Index2Point(maxIndex);
      const double dxMin = (P.x - bbox.P.x) / hx;
      const double dxMax = (bbox.Q.x - Q.x) / hx;
      const double dyMin = (P.y - bbox.P.y) / hy;
      const double dyMax = (bbox.Q.y - Q.y) / hy;
      // std::cout << "CHECK: " << dxMin << " " << dxMax << " " << dyMin << " " <<
      //  dyMax << std::endl;
      assert(dxMin < 0.0);
      assert(dxMax < 0.0);
      assert(dyMin < 0.0);
      assert(dyMax < 0.0);
    }

    // Get neighbors of building (buildings with overlapping bins)
    static std::unordered_set<size_t>
    GetNeighbors(size_t buildingIndex,
                 const std::vector<std::unordered_set<size_t>> &polygons2bins,
                 const std::vector<std::unordered_set<size_t>> &bin2polygons)
    {
      std::unordered_set<size_t> indices{};
      for (const auto binIndex : polygons2bins[buildingIndex])
        for (const auto index : bin2polygons[binIndex])
          indices.insert(index);
      return indices;
    }
  };
} // namespace DTCC_BUILDER

#endif