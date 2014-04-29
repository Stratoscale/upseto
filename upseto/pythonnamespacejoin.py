import os
from upseto import manifest
from upseto import gitwrapper
from upseto import traverse


def join(moduleGlobals):
    if 'UPSETO_JOIN_PYTHON_NAMESPACES' not in os.environ:
        return []
    joiner = Joiner(moduleGlobals['__file__'], moduleGlobals['__name__'])
    return joiner.found()


class Joiner:
    def __init__(self, invokingModulePath, invokingModuleName):
        self._lookingFor = os.path.join(*(invokingModuleName.split('.') + ['__init__.py']))
        self._projectDir, self._baseDir = self._findManifestFile(invokingModulePath)
        self._traverse = traverse.Traverse(self._baseDir)
        self._found = []
        mani = manifest.Manifest.fromDir(self._projectDir)
        for dependency in self._traverse.traverse(mani):
            self._lookInProjectDir(dependency.projectDir)

    def found(self):
        return self._found

    def _findManifestFile(self, invokingModulePath):
        dirs = os.path.dirname(os.path.abspath(invokingModulePath)).split(os.path.sep)
        while len(dirs) > 2:
            asString = os.path.sep.join(dirs)
            if manifest.Manifest.exists(asString):
                basedir = os.path.sep.join(dirs[: -1])
                return asString, basedir
            dirs.pop()
        raise Exception(
            "Upseto manifest file was not found under any parent directory of '%s'" % invokingModulePath)

    def _lookInProjectDir(self, projectDir):
        candidate1 = os.path.join(projectDir, self._lookingFor)
        if os.path.isfile(candidate1):
            self._found.append(os.path.dirname(candidate1))
        candidate2 = os.path.join(projectDir, 'py', self._lookingFor)
        if os.path.isfile(candidate2):
            self._found.append(os.path.dirname(candidate2))
