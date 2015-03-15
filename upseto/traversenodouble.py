from upseto import traverse


class TraverseNoDouble:
    def __init__(self, baseDir=".."):
        self._traverse = traverse.Traverse(baseDir=baseDir)
        self._visitedProjectDirs = set()

    def traverse(self, mani):
        """
        Unlike traverse, which avoid scanning the same subtree twice,
        but does produce the same dependency on diamond cases, this
        wrapper will avoid the double even in diamond cases.
        """
        for dependency in self._traverse.traverse(mani):
            if dependency.projectDir in self._visitedProjectDirs:
                continue
            self._visitedProjectDirs.add(dependency.projectDir)
            yield dependency
