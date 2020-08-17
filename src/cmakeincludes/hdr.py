import itertools

VERBOSE = False


def sortkey(s):
    s = s.strip()
    if s.startswith('#'):
        s = s[1:].strip()
    return s


class Thing:
    def __init__(self, lib, srcs, node):
        self.name = lib
        self.srcs = srcs
        self.indirect = dict()

    @classmethod
    def add_thing(cls, lib, srcs, node):
        if isinstance(srcs, str):
            srcs = srcs.splitlines()
        obj = cls(lib, dict((s.split('#', 1) + [''])[:2]
                            for s in sorted(srcs, key=sortkey)),
                  node)
        return obj

    def print_add(self):
        sep = '\n'
        items = sep.join(
            sorted((f"{k.rstrip():30} # {v}" if v.strip() and k.strip() else
                    f"{k}#{v}" if v.strip() else
                    f"{k}"
                    for k, v in itertools.chain(self.srcs.items(),
                                                self.indirect.items())),
                   key=sortkey))
        print(f"\n{self.ADD_WHAT}({self.name}\n{items}\n)\n")


class Library(Thing):
    ADD_WHAT = "add_library"


class Executable(Thing):
    ADD_WHAT = "add_executable"


Nowhere = Thing('???', [], None)


def is_include_line(line):
    return line.startswith('#') and line[1:].lstrip().startswith('include')


class FsCache:
    def __init__(self, cwd):
        self.f = {}
        self.cwd = cwd

    def get(self, f):
        # remember just what gets included
        if f not in self.f:
            with open(self.cwd.joinpath(f)) as fd:
                self.f[f] = set(line.partition('include')[2].strip()
                                for line in fd.readlines()
                                if is_include_line(line))
        return self.f[f]


class HeaderIncluder:
    def __init__(self, cmakefile):
        self.cmakefile = cmakefile
        self.excluded_dirs = []
        self.ALL = dict()
        self.include_cache = FsCache(cwd=cmakefile.cwd)

    def add_subdirectory(self, d):
        self.excluded_dirs.append(f"{d}/")

    def is_not_excluded(self, p):
        return not any(map(p.startswith, self.excluded_dirs))

    def find_name(self, pattern):
        cwd = self.cmakefile.cwd
        for full_name in sorted(cwd.rglob(pattern)):
            name = str(full_name.relative_to(cwd))
            if self.is_not_excluded(name):
                yield name

    def add_executable(self, *, exe, srcs, node):
        self.ALL[exe] = Executable.add_thing(exe, srcs, node)

    def add_library(self, *, lib, srcs, node):
        self.ALL[lib] = Library.add_thing(lib, srcs, node)

    def all_values(self, cls):
        return (v for v in self.ALL.values() if isinstance(v, cls))

    def includes(self, f, o):
        inc1 = f'"{f}"'
        # assume srcdir is in include path
        inc2 = f'<{f}>'
        # ensure we first look if same name .cpp includes the .h
        cpp = f.replace('.h', '.cpp').strip()

        def prefer_cpp(s):
            return sortkey(s) != cpp

        for on in itertools.chain(sorted(o.srcs, key=prefer_cpp), o.indirect):
            n = on.strip()
            if not n:
                continue
            full_includes = set([inc1, inc2])
            possible_includes = set(full_includes)
            parts = n.split('/')
            # check for relative includes, too
            for i in range(1, len(parts)):
                common_prefix = "/".join(parts[:i]) + "/"
                if f.startswith(common_prefix):
                    relative_include = f[len(common_prefix):]
                    possible_includes.add(f'"{relative_include}"')
            included_files = self.include_cache.get(n)
            inc = possible_includes.intersection(included_files)
            if inc:
                if VERBOSE:
                    if full_includes.intersection(included_files):
                        method = ""
                    else:
                        method = "relative "
                    inc = list(inc)[0]
                    print(f"# Indirect {o.name} {n} includes {f} as {method}{inc}")
                return on
        return None

    def claim_once(self, o, unclaimed_headers):
        ret = {}
        for u in unclaimed_headers:
            f = self.includes(u, o)
            if f is None:
                continue
            ret[u] = f
        return ret

    def claim(self, o, unclaimed_headers):
        indirect = self.claim_once(o, unclaimed_headers)
        while indirect:
            # pre-format indirect includes so that comments format properly
            o.indirect.update({f"\t{k}": v for k, v in indirect.items()})
            unclaimed_headers = unclaimed_headers.difference(indirect)
            indirect = self.claim_once(o, unclaimed_headers)
        return unclaimed_headers

    def check_cmake(self):
        all_headers = {k: Nowhere for k in self.find_name('*.h')}
        all_sources = {k: Nowhere for k in self.find_name('*.cpp')}

        def track_owner(path_owners, path, owner):
            old = path_owners.get(path)
            if old is None:
                pass             # not on the list
            elif old is Nowhere:
                path_owners[path] = owner
            else:
                print(f"# ERROR Path {path} claimed by {owner.name} is already claimed by {old.name}")

        for lib in self.all_values(Thing):
            for src in lib.srcs:
                pth = src.strip()
                old = all_headers.get(pth)
                del old
                track_owner(all_headers, pth, lib)
                track_owner(all_sources, pth, lib)

        unclaimed_headers = set(h for h, o in all_headers.items() if o is Nowhere)
        unclaimed_sources = set(h for h, o in all_sources.items() if o is Nowhere)

        # TODO: check all headers if they belong to the correct library

        for owner in self.all_values(Thing):
            unclaimed_headers = self.claim(owner, unclaimed_headers)

        for thing in self.all_values(Thing):
            thing.print_add()

        print(f"# Unclaimed headers: {unclaimed_headers}")
        print(f"# Unclaimed sources: {unclaimed_sources}")
