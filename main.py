#!/bin/python

from symmetry import *
import argparse
import re
import matplotlib.pyplot as plt
import matplotlib.axes
from decimal import localcontext
import sys

def plot_line(subplot: matplotlib.pyplot.Axes, line: Line, x_range: tuple[float, float], y_range: tuple[float, float],
              **kwargs) -> None:
    """
    Plot a single Line object within a specified plot area

    :param subplot: The Matplotlib subplot to use
    :param line: The line to plot
    :param x_range: The X boundaries of the plot
    :param y_range: The Y boundaries of the plot
    :param kwargs: Additional arguments passed along to `matplotlib.pyplot.plot()`
    """
    if line.is_vertical():
        subplot.plot([line.x, line.x], y_range, **kwargs)
    else:
        subplot.plot(x_range,
                     [float(line.slope) * x + float(line.intercept) for x in x_range],
                     **kwargs)


def plot_symmetry_lines(points: List[Point], lines: Iterator[tuple[bool, Line]], fig: matplotlib.pyplot.Figure) -> None:
    """
    Plot symmetry lines and candidate lines.

    :param lines: Generator of tuples (bool, Line) where the first value indicates whether the line is a symmetry line.
    :param points: The original set of input points (vertices)
    :param fig: The matplotlib figure to add the plots to
    """
    subplot = fig.add_subplot()
    x_range = x_min, x_max = min([float(p.x) for p in points]), max([float(p.x) for p in points])
    y_range = y_min, y_max = min([float(p.y) for p in points]), max([float(p.y) for p in points])
    # Make the plot square
    factor = 0.05  # could make this a parameter or global
    y_factor = abs((y_min - y_max) * factor)
    x_factor = abs((x_min - x_max) * factor)
    xlim = [x_min - x_factor, x_max + x_factor]
    ylim = [y_min - y_factor, y_max + y_factor]
    subplot.set_xlim(xlim)
    subplot.set_ylim(ylim)

    for is_symmetry_line, line in lines:
        if is_symmetry_line:
            plot_line(subplot, line, x_range, y_range, color="b", zorder=2)
            print(line)
        else:
            plot_line(subplot, line, x_range, y_range, color="0.75", linestyle="dashed", zorder=1)

    subplot.scatter([float(p.x) for p in points], [float(p.y) for p in points], color="black", zorder=3)


def main():
    desc = """Find the lines of symmetry in a scatterplot.

    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--graph", help="Create a PNG with a graph representation of the points and symmetry lines")
    parser.add_argument("--log-level", "-l", help="Python log level", default="WARNING")
    parser.add_argument("--precision", "-p",
                        help="Number of digits of precision to use when comparing floating point numbers", type=int,
                        default=12)
    args = parser.parse_args()

    logger.level = getattr(logging, args.log_level)
    logger.addHandler(logging.StreamHandler(sys.stderr))

    data = re.split(r"\s", sys.stdin.read())
    # Adjust the precision for calculations.
    with localcontext() as ctx:
        ctx.prec = args.precision
        points = [Point(*[Decimal(c) for c in p.split(",")[:2]]) for p in data if p]
        fig = plt.figure()
        lines = list(SymmetryLineFinder(points).find_all())

        for line in [l for is_symmetry_line, l in lines if is_symmetry_line]:
            print(line)
        if args.graph:
            plot_symmetry_lines(points, lines, fig)
            fig.savefig(args.graph, format="png")
            import subprocess, os, platform
            try:
                if platform.system() == 'Darwin':  # macOS
                    subprocess.call(('open', args.graph))
                elif platform.system() == 'Windows':  # Windows
                    os.startfile(args.graph)
                else:  # linux variants
                    subprocess.call(('xdg-open', args.graph))
            except Exception:
                # Couldn't get the OS to open the file. Oh well - just print a reminder
                print(f"Saved plot to {args.graph}")

if __name__ == "__main__":
    main()
