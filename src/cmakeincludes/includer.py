import cmakeast

from . import hdr


class CMakeAnalysis:
    def __init__(self, *, cmakefile):
        self.hdr = hdr.HeaderIncluder(cmakefile)

    def _function_call(self, node_name, node, depth):
        handler_name = f"analyze_{node.name}"
        print(node.name, depth, node.arguments)
        handler = getattr(self, handler_name, None)
        if handler is not None:
            handler(node, depth)

    def analyze_add_subdirectory(self, node, depth):
        self.hdr.add_subdirectory(node.arguments[0].contents)

    def analyze_add_library(self, node, depth):
        self.hdr.add_library(lib=node.arguments[0].contents,
                             srcs=[x.contents for x in node.arguments[1:]],
                             node=node)

    def analyze_add_executable(self, node, depth):
        self.hdr.add_executable(exe=node.arguments[0].contents,
                                srcs=[x.contents for x in node.arguments[1:]],
                                node=node)


class CMakeAnalyzer:
    def __init__(self, CMakeAnalysis=CMakeAnalysis):
        self.CMakeAnalysis = CMakeAnalysis

    def analyze(self, *, cmakefile):
        a = self.CMakeAnalysis(cmakefile=cmakefile)
        cmakeast.ast_visitor.recurse(cmakefile.ast,
                                     function_call=a._function_call)
        return a
