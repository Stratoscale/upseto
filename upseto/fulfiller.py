import os
import logging
from upseto import gitwrapper
from upseto import avoidparadox
from upseto import traverse
from upseto import manifest
from upseto import dirtyparadoxresolution


class Fulfiller:
    def __init__(self, rootManifest, baseDir=".."):
        self._rootManifest = rootManifest
        self._baseDir = baseDir
        self._avoidParadox = avoidparadox.AvoidParadox()
        self._traverse = traverse.Traverse(baseDir)
        self._dirtyParadoxResolution = dirtyparadoxresolution.DirtyParadoxResolution()
        self._fulfill(rootManifest)

    def _fulfill(self, mani):
        self._dirtyParadoxResolution.process(mani)
        self._avoidParadox.process(mani)
        for dependency in self._traverse.traverse(mani):
            existance, git = self._existingOrClone(dependency.requirement['originURL'])
            if manifest.Manifest.exists(git.directory()):
                mani = manifest.Manifest.fromDir(git.directory())
                self._dirtyParadoxResolution.process(mani)
                self._avoidParadox.process(mani)
            self._printDependency(dependency, existance, git)

    def _printDependency(self, dependency, existance, git):
        levelIndentation = "    " * dependency.level
        if levelIndentation:
            levelIndentation += "|-- "
        hashWithDirt = self._dirtyParadoxResolution.hashOverride(
            dependency.requirement, dependency.parentOriginURL)
        revision = self._checkoutExactHash(git, hashWithDirt)
        logging.info("%s%s: %s, %s" % (levelIndentation, os.path.basename(git.directory()), existance,
                                       revision))

    def _existingOrClone(self, originURL):
        try:
            git = gitwrapper.GitWrapper.existing(originURL, self._baseDir)
            return "Found", git
        except:
            git = gitwrapper.GitWrapper.clone(originURL, self._baseDir)
            return "Cloned", git

    def _checkoutExactHash(self, git, hash):
        if git.hash() != hash:
            if git.hash('master') == hash:
                git.checkout('master')
                assert git.hash() == hash
                return "master checked out"
            else:
                git.fetch()
                git.checkout(hash)
                assert git.hash() == hash
                return "exact hash checked out"
        else:
            return "untouched"
