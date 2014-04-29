import tempfile
from upseto import run


class Graph:
    def __init__(self):
        self._arcs = {}
        self._labels = {}

    def saveDot(self, filename):
        with open(filename, "w") as f:
            f.write(self._dotContents())

    def savePng(self, filename):
        assert filename.endswith(".png")
        dot = tempfile.NamedTemporaryFile(suffix=".dot")
        dot.write(self._dotContents())
        dot.flush()
        run.run(["dot", dot.name, "-Tpng", "-o", filename])

    def addArc(self, source, dest):
        self._arcs.setdefault(source, list()).append(dest)

    def label(self, node, text):
        self._labels[node] = text

    def _dotContents(self):
        result = ["digraph G {"]
        for source, arcs in self._arcs.iteritems():
            for dest in arcs:
                result.append('"%s" -> "%s";' % (source, dest))
        for node, label in self._labels.iteritems():
            result.append('"%s" [ label="%s" ];' % (node, label))
        result.append("}")
        return "\n".join(result)

    def _digraphSource(self):
        withoutIncomingArcs = set(self._arcs.keys()) | set(self._labels.keys())
        for froms, dests in self._arcs.iteritems():
            for d in dests:
                withoutIncomingArcs.discard(d)
        assert len(withoutIncomingArcs) == 1
        return withoutIncomingArcs.pop()

    def renderAsTreeText(self, indentation="    "):
        result = self._treeIterate(self._digraphSource(), 0)
        return "\n".join(indentation * l[1] + l[0] for l in result)

    def _treeIterate(self, node, depth):
        label = self._labels.get(node, node).replace("\n", "\t")
        result = [(label, depth)]
        for dest in self._arcs.get(node, []):
            result += self._treeIterate(dest, depth + 1)
        return result


if __name__ == "__main__":
    g = Graph()
    g.addArc("here", "there")
    g.addArc("there", "back again")
    g.label("back again", "first line\nsecond line")
    g.savePng("/tmp/t.png")
