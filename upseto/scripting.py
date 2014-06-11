from upseto import gitwrapper
from upseto import traverse
from upseto import manifest
import os


def checkWorkspaceUnsullied():
    git = gitwrapper.GitWrapper('.')
    basename = git.originURLBasename()
    traversal = traverse.Traverse()
    basenames = [basename]
    for dependency in traversal.traverse(manifest.Manifest.fromLocalDirOrNew()):
        basenames.append(dependency.basename)
    directoriesInWorkspace = os.listdir("..")
    sullied = set(directoriesInWorkspace) - set(basenames)
    if len(sullied) > 0:
        raise Exception(
            "Workspace is sullied: following projects exist that are not "
            "referred by upseto dependencies: %s" % sullied)
