import argparse
from upseto import manifest
from upseto import gitwrapper
from upseto import fulfiller
from upseto import checkfulfilled
from upseto import recursivegit
import os
import logging
import sys

logging.basicConfig(level=logging.INFO)


def main():
    commandLine = sys.argv[1:]
    gitArgs = []
    if 'git' in commandLine:
        gitArgs = commandLine[commandLine.index('git') + 1:]
        commandLine = commandLine[:commandLine.index('git') + 1]
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd")
    addRequirement = subparsers.add_parser(
        "addRequirement",
        help="Name of the directory of the project, in the parent directory."
        " The current HEAD revision will be used as the requirement hash")
    addRequirement.add_argument("project", nargs="+")
    addRequirement.add_argument(
        "--dirtyParadoxResolution", nargs='+', default=[],
        help="space sparated list of project basenames (not a single argument). "
        "If a project has two different hashes in the recursive requirement "
        "tree, force the hash from the current manifest. Projects that add this "
        "to their manifests become inheritnly dirty, and even project that will "
        "use this hash later on. All these flags will be cleared on the next "
        "'addRequirement', unless it is repeated (even when adding different "
        "projects)")
    delRequirement = subparsers.add_parser(
        "delRequirement",
        help="Remove a requirement from the manifest file, by project name")
    delRequirement.add_argument("project")
    fulfillRequirements = subparsers.add_parser(
        "fulfillRequirements",
        help="Checkout the exact versions of all requirements, recursively."
        " Note that if you have patches this depends on the behavior "
        "of git checkout in the apropriate cases, including possible "
        "failures")
    checkRequirements = subparsers.add_parser(
        "checkRequirements",
        help="Check that the HEAD revision of all dependencies, recursivly, "
        "matches the recursive requirements. Note that this does not "
        "check dirtyness of the working directories.")
    checkRequirements.add_argument(
        "--show", action="store_true",
        help="show all the dependencies, recursively")
    checkRequirements.add_argument(
        "--gitClean", action="store_true",
        help="fail if not all dependencies are 'git status' clean")
    checkRequirements.add_argument(
        "--unsullied", action="store_true",
        help="fail if workspace contains other files not under "
        "upseto recursive dependency tree")
    checkRequirements.add_argument(
        "--allowNoManifest", action="store_true",
        help="if this project does not contain an upseto.manifest file "
        "consider as if it has an empty one. Allows checking gitClean "
        "and unsullied uniformly in projects")
    git = subparsers.add_parser(
        "git",
        help="Run a git command recursively on all dependencies. E.g., "
        "'upseto git status -s' will show status of all dependant "
        "projects")
    args = parser.parse_args(commandLine)
    
    baseDir = ".."
    if args.cmd == "addRequirement":
        mani = manifest.Manifest.fromLocalDirOrNew()
        for project in args.project:
            projectDirectory = os.path.join(baseDir, project)
            git = gitwrapper.GitWrapper(projectDirectory)
            mani.addRequirement(originURL=git.originURL(), hash=git.hash())
            logging.info("Adding the origin URL '%(originURL)s' at hash '%(hash)s' as a requirement", dict(
                originURL=git.originURL(), hash=git.hash()))
        mani.clearAllDirtyParadoxResolution()
        for dirtyParadoxResolution in args.dirtyParadoxResolution:
            mani.setDirtyParadoxResolution(dirtyParadoxResolution)
        check = checkfulfilled.CheckFulfilled(baseDir)
        check.check(mani)
        mani.save()
        logging.info("Requirements successfully added")
    elif args.cmd == "delRequirement":
        mani = manifest.Manifest.fromLocalDir()
        originURL = mani.delRequirementByBasename(args.project)
        mani.save()
        logging.info("Removed the origin URL '%s' from requirements", originURL)
    elif args.cmd == "fulfillRequirements":
        mani = manifest.Manifest.fromLocalDir()
        ff = fulfiller.Fulfiller(mani, baseDir)
        logging.info("Requirements Fulfilled")
    elif args.cmd == "checkRequirements":
        if args.allowNoManifest:
            mani = manifest.Manifest.fromLocalDirOrNew()
        else:
            mani = manifest.Manifest.fromLocalDir()
        check = checkfulfilled.CheckFulfilled(baseDir, gitClean=args.gitClean)
        check.check(mani)
        if args.unsullied:
            check.unsullied()
        logging.info("Requirements Checked")
        if args.show:
            logging.info("\n%s", check.renderAsTreeText())
    elif args.cmd == "git":
        mani = manifest.Manifest.fromLocalDir()
        recursiveGit = recursivegit.RecursiveGit(baseDir)
        recursiveGit.run(mani, gitArgs)
    else:
        assert False, "command mismatch"


if __name__ == '__main__':
    main()
