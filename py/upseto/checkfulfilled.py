import logging
from upseto import gitwrapper
from upseto import avoidparadox
from upseto import manifest
from upseto import graph


class CheckFulfilled:
    def __init__(self, basedir=".."):
        self._basedir = basedir
        self._avoidParadox = avoidparadox.AvoidParadox()
        self._checked = set()
        self._graph = graph.Graph()

    def check(self, mani):
        if mani.originURL() in self._checked:
            return
        self._checked.add(mani.originURL())
        self._avoidParadox.process(mani)
        self._graph.label(mani.originURL(), mani.originURL())
        for requirement in mani.requirements():
            git = gitwrapper.GitWrapper.existing(requirement['originURL'], self._basedir)
            if git.hash() != requirement['hash']:
                raise Exception(
                    "project '%s' is not as hash '%s'" % (
                        git.directory(), requirement['hash']))
            self._graph.addArc(mani.originURL(), requirement['originURL'])
            if manifest.Manifest.exists(git.directory()):
                submanifest = manifest.Manifest.fromDir(git.directory())
                self.check(submanifest)
                self._graph.label(submanifest.originURL(), "%(originURL)s\n%(hash)s" % requirement)

    def savePng(self, filename):
        self._graph.savePng(filename)

    def renderAsTreeText(self):
        return self._graph.renderAsTreeText()
