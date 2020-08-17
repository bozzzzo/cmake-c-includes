# cmake-c-includes

Add header files to `add_library` calls

```
Usage:
  cmake-c-includes [diff] [options] [<file>]
  cmake-c-includes patch [options] [<file>]

Options:
  -h --help     Show this help
  -v --verbose  Add comments which file caused addition of the header
  -n --dry-run  Do not change any files, write new content to stdout

Commands:
  diff     Show unified diff of changes to be made
  patch    Change the <file> to the new
```

Process `<file>` [default: `CMakeLists.txt`] and identify headers that are not
added to `add_library` commands. This is totally naive, does not support
generator or vars, just plain source files listed directly to `add_library`
commands.

Also, assume that headers from `add_subdirectory` folders are not to be added.
