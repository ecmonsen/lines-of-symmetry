"""
Unit tests for symmetry project
"""
from unittest import main as test_main, TestCase
from symmetry import *
from decimal import getcontext
import sys
import os

PRECISION = 100


class SymmetryTests(TestCase):
    @classmethod
    def setUpClass(cls):
        logger.debug(f"Setting precision to {PRECISION}")
        cls.prec = getcontext().prec
        getcontext().prec = PRECISION

    @classmethod
    def tearDownClass(cls):
        # reset precision
        logger.debug(f"Resetting precision to {cls.prec}")
        getcontext().prec = cls.prec

    # def test_point_constructor_with_float(self):
    #     Point(2,3)
    #     Point("3.0", "4.00000001")
    #     with self.assertRaises(ValueError):
    #         Point(1.0,1)
    #     with self.assertRaises(ValueError):
    #         Point(2, 2.01)

    def test_bisection_point_repr(self):
        bp = BisectionPoint(Point("4", "1"), Point("8", "2"))
        self.assertEqual("BisectionPoint(x=6,y=1.5)[Point(x=4,y=1),Point(x=8,y=2)]", str(bp))

    def test_bisection_point___eq__(self):
        bp = BisectionPoint(Point(4, 1), Point(8, 2))
        self.assertEqual(Point(x=6.0, y=1.5), bp)

    def test_from_points(self):
        line = Line.from_points(Point(4, 1), Point(2, -2))
        self.assertEqual(line.slope, 1.5)
        self.assertEqual(line.intercept, -5)
        self.assertTrue(math.isnan(line.x))
        self.assertFalse(line.is_vertical())

    def test_from_points_vertical(self):
        line = Line.from_points(Point(4, 1), Point(4, 5))
        self.assertTrue(math.isnan(line.slope))
        self.assertTrue(math.isnan(line.intercept))
        self.assertEqual(4, line.x)
        self.assertTrue(line.is_vertical())

    def test_point___eq__(self):
        self.assertNotEqual(Point(1, 1), Point(1, 2))
        self.assertNotEqual(Point(1, 1), Point(2, 1))
        self.assertNotEqual(Point(1, 2), Point(3, 4))
        self.assertEqual(Point(1, 1), Point(1, 1))
        self.assertEqual(Point(1.1, 2.1), Point(1.1, 2.1))

    def test_line___eq__(self):
        self.assertNotEqual(Line(1, 1), Line(1, 2))
        self.assertNotEqual(Line(1, 1), Line(2, 1))
        self.assertNotEqual(Line(1, 2), Line(3, 4))
        self.assertEqual(Line(1, 1), Line(1, 1))
        self.assertEqual(Line(1.1, 2.1), Line(1.1, 2.1))
        self.assertEqual(Line(1.1, 2.1, 3), Line(1.1, 2.1, 5))  # superfluous x is ignored
        self.assertEqual(Line(x=3), Line(x=3))
        self.assertNotEqual(Line(x=3), Line(x=5))

    def test_bisection_point(self):
        bp = BisectionPoint(Point(1, 2), Point(2, 2))
        p = Point(1.5, 2.0)
        self.assertTrue(bp == p)

        self.assertEqual(
            BisectionPoint(Point(1, 2), Point(2, 2)),
            Point(1.5, 2.0)
        )

    def test_is_horizontal(self):
        self.assertTrue(Line(slope=0, intercept=8).is_horizontal())
        self.assertTrue(Line(slope=0, intercept=0).is_horizontal())

    def test_perpendicular_intersection_point_horizontal(self):
        line = Line(slope=0, intercept=5)
        point = Point(x=4, y=-10)
        self.assertEqual(Point(x=4, y=5), line.perpendicular_intersection_point(point))

    def test_perpendicular_intersection_point_vertical(self):
        line = Line(x=15.5)
        point = Point(x=4, y=-10)
        self.assertEqual(Point(x=15.5, y=-10), line.perpendicular_intersection_point(point))

    def test_perpendicular_intersection_point(self):
        line = Line(slope=1, intercept=2)
        point = Point(x=1, y=1)
        self.assertEqual(Point(x=0, y=2), line.perpendicular_intersection_point(point))
        self.assertEqual(Point(x=1, y=3), line.perpendicular_intersection_point(Point(2, 2)))

    def test_centroid_triangle(self):
        points = [
            Point(0, 50),
            Point(50, 50),
            Point(50, 0),
        ]
        self.assertEqual(Point(Decimal(100) / Decimal(3), Decimal(100) / Decimal(3)),
                         SymmetryLineFinder(points)._centroid())

    def test_fold_point_over_horizontal(self):
        line = Line(slope=0, intercept=25)
        self.assertEqual(Point(25, 30), line.folded_point(Point(25, 20)))

    def test_fold_point_over_vertical(self):
        line = Line(x=26)
        self.assertEqual(Point(27, 30), line.folded_point(Point(25, 30)))

    def test_fold_point_on_horizontal_line(self):
        line = Line(slope=0, intercept=25)
        self.assertEqual(Point(25, 25), line.folded_point(Point(25, 25)))

    def test_fold_point_on_vertical_line(self):
        line = Line(x=4.3)
        self.assertEqual(Point(4.3, 30), line.folded_point(Point(4.3, 30)))

    def test_fold_point(self):
        line = Line(slope=1, intercept=2)
        self.assertEqual(Point(-1, 3), line.folded_point(Point(1, 1)))

    def test_candidate_symmetry_lines_triangle(self):
        points = [
            Point(0, 50),
            Point(50, 50),
            Point(50, 0),
        ]
        candidates = set(SymmetryLineFinder(points)._candidate_symmetry_lines())
        expected_lines = {Line(slope=1, intercept=0), Line(slope=-2, intercept=100), Line(slope=-0.5, intercept=50)}
        self.assertEqual(expected_lines, set(candidates))

    def test_candidate_symmetry_lines_rectangle(self):
        points = [
            Point(0, 50),
            Point(50, 50),
            Point(50, 0),
            Point(0, 0)
        ]
        candidates = list(SymmetryLineFinder(points)._candidate_symmetry_lines())
        expected_lines = {
            # _centroid to vertex
            Line(slope=1, intercept=0),
            Line(slope=-1, intercept=50),
            # _centroid to bisect
            Line(x=25),
            Line(slope=0, intercept=25),
        }
        self.assertEqual(expected_lines, set(candidates))

    def test_candidate_symmetry_lines_2_points(self):
        points = [Point(1.1, 2.2), Point(3.3, 4.4)]
        with self.assertRaises(ValueError):
            SymmetryLineFinder(points)._candidate_symmetry_lines()

    def test_candidate_symmetry_lines_1_points(self):
        points = [Point(1.1, 2.2)]
        with self.assertRaises(ValueError):
            SymmetryLineFinder(points)._candidate_symmetry_lines()

    def test_find_square(self):
        points = [Point(501, 501), Point(501, 1001), Point(1001, 1001), Point(1001, 501)]
        expected_lines = {
            Line(slope=1, intercept=0),
            Line(slope=-1, intercept=1502),
            Line(x=751),
            Line(slope=0, intercept=751)
        }
        lines = set(SymmetryLineFinder(points).find())
        self.assertEqual(expected_lines, lines)

    def test_find_square_2(self):
        points = [Point("501.000000000000000001", 501),
                  Point("501.000000000000000001", 1001),
                  Point("1001.000000000000000001", 1001),
                  Point("1001.000000000000000001", 501)]
        expected_lines = {
            Line(slope=1, intercept="-0.000000000000000001"),
            Line(slope=-1, intercept="1502.000000000000000001"),
            Line(x="751.000000000000000001"),
            Line(slope=0, intercept=751)
        }
        lines = set(SymmetryLineFinder(points).find())
        self.assertEqual(expected_lines, lines)

    def test_find_verysmall_and_verylarge(self):
        points = [Point("1e-16", "1e-16"),
                  Point("1e-16", "1e+16"),
                  Point("1e+16", "1e+16"),
                  Point("1e+16", "1e-16"),
                  ]
        # print(" ".join([f"{p.x},{p.y}" for p in points]))
        expected_lines = {
            Line(x="5000000000000000.00000000000000005"),
            Line(slope="-1", intercept="10000000000000000.0000000000000001"),
            Line(slope="1", intercept="0"),
            Line(slope="0", intercept="5000000000000000.00000000000000005")
        }
        lines = set(SymmetryLineFinder(points).find())
        self.assertEqual(expected_lines, lines)


if __name__ == "__main__":
    logger = logging.getLogger("symmetry")
    log_level = getattr(logging, os.environ.get("LOG_LEVEL", "ERROR"))
    logger.level = log_level
    logger.addHandler(logging.StreamHandler(sys.stdout))

    test_main()
