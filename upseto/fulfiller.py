import logging
from upseto import gitwrapper
from upseto import avoidparadox
from upseto import traverse
from upseto import manifest
from upseto import dirtyparadoxresolution
from upseto import run


class Fulfiller:
    def __init__(self, rootManifest, baseDir=".."):
        self._rootManifest = rootManifest
        self._baseDir = baseDir
        self._avoidParadox = avoidparadox.AvoidParadox(baseDir)
        self._traverse = traverse.Traverse(baseDir)
        self._dirtyParadoxResolution = dirtyparadoxresolution.DirtyParadoxResolution()
        self._fulfill(rootManifest)

    def _fulfill(self, mani):
        self._dirtyParadoxResolution.process(mani)
        self._avoidParadox.process(mani)
        for dependency in self._traverse.traverse(mani):
            hashWithDirt = self._dirtyParadoxResolution.hashOverride(
                dependency.requirement, dependency.parentOriginURL)
            existance, git = gitwrapper.GitWrapper.getGit(dependency.requirement['originURL'], self._baseDir)
            revision = self._checkoutExactHash(git, hashWithDirt)
            if manifest.Manifest.exists(git.directory()):
                mani = manifest.Manifest.fromDir(git.directory())
                self._dirtyParadoxResolution.process(mani)
                self._avoidParadox.process(mani)
            logging.info("%s '%s' %s" % (existance, git.directory(), revision))

    def _checkoutExactHash(self, git, hash):
        if git.isBranch(hash):
            git.fetch()
        if git.hash() == git.hash(hash):
            return "untouched"
        if git.hash('master') == git.hash(hash):
            git.checkout('master')
            assert git.hash() == git.hash(hash)
            return "master checked out"
        else:
            git.fetch()
            git.checkout(hash)
            assert git.hash() == git.hash(hash)
            return "exact hash checked out"
