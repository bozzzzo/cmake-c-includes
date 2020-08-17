"""Add header files to add_library calls

Usage:
  cmake-c-includes [options] [FILE]

Options:
  -h --help     Show this help
  -p --patch    Patch the FILE
  -d --diff     Show the diff


Process FILE [default: CMakeLists.txt] and identify headers that are not added
to add_library commands. This is totally naive, does not support generator or
vars, just plain source files listed directly to add_library commands.

Also, assume that headers from add_subdirectory() folders are not to be added.

"""

import pathlib

from docopt import docopt

from . import parser
from . import includer


def main():
    args = docopt(__doc__, version="0.1")
    print(args)

    FILE = pathlib.Path(args["FILE"] or "CMakeLists.txt")

    p = parser.CMakeParser()
    c = p.parse(FILE)

    a = includer.CMakeAnalyzer()

    r = a.analyze(cmakefile=c)

    r.hdr.check_cmake()

    print(c, r)
