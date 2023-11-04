"""
main file
"""
import math
from typing import List, Iterator, Any
import logging
from decimal import *

logger = logging.getLogger("symmetry")


def normalize(d:Decimal)->Decimal:
    """
    Despite its promises of perfect accuracy, Python's Decimal does not perfectly handle divisions that
     produce repeating decimals, such as 100.0/3,0.

    Example: (0-100/3) / (50-100/3)
    When simplified symbolically, this should equal -2.
    Using Python decimals, we get:
    ```
    >>> getcontext().prec = 10
    >>> d = (Decimal("0.0") - Decimal("100.0")/Decimal("3.0"))/(Decimal("50")-Decimal("100.0")/Decimal("3.0"))
    >>> d
    Decimal('-1.999999999')
    >>> d.normalize()
    Decimal('-1.999999999')
    >>> getcontext().prec = 9
    >>> d.normalize()
    Decimal('-2')
    ```

    One workaround is to use normalize() at a slightly lower precision than the divided decimal was created
    with.

    This function returns a decimal normalized at (current precision - 1).

    TODO: Testing to make sure this works generally

    :param d: Decimal to normalize
    :return: Normalized decimal
    """
    prec = getcontext().prec
    with localcontext() as ctx:
        ctx.prec=(prec - 1)
        return d.normalize()


class Point:
    """
    Represents a single two-dimensional point (x,y) in a plane
    """

    def __init__(self, x:Any, y:Any):
        self.x = Decimal(str(x)) if x is not Decimal else x
        self.y = Decimal(str(y)) if y is not Decimal else y

    def __repr__(self):
        return f"{self.__class__.__name__}(x={normalize(self.x)},y={normalize(self.y)})"

    def __eq__(self, other):
        return normalize(self.x) == normalize(other.x) \
            and normalize(self.y) == normalize(other.y)

    def __hash__(self):
        return hash((normalize(self.x), normalize(self.y)))


class Line:
    def __init__(self, slope: Any = Decimal("nan"), intercept: Any = Decimal("nan"), x: Any = Decimal("nan"), point0=None,
                 point1=None):

        self.slope = Decimal(str(slope)) if slope is not Decimal else slope
        self.intercept = Decimal(str(intercept)) if intercept is not Decimal else intercept
        self.x = Decimal(str(x)) if x is not Decimal else x
        # self.point0 = point0
        # self.point1 = point1

    def __eq__(self, other):
        if self.is_vertical() and other.is_vertical():
            return not self.x.is_nan() and normalize(self.x) == normalize(other.x)
        return normalize(self.slope) == normalize(other.slope) \
            and normalize(self.intercept) == normalize(other.intercept)

    def __repr__(self):
        if self.is_vertical():
            return f"{self.__class__.__name__}(x={normalize(self.x)})"
        return f"{self.__class__.__name__}(m={normalize(self.slope)},b={normalize(self.intercept)})"

    def __hash__(self):
        s = normalize(self.slope) if not self.slope.is_nan() else "nan"
        i = normalize(self.intercept) if not self.intercept.is_nan() else "nan"
        x = normalize(self.x) if not self.x.is_nan() else "nan"
        h = hash((s, i, x))

        return h

    @staticmethod
    def from_points(p0: Point, p1: Point) -> "Line":
        """
        Create a Line from two points
        :param p0: First point
        :param p1: Second point
        :return: Line connecting the points
        """
        # logger.debug(f"from_points({p0}, {p1}):")
        den = p1.x - p0.x
        # logger.debug(f" den = {den}")
        if den != 0:
            # logger.debug(f"slope: {p1.y} - {p0.y} = {p1.y - p0.y}")
            slope = (p1.y - p0.y) / den
            # logger.debug(f"int part 1: ({p1.y} - {p0.y})/{den} = {slope}")
            # logger.debug(f"int part 2: ({p1.y} - {slope * p1.x}) = {(p1.y - slope * p1.x)}")
            return Line(slope, (p1.y - slope * p1.x))
        else:
            return Line(Decimal("nan"), Decimal("nan"), x=p1.x)

    def is_vertical(self):
        return self.slope.is_nan() or self.intercept.is_nan()

    def is_horizontal(self):
        return self.slope == 0

    def is_symmetry_line(self, points: List[Point]):
        """
        Evaluate whether this line is a symmetry line for the collection of points by "folding"

        :param points: Collection of points to evaluate
        :return: True if this is a symmetry line
        """
        logger.debug(f"Checking symmetry of {self}")
        for i1 in range(0, len(points)):
            matched = False
            f1 = self.folded_point(points[i1])
            logger.debug(f"- {i1}.{points[i1]} folds to to {f1.x}, {f1.y}")
            if f1 == points[i1]:
                # Point is symmetric with another point
                logger.debug("  - Folded point is identical to self.")
                continue
            for i2 in range(0, len(points)):
                logger.debug(f"  - Does folded point match {i2}.{points[i2]}?")
                if points[i2] == f1:
                    # Folded point overlaps with another point
                    # todo: remove point[i2] from future checks
                    logger.debug(f"    - Folded point corresponds to original point {i2}.")
                    matched = True
                    break
            # Folded point did not overlap any other points
            if not matched:
                logger.debug(" - Folded point did not overlap any other points")
                logger.debug(f"{self} is NOT a symmetry line")

                return False

        # Did not find_all any points that don't fold over to another point
        logger.debug(f"{self} IS a symmetry line")
        return True

    def perpendicular_intersection_point(self, p0: Point):
        #     x = (m/(m^2+1))(y0+x0/m-b)
        #     and y = mx+b
        if self.is_vertical():
            return Point(self.x, p0.y)
        if self.is_horizontal():
            return Point(p0.x, self.intercept)
        # logger.debug(f"{self.slope} / {(self.slope * self.slope + Decimal(1))} = {(self.slope / (self.slope * self.slope + Decimal(1)))}")
        # logger.debug(f"{p0.x} / {self.slope} = {(p0.x / self.slope)}")
        # logger.debug(f"{p0.y} + {p0.x / self.slope} - {self.intercept} = {(p0.y + p0.x / self.slope - self.intercept)}")
        # logger.debug(f"{(self.slope / (self.slope * self.slope + Decimal(1)))} * {(p0.y + p0.x / self.slope - self.intercept)} = {(self.slope / (self.slope * self.slope + Decimal(1))) * (p0.y + p0.x / self.slope - self.intercept)}")
        x = (self.slope / (self.slope * self.slope + Decimal("1"))) * (p0.y + p0.x / self.slope - self.intercept)
        # logger.debug(f"{self.slope} * {x} = {self.slope * x}")
        # logger.debug(f"{self.slope * x}  + {self.intercept} = {self.slope * x + self.intercept}")
        y = self.slope * x + self.intercept
        return Point(x, y)  # todo line also?

    def folded_point(self, p0: Point) -> Point:
        """
        The intersection point of a line running through p0 perpendicular to this line.

        The point that p0 touches if we fold the plane along this line.

        Return the point that is equidistant from this line on the other side.

        see https://math.stackexchange.com/a/2325304

        :param p0:
        :return:
        """
        if self.contains_point(p0):
            return p0
        p_int = self.perpendicular_intersection_point(p0)
        # logger.debug(f"{Decimal(2)} * {p_int.x} = {Decimal(2) * p_int.x}")
        # logger.debug(f"{Decimal(2) * p_int.x} - {p0.x} = {Decimal(2) * p_int.x - p0.x}")
        # "You shouldn't trust a difference between two numbers, unless it is bigger than the mantissa [Double precision floats: (a - b) / b >= ~4e-16]"
        return Point((Decimal("2") * p_int.x -  p0.x), (Decimal("2") * p_int.y - p0.y))
