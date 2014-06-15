from upseto import gitwrapper
from upseto import avoidparadox
from upseto import graph
from upseto import traverse
import os


class CheckFulfilled:
    def __init__(self, baseDir="..", gitClean=False):
        self._baseDir = baseDir
        self._gitClean = gitClean
        self._basenames = set()
        self._avoidParadox = avoidparadox.AvoidParadox()
        self._traverse = traverse.Traverse(baseDir)
        self._graph = graph.Graph()

    def check(self, mani):
        if self._gitClean:
            git = gitwrapper.GitWrapper.existing(mani.originURL(), self._baseDir)
            if git.shortStatus().strip() != "":
                raise Exception(
                    "project '%s' is not clean: git status -s returned:\n%s" % (
                        git.directory(), git.shortStatus()))
        self._basenames.add(mani.originURLBasename())
        self._avoidParadox.process(mani)
        self._graph.label(mani.originURL(), mani.originURL())
        for dependency in self._traverse.traverse(mani):
            git = gitwrapper.GitWrapper.existing(dependency.requirement['originURL'], self._baseDir)
            if git.hash() != dependency.requirement['hash']:
                raise Exception(
                    "project '%s' is not as hash '%s'" % (
                        git.directory(), dependency.requirement['hash']))
            if self._gitClean and git.shortStatus().strip() != "":
                raise Exception(
                    "project '%s' is not clean: git status -s returned:\n%s" % (
                        git.directory(), git.shortStatus()))
            self._basenames.add(dependency.basename)
            self._graph.addArc(dependency.parentOriginURL, dependency.requirement['originURL'])
            self._graph.label(
                dependency.requirement['originURL'], "%(originURL)s\n%(hash)s" % dependency.requirement)
            if dependency.manifest is not None:
                self._avoidParadox.process(dependency.manifest)

    def unsullied(self):
        directoriesInWorkspace = os.listdir(self._baseDir)
        sullied = set(directoriesInWorkspace) - self._basenames
        if len(sullied) > 0:
            raise Exception(
                "Workspace is sullied: following projects exist that are not "
                "referred by upseto dependencies: %s" % sullied)

    def savePng(self, filename):
        self._graph.savePng(filename)

    def renderAsTreeText(self):
        return self._graph.renderAsTreeText()
