import logging
from upseto import gitwrapper
from upseto import avoidparadox
from upseto import manifest


class Fulfiller:
    def __init__(self, rootManifest, basedir=".."):
        self._rootManifest = rootManifest
        self._basedir = basedir
        self._avoidParadox = avoidparadox.AvoidParadox()
        self._fulfulled = set()
        self._fulfill(rootManifest)

    def _fulfill(self, mani):
        if mani.originURL() in self._fulfulled:
            return
        self._fulfulled.add(mani.originURL())
        self._avoidParadox.process(mani)
        for requirement in mani.requirements():
            existance, git = self._existingOrClone(requirement['originURL'])
            revision = self._checkoutExactHash(git, requirement['hash'])
            logging.info("%s '%s' %s" % (existance, git.directory(), revision))
            if manifest.Manifest.exists(git.directory()):
                submanifest = manifest.Manifest.fromDir(git.directory())
                self._fulfill(submanifest)

    def _existingOrClone(self, originURL):
        try:
            git = gitwrapper.GitWrapper.existing(originURL, self._basedir)
            return "Found", git
        except:
            git = gitwrapper.GitWrapper.clone(originURL, self._basedir)
            return "Cloned", git

    def _checkoutExactHash(self, git, hash):
        if git.hash() != 'hash':
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
