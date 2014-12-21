import argparse
import modulefinder
import zipfile
import sys
import os
import glob
from upseto import tipoffmodulefinder

DIRECTORIES_CONTAINING_PYTHON_STANDARD_LIBRARIES = [
    "/usr/lib/",
    "/usr/lib64/",
    "/usr/local/lib/",
    "/usr/local/lib64/",
]


class PackEgg:
    def __init__(self, args):
        self._args = args
        if args.entryPoint == [] and args.directory == []:
            raise Exception("At least one of --entryPoint or --directory must be specified")
        if args.joinPythonNamespaces:
            os.environ['UPSETO_JOIN_PYTHON_NAMESPACES'] = 'yes'
            tipoffmodulefinder.TipOffModuleFinder()

    def pack(self):
        deps = _Deps(self._args.output)
        zip = zipfile.ZipFile(self._args.output, "w")
        try:
            for entryPoint in self._args.entryPoint:
                self._pack(zip, entryPoint, deps)
            for directory in self._args.directory:
                for filename in glob.glob(os.path.join(directory, "*.py")):
                    if filename.endswith("__init__.py"):
                        continue
                    self._pack(zip, filename, deps)
            zip.close()
            if self._args.createDeps:
                deps.write(self._args.createDeps)
        except:
            os.unlink(self._args.output)
            raise

    @classmethod
    def addArgumentParserParameters(cls, parser):
        parser.add_argument(
            "--entryPoint", nargs='*', default=[], help="Entry points to pack")
        parser.add_argument(
            "--directory", nargs='*', default=[], help="Directories to pack")
        parser.add_argument("--output", required=True, help="output egg file")
        parser.add_argument("--createDeps", help="create .dep file")
        parser.add_argument(
            "--takeEverything", action='store_true', default=False,
            help="take dependency files from /usr, site-packages, whereever")
        parser.add_argument(
            "--takeSitePackages", action='store_true', default=False,
            help="take dependency files from site-packages")
        parser.add_argument(
            "--takeSitePackage", nargs="*", default=[],
            help="take dependecy from a specific namespace in site-packages")
        parser.add_argument(
            "--compile_pyc", action="store_true", help="compile and pack .pyc files into egg")
        parser.add_argument(
            "--compile_pyo", action="store_true", help="compile and pack .pyo files into egg")
        parser.add_argument(
            "--joinPythonNamespaces", action="store_true",
            help="collect files from joined namespaces. Only works when "
            "invoked from an upseto project directory")

    def _pack(self, zip, script, deps):
        moduleFinder = modulefinder.ModuleFinder()
        moduleFinder.run_script(script)
        deps.add(script)
        zip.write(script, self._pathRelativeToPythonPath(script))
        for module in moduleFinder.modules.itervalues():
            if not self._packModule(module):
                continue
            relpath = self._pathRelativeToPythonPath(module.__file__)
            if relpath not in zip.namelist():
                if tipoffmodulefinder.fileIsUpsetoPythonNamespaceJoinInit(module.__file__):
                    zip.writestr(relpath, "")
                else:
                    zip.write(module.__file__, relpath)
                deps.add(module.__file__)

    def _packModule(self, module):
        if module.__name__ == "__main__":
            return False
        if module.__file__ is None:
            return False
        if self._args.takeEverything:
            return True
        if 'site-packages' in module.__file__:
            for sitePackage in self._args.takeSitePackage:
                path = os.path.join('site-packages', * sitePackage.split("."))
                if path in module.__file__:
                    return True
            return self._args.takeSitePackages
        if any([module.__file__.startswith(excludedDir)
               for excludedDir in DIRECTORIES_CONTAINING_PYTHON_STANDARD_LIBRARIES]):
            return False
        return True

    def _candidatesPathRelativeToPythonPath(self, filename):
        absoluteFilename = os.path.abspath(filename)
        for path in sys.path:
            absolutePath = os.path.abspath(path)
            if absoluteFilename.startswith(absolutePath):
                yield absoluteFilename[len(absolutePath):].strip(os.sep)

    def _candidatesPathRelativeToPackagesPaths(self, filename):
        absoluteFilename = os.path.abspath(filename)
        for packageName, paths in modulefinder.packagePathMap.iteritems():
            for path in paths:
                absolutePath = os.path.abspath(path)
                if absoluteFilename.startswith(absolutePath):
                    relative = absoluteFilename[len(absolutePath):].strip(os.sep)
                    yield os.path.join(*(packageName.split(".") + [relative]))

    def _pathRelativeToPythonPath(self, filename):
        candidates = list(self._candidatesPathRelativeToPythonPath(filename)) + \
            list(self._candidatesPathRelativeToPackagesPaths(filename))
        if candidates == []:
            raise Exception("Filename '%s' not in sys.path or packages path" % filename)
        shortest = min(candidates, key=lambda x: len(x))
        return shortest


class _Deps:
    def __init__(self, target):
        self._target = target
        self._dependencies = []

    def add(self, dependency):
        self._dependencies.append(dependency)

    def write(self, filename):
        with open(filename, "w") as f:
            f.write("%s: \\\n" % self._target)
            for dependency in self._dependencies:
                f.write("\t%s \\\n" % dependency)
            f.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    PackEgg.addArgumentParserParameters(parser)
    args = parser.parse_args()
    PackEgg(args).pack()
