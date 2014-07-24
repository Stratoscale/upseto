import os
import sys
from upseto import manifest
from upseto import traverse


def join(moduleGlobals):
    if 'UPSETO_JOIN_PYTHON_NAMESPACES' not in os.environ:
        return []
    joiner = Joiner(moduleGlobals['__file__'], moduleGlobals['__name__'])
    return joiner.found()


def extendPath():
    if 'UPSETO_JOIN_PYTHON_NAMESPACES' not in os.environ:
        return
    finder = PathFinder()
    sys.path.extend(finder.found())


class Joiner:
    def __init__(self, invokingModulePath, invokingModuleName):
        self._lookingFor = os.path.join(*(invokingModuleName.split('.') + ['__init__.py']))
        self._found = []
        self._projectDir = None
        self._baseDir = None
        self._findManifestFile(invokingModulePath)
        if self._projectDir is None:
            return
        self._traverse = traverse.Traverse(self._baseDir)
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
                self._projectDir = asString
                self._baseDir = basedir
                return
            dirs.pop()

    def _lookInProjectDir(self, projectDir):
        candidate1 = os.path.join(projectDir, self._lookingFor)
        if os.path.isfile(candidate1):
            self._found.append(os.path.dirname(candidate1))
        candidate2 = os.path.join(projectDir, 'py', self._lookingFor)
        if os.path.isfile(candidate2):
            self._found.append(os.path.dirname(candidate2))


class PathFinder:
    def __init__(self):
        self._found = []
        self._projectDir = None
        self._baseDir = None
        self._findManifestFile()
        if self._projectDir is None:
            return
        self._traverse = traverse.Traverse(self._baseDir)
        mani = manifest.Manifest.fromDir(self._projectDir)
        for dependency in self._traverse.traverse(mani):
            self._lookInProjectDir(dependency.projectDir)

    def found(self):
        return self._found

    def _findManifestFile(self):
        for entry in sys.path:
            if entry != "py" and not entry.endswith(os.sep + "py"):
                continue
            path = os.path.dirname(os.path.abspath(entry))
            if not manifest.Manifest.exists(path):
                continue
            self._projectDir = path
            self._baseDir = os.path.dirname(path)
            return

    def _lookInProjectDir(self, projectDir):
        candidate = os.path.join(projectDir, 'py')
        if os.path.isdir(candidate):
            self._found.append(candidate)
