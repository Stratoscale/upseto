from upseto import gitwrapper
from upseto import avoidparadox
from upseto import graph
from upseto import traverse


class CheckFulfilled:
    def __init__(self, baseDir=".."):
        self._baseDir = baseDir
        self._avoidParadox = avoidparadox.AvoidParadox()
        self._traverse = traverse.Traverse(baseDir)
        self._graph = graph.Graph()

    def check(self, mani):
        self._avoidParadox.process(mani)
        self._graph.label(mani.originURL(), mani.originURL())
        for dependency in self._traverse.traverse(mani):
            git = gitwrapper.GitWrapper.existing(dependency.requirement['originURL'], self._baseDir)
            if git.hash() != dependency.requirement['hash']:
                raise Exception(
                    "project '%s' is not as hash '%s'" % (
                        git.directory(), dependency.requirement['hash']))
            self._graph.addArc(dependency.parentOriginURL, dependency.requirement['originURL'])
            self._graph.label(
                dependency.requirement['originURL'], "%(originURL)s\n%(hash)s" % dependency.requirement)
            if dependency.manifest is not None:
                self._avoidParadox.process(dependency.manifest)

    def savePng(self, filename):
        self._graph.savePng(filename)

    def renderAsTreeText(self):
        return self._graph.renderAsTreeText()
