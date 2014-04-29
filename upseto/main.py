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
addRequirement.add_argument("project")
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
checkRequirements.add_argument("--show", action="store_true")
git = subparsers.add_parser(
    "git",
    help="Run a git command recursively on all dependencies. E.g., "
    "'upseto git status -s' will show status of all dependant "
    "projects")
args = parser.parse_args(commandLine)

baseDir = ".."
if args.cmd == "addRequirement":
    mani = manifest.Manifest.fromLocalDirOrNew()
    projectDirectory = os.path.join(baseDir, args.project)
    git = gitwrapper.GitWrapper(projectDirectory)
    mani.addRequirement(originURL=git.originURL(), hash=git.hash())
    check = checkfulfilled.CheckFulfilled(baseDir)
    check.check(mani)
    mani.save()
    logging.info("Added the origin URL '%(originURL)s' at hash '%(hash)s' as a requirement", dict(
        originURL=git.originURL(), hash=git.hash()))
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
    mani = manifest.Manifest.fromLocalDir()
    check = checkfulfilled.CheckFulfilled(baseDir)
    check.check(mani)
    logging.info("Requirements Checked")
    if args.show:
        logging.info("\n%s", check.renderAsTreeText())
elif args.cmd == "git":
    mani = manifest.Manifest.fromLocalDir()
    recursiveGit = recursivegit.RecursiveGit(baseDir)
    recursiveGit.run(mani, gitArgs)
else:
    assert False, "command mismatch"
