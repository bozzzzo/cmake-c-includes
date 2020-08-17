"""Add header files to add_library calls

Usage:
  cmake-c-includes [diff] [options] [<file>]
  cmake-c-includes patch [options] [<file>]

Options:
  -h --help     Show this help.
  -v --verbose  Add comments which file caused addition of the header.
  -n --dry-run  Do not change any files, write new content to stdout.

Commands:
  diff     Show unified diff of changes to be made.
  patch    Change the <file> to the new state.

Process <file> [default: CMakeLists.txt] and identify headers that are not
added to add_library commands. This is totally naive, does not support
generator or vars, just plain source files listed directly to add_library
commands.

Also, assume that headers from add_subdirectory() folders are not to be added.

"""

import pathlib

from docopt import docopt

from . import parser
from . import includer
from . import editor


def main():
    args = docopt(__doc__, version="0.1")
 
    fn = pathlib.Path(args["<file>"] or "CMakeLists.txt")

    p = parser.CMakeParser()
    c = p.parse(fn)
    a = includer.CMakeAnalyzer()
    r = a.analyze(cmakefile=c)
    e = editor.CMakeEditor(verbose=args['--verbose'])
    a, p = e.edit(r)
    b = a.with_changes(p)

    command = ([arg for arg, v in args.items()
                if arg[0] not in '<-' and v]
               + ['diff'])[0]
    if command == 'diff':
        import difflib
        d = difflib.unified_diff(a.lines, b.lines, str(a.name), str(b.name))
        print("".join(d))
    elif command == 'patch':
        content = "".join(b.lines)
        if args['--dry-run']:
            print(content)
        else:
            with open(b.name, "wt") as f:
                f.write(content)

