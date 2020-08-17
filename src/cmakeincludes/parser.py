import cmakeast


class CMakeParser:
    def parse(self, fn):
        with open(fn) as f:
            contents = f.read()
            ast = cmakeast.ast.parse(contents)
            return self.new_CMakeFile(fn=fn, ast=ast)

    @classmethod
    def new_CMakeFile(cls, *, fn, ast, **kwargs):
        return CMakeFile(fn=fn, ast=ast, **kwargs)


class CMakeFile:
    def __init__(self, *, fn, ast):
        self.fn = fn
        self.ast = ast

    @property
    def cwd(self):
        return self.fn.resolve().parent

    def __str__(self):
        return f"CMakeFile({self.fn})"