#        return Point(Decimal(2) * p_int.x - p0.x, Decimal(2) * p_int.y - p0.y)

    def contains_point(self, p0: Point) -> bool:
        return p0.y == (p0.x * self.slope) + self.intercept


class BisectionPoint(Point):
    def __init__(self, p0: Point, p1: Point):
        super().__init__((p1.x - p0.x) / Decimal("2.0") + p0.x,
                         (p1.y - p0.y) / Decimal("2.0") + p0.y)
        self.p0 = p0
        self.p1 = p1

    def __repr__(self):
        return f"{super().__repr__()}[{self.p0},{self.p1}]"


class SymmetryLineFinder:
    def __init__(self, points: List[Point]):
        if len(points) <= 2:
            raise ValueError("Cannot create symmetry lines for <3 points")
        self.points = list(set(points))  # Remove duplicates

    def _centroid(self) -> Point:
        # TODO cache
        return Point(sum([p.x for p in self.points]) / len(self.points),
                     sum([p.y for p in self.points]) / len(self.points))

    def _candidate_symmetry_lines(self) -> Iterator[Line]:
        """
        Return a list of candidate symmetry lines for a group of points
        :param points:
        :return:
        """
        if len(self.points) < 3:
            return

        # Lines of symmetry must pass thru _centroid
        cent = self._centroid()

        # don't bother re-evaluating lines we have seen before
        visited = set()
        # visited=
        for i0 in range(0, len(self.points) - 1):
            for i1 in range(i0 + 1, len(self.points)):
                b = BisectionPoint(self.points[i0], self.points[i1])
                logger.debug(f"bisection point between {i0}.{self.points[i0]} and {i1}.{self.points[i1]} is {b}")
                line1 = Line.from_points(cent, b)
                if line1 not in visited:
                    logger.debug(
                        f"Returning line between centroid {cent} and bisection point {line1} ({hash(line1)})")
                    visited.add(line1)
                    yield line1

        for i0 in range(0, len(self.points)):
            line1 = Line.from_points(cent, self.points[i0])
            if line1 not in visited:
                logger.debug(
                    f"Returning line between centroid {cent} and vertex {i0}.{self.points[i0]} {line1} ({hash(line1)})")
                visited.add(line1)
                yield line1

    def find_all(self) -> Iterator[tuple[bool, Line]]:
        for line in self._candidate_symmetry_lines():
            yield line.is_symmetry_line(self.points), line

    def find(self) -> Iterator[Line]:
        for is_symmetry, line in self.find_all():
            if is_symmetry:
                yield line
