import itertools
import pathlib

VERBOSE=False

excluded_dirs = []

def add_subdirectory(d):
  excluded_dirs.append(f"{d}/")

def is_not_excluded(p):
  return not any(map(p.startswith, excluded_dirs))

def find_name(pattern):
  cwd = pathlib.Path()
  return list(sorted(map(str, cwd.rglob(pattern))))

def sortkey(s):
  s = s.strip()
  if s.startswith('#'):
    s = s[1:].strip()
  return s


class Thing:
  ALL = dict()
  def __init__(self, lib, srcs):
    self.name = lib
    self.srcs = srcs
    self.indirect = dict()

  @classmethod
  def add_thing(cls, lib, srcs):
    obj = cls(lib, dict((s.split('#',1) + [''])[:2]
                        for s in sorted(srcs.splitlines(),
                                        key=sortkey)))
    cls.ALL[lib] = obj

  @classmethod
  def all_values(cls):
    return (v for v in cls.ALL.values() if isinstance(v, cls))

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

add_library = Library.add_thing

Nowhere=Thing('???', [])

class Executable(Thing):
  ADD_WHAT = "add_executable"

add_executable = Executable.add_thing

class FsCache:
  def __init__(self):
    self.f = {}

  def get(self, f):
    # remember just what gets included
    if f not in self.f:
      with open(f) as fd:
        self.f[f] = [l.partition('include')[2].strip()
                     for l in fd.readlines()
                     if l.startswith('#') and l[1:].lstrip().startswith('include')]
    return self.f[f]

def includes(f, o, include_cache=FsCache()):
  inc1 = f'"{f}"'
  # assume srcdir is in include path
  inc2 = f'<{f}>'
  # ensure we first look if same name .cpp includes the .h
  cpp = f.replace('.h', '.cpp').strip()
  prefer_cpp = lambda s: sortkey(s) != cpp
  for on in itertools.chain(sorted(o.srcs, key=prefer_cpp), o.indirect):
    n = on.strip()
    if not n:
      continue
    possible_includes = [inc1, inc2]
    parts = n.split('/')
    # check for relative includes, too
    for i in range(1, len(parts)):
      common_prefix = "/".join(parts[:i]) + "/"
      if f.startswith(common_prefix):
        relative_include = f[len(common_prefix):]
        possible_includes.append(f'"{relative_include}"')
    included_files = include_cache.get(n)
    for inc in possible_includes:
      if inc in included_files:
        if VERBOSE:
          if inc in [inc1, inc2]:
            print(f"# Indirect {o.name} {n} includes {f} as {inc}")
          else:
            print(f"# Indirect {o.name} {n} includes {f} as relative {inc}")
        return on
  return None

def claim_once(o, unclaimed_headers):
  ret = {}
  for u in unclaimed_headers:
    f = includes(u, o)
    if f is None:
      continue
    ret[u] = f
  return ret

def claim(o, unclaimed_headers):
  indirect = claim_once(o, unclaimed_headers)
  while indirect:
    # pre-format indirect includes so that comments format properly
    o.indirect.update({f"\t{k}": v for k, v in indirect.items()})
    unclaimed_headers = unclaimed_headers.difference(indirect)
    indirect = claim_once(o, unclaimed_headers)
  return unclaimed_headers

def check_cmake():
  all_headers = {k: Nowhere for k in find_name('*.h') if is_not_excluded(k)}
  all_sources = {k: Nowhere for k in find_name('*.cpp') if is_not_excluded(k)}

  def track_owner(path_owners, path, owner):
    old = path_owners.get(path)
    if old is None:
      pass             # not on the list
    elif old is Nowhere:
      path_owners[path] = owner
    else:
      print(f"# ERROR Path {path} claimed by {owner.name} is already claimed by {old.name}")

  for lib in Thing.all_values():
    for src in lib.srcs:
      pth = src.strip()
      old = all_headers.get(pth)
      track_owner(all_headers, pth, lib)
      track_owner(all_sources, pth, lib)

  unclaimed_headers = set(h for h,o in all_headers.items() if o is Nowhere)
  unclaimed_sources = set(h for h,o in all_sources.items() if o is Nowhere)

  # TODO: check all headers if they belong to the correct library

  for owner in Thing.all_values():
    unclaimed_headers = claim(owner, unclaimed_headers)

  for thing in Thing.all_values():
    thing.print_add()

  print(f"# Unclaimed headers: {unclaimed_headers}")
  print(f"# Unclaimed sources: {unclaimed_sources}")
