import argparse
from upseto import manifest
from upseto import gitwrapper
from upseto import fulfiller
from upseto import checkfulfilled
import os
import logging

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="cmd")
addRequirement = subparsers.add_parser(
    "addRequirement",
    help="Name of the directory of the project, in the parent directory")
addRequirement.add_argument("project")
delRequirement = subparsers.add_parser("delRequirement")
delRequirement.add_argument("project")
fulfillRequirements = subparsers.add_parser("fulfillRequirements")
checkRequirements = subparsers.add_parser("checkRequirements")
checkRequirements.add_argument("--show", action="store_true")
args = parser.parse_args()

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
else:
    assert False, "command mismatch"

# ~/.netrc method for github auth
# http://stackoverflow.com/questions/5343068/is-there-a-way-to-skip-password-typing-when-using-https-github
