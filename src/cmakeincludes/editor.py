
class TextFile:
    def __init__(self, what):
        if isinstance(what, TextFile):
            self.name = what.name
            self.content = what.content[:]
        else:
            with open(what) as f:
                self.name = what
                self.content = [''] + list(f)

    @property
    def lines(self):
        return self.content[1:]

    def with_changes(self, changes):
        final = self.__class__(self)
        for change in reversed(sorted(changes, key=lambda c: c.where)):
            old_slice = slice(change.where, change.where + len(change.old))
            new_slice = slice(change.where, change.where)
            del final.content[old_slice]
            final.content[new_slice] = change.new
        return final

class TextChange:
    def __init__(self, where, old, new):
        self.where = where
        self.old = old
        self.new = new

    def __repr__(self):
        old = "".join("- " + x for x in self.old)
        new = "".join("+ " + x for x in self.new)
        return f"===\n@{self.where}\n{old}{new}"

class CMakeEditor:
    def __init__(self, verbose=True):
        self.verbose = verbose

    def edit(self, analysis):
        source = TextFile(analysis.hdr.cmakefile.fn)
        changes = []
        for thing in analysis.hdr.all_things():
            start = thing.node.line
            end = thing.node.arguments[-1].line
            close = ')'
            if not source.content[end].strip().endswith(close):
                close = ''
            first_old = source.content[start]
            leading_ws = first_old[:-len(first_old.lstrip())]
            new = thing.format_thing(close=close,
                                     verbose=self.verbose)
            new[0] = leading_ws + new[0]
            changes.append(TextChange(where=start,
                                      old=source.content[start:end+1],
                                      new=new))

        return source, changes

    def patch(self, analysis):
        source, changes = self.edit(analysis)
        return source, source.with_changes(changes)

