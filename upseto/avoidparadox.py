from upseto import gitwrapper


class AvoidParadox:
    def __init__(self):
        self._allHashes = {}
        self._allBasenames = {}
        self._graph = {}

    def process(self, manifest):
        self._testBasenameConsistency(manifest.originURL())
        for requirement in manifest.requirements():
            self._testCollisionInDependencies(requirement, manifest)
            self._testBasenameConsistency(requirement['originURL'])
            self._graph.setdefault(manifest.originURL(), list()).append(requirement['originURL'])
        self._testNoCircles(manifest.originURL())

    def _testCollisionInDependencies(self, requirement, mani):
        if requirement['originURL'] not in self._allHashes:
            self._allHashes[requirement['originURL']] = dict(hash=requirement['hash'], manifest=mani)
        else:
            if requirement['hash'] != self._allHashes[requirement['originURL']]['hash']:
                raise Exception(
                    "Requirement hash paradox: '%s' need hash '%s' by '%s' and hash '%s' by '%s'" % (
                        requirement['originURL'], requirement['hash'], mani.originURL(),
                        self._allHashes[requirement['originURL']]['hash'],
                        self._allHashes[requirement['originURL']]['manifest'].originURL()))

    def _testBasenameConsistency(self, originURL):
        basename = gitwrapper.originURLBasename(originURL)
        if basename in self._allBasenames:
            if originURL != self._allBasenames[originURL]:
                raise Exception(
                    "Both requirements '%s' and '%s' have the same basename" % (
                        originURL, self._allBasenames[originURL]))

    def _testNoCircles(self, originURL):
        visited = set()
        stack = [originURL]
        while len(stack) > 0:
            top = stack[-1]
            for node in self._graph.get(top, []):
                if node in stack:
                    raise Exception(
                        'Dependency circle found:\n ' + " ->\n ".join(stack[stack.index(node):]))
                if node not in visited:
                    visited.add(node)
                    stack.append(node)
                    break
            else:
                stack.pop()
