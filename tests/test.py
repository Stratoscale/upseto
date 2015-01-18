import upseto
import unittest
import gitwrapper
import upsetowrapper
import upseto.manifest
import upseto.gitwrapper
import os
import shutil
import tempfile
import zipfile


class Test(unittest.TestCase):
    def setUp(self):
        gitwrapper.setUp()

    def tearDown(self):
        gitwrapper.tearDown()

    class SimpleManifest_OneProjectDependsOnTwoOthers:
        def __init__(self, test):
            self.project1 = gitwrapper.GitHub("project1")
            self.project2 = gitwrapper.GitHub("project2")
            self.requiringProject = gitwrapper.GitHub("requiringProject")

            self.localClone1 = gitwrapper.LocalClone(self.project1)
            self.localClone2 = gitwrapper.LocalClone(self.project2)
            self.localRequiringProject = gitwrapper.LocalClone(self.requiringProject)
            test.assertEquals(self.project1.hash('master'), self.localClone1.hash())
            test.assertEquals(self.project2.hash('master'), self.localClone2.hash())
            test.assertEquals(self.requiringProject.hash(), self.localRequiringProject.hash())

            upsetowrapper.run(self.localRequiringProject, "addRequirement project1")
            upsetowrapper.run(self.localRequiringProject, "addRequirement project2")
            test.assertTrue(os.path.exists(self.localRequiringProject.manifestFilename()))
            self.localRequiringProject.addCommitPushManifest()

            self.manifest = upseto.manifest.Manifest.fromDir(self.localRequiringProject.directory())
            requirements = self.manifest.requirements()
            test.assertEquals(len(requirements), 2)
            test.assertEquals(requirements[0]['originURL'], "file://" + self.project1.directory())
            test.assertEquals(requirements[0]['hash'], self.project1.hash())
            test.assertEquals(requirements[1]['originURL'], "file://" + self.project2.directory())
            test.assertEquals(requirements[1]['hash'], self.project2.hash())

        def addThirdTier(self):
            self.recursiveProject = gitwrapper.GitHub("recursiveProject")
            self.localRecursiveProject = gitwrapper.LocalClone(self.recursiveProject)
            upsetowrapper.run(self.localRecursiveProject, "addRequirement requiringProject")
            self.localRecursiveProject.addCommitPushManifest()

        def addFourthTier(self):
            self.fourthTierProject = gitwrapper.GitHub('forthTier')
            self.localFourthTierProject = gitwrapper.LocalClone(self.fourthTierProject)
            upsetowrapper.run(self.localFourthTierProject, "addRequirement recursiveProject")
            self.localFourthTierProject.addCommitPushManifest()

    def test_simpleManifest_OneProjectDependsOnTwoOthers_RequirementsFetched(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)

        shutil.rmtree(gitwrapper.localClonesDir())

        localRequiringProject = gitwrapper.LocalClone(case.requiringProject)
        upsetowrapper.run(localRequiringProject, "fulfillRequirements")
        self.assertEquals(case.project1.hash('master'), case.localClone1.hash())
        self.assertEquals(case.project2.hash('master'), case.localClone2.hash())
        self.assertEquals(case.requiringProject.hash('master'), case.localRequiringProject.hash())

        upsetowrapper.run(localRequiringProject, "fulfillRequirements")  # does nothing
        self.assertEquals(case.project1.hash('master'), case.localClone1.hash())
        self.assertEquals(case.project2.hash('master'), case.localClone2.hash())
        self.assertEquals(case.requiringProject.hash('master'), case.localRequiringProject.hash())

    def test_simpleManifest_NothingToBeDone(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)

        upsetowrapper.run(case.localRequiringProject, "fulfillRequirements")
        self.assertEquals(case.project1.hash('master'), case.localClone1.hash())
        self.assertEquals(case.project2.hash('master'), case.localClone2.hash())
        self.assertEquals(case.requiringProject.hash('master'), case.localRequiringProject.hash())

    def test_checkRequirements(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)

        upsetowrapper.run(case.localRequiringProject, "checkRequirements")
        shutil.rmtree(case.localClone2.directory())
        upsetowrapper.runShouldFail(case.localRequiringProject, "checkRequirements", "exist")

    def test_simpleManifest_DetachedVersion(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)

        hashBefore = case.localClone1.hash()
        case.localClone1.createAddCommitPush('anotherfile')
        hashAfter = case.localClone1.hash()
        self.assertNotEqual(hashBefore, hashAfter)

        upsetowrapper.run(case.localRequiringProject, "fulfillRequirements")
        self.assertEquals(case.localClone1.hash(), hashBefore)
        self.assertEquals(case.project2.hash('master'), case.localClone2.hash())
        self.assertEquals(case.requiringProject.hash('master'), case.localRequiringProject.hash())

    def test_recursiveRequirements(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)
        case.addThirdTier()

        shutil.rmtree(gitwrapper.localClonesDir())
        localRecursiveProject = gitwrapper.LocalClone(case.recursiveProject)
        upsetowrapper.run(localRecursiveProject, "fulfillRequirements")
        self.assertEquals(case.requiringProject.hash('master'), case.localRequiringProject.hash())
        self.assertEquals(case.project1.hash('master'), case.localClone1.hash())
        self.assertEquals(case.project2.hash('master'), case.localClone2.hash())

    def test_recursiveRequirementDirectlyRequiresFirstLayerProject(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)
        case.addThirdTier()

        upsetowrapper.run(case.localRecursiveProject, "addRequirement project1")
        case.localRecursiveProject.addCommitPushManifest()

        shutil.rmtree(gitwrapper.localClonesDir())
        localRecursiveProject = gitwrapper.LocalClone(case.recursiveProject)
        upsetowrapper.run(localRecursiveProject, "fulfillRequirements")
        self.assertEquals(case.requiringProject.hash('master'), case.localRequiringProject.hash())
        self.assertEquals(case.project1.hash('master'), case.localClone1.hash())
        self.assertEquals(case.project2.hash('master'), case.localClone2.hash())

    def test_refusesToCreateHashInconsistency_TwoProjectPointAtSameOriginWithDifferentHashes(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)
        case.addThirdTier()

        case.localClone1.createAddCommitPush("anotherfile")
        upsetowrapper.runShouldFail(case.localRecursiveProject, "addRequirement project1", "hash paradox")
        upsetowrapper.runShouldFail(case.localRecursiveProject, "checkRequirements", "hash")
        upsetowrapper.run(case.localRecursiveProject, "fulfillRequirements")
        upsetowrapper.run(case.localRecursiveProject, "checkRequirements")
        upsetowrapper.run(case.localRecursiveProject, "addRequirement project1")

    def test_updateVersion(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)

        case.localClone1.createAddCommitPush("anotherfile")
        newHash = case.localClone1.hash()

        upsetowrapper.runShouldFail(case.localRequiringProject, "checkRequirements", "hash")
        upsetowrapper.run(case.localRequiringProject, "fulfillRequirements")
        upsetowrapper.run(case.localRequiringProject, "checkRequirements")
        self.assertNotEqual(case.localClone1.hash(), newHash)

        case.localClone1.checkout('master')
        self.assertEqual(case.localClone1.hash(), newHash)
        upsetowrapper.run(case.localRequiringProject, "addRequirement project1")
        upsetowrapper.run(case.localRequiringProject, "checkRequirements")
        self.assertEqual(case.localClone1.hash(), newHash)

    def test_circle(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)
        case.addThirdTier()

        upsetowrapper.runShouldFail(case.localClone1, "addRequirement recursiveProject", "circle")

        upsetowrapper.run(case.localRecursiveProject, "delRequirement requiringProject")
        upsetowrapper.run(case.localClone1, "addRequirement recursiveProject")
        upsetowrapper.runShouldFail(case.localRecursiveProject, "addRequirement requiringProject", "circle")

    def test_show(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)
        case.addThirdTier()
        result = upsetowrapper.run(case.localRecursiveProject, "checkRequirements --show")
        print "\nupseto checkRequirements --show"
        print result
        self.assertIn('file://%s\t%s' % (case.project1.directory(), case.project1.hash('master')), result)
        self.assertIn('file://%s\t%s' % (case.project2.directory(), case.project2.hash('master')), result)

    def pythonNamespacesTestcase(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)
        os.makedirs(case.localClone1.directory() + "/py/namespace")
        with open(case.localClone1.directory() + "/py/namespace/__init__.py", "w") as f:
            f.write("")
        with open(case.localClone1.directory() + "/py/namespace/module_a.py", "w") as f:
            f.write("VARIABLE='value'\n")
        with open(case.localClone1.directory() + "/py/withoutnamespace.py", "w") as f:
            f.write("VARIABLE='yetanothervalue'\n")
        os.makedirs(case.localRequiringProject.directory() + "/py/namespace")
        with open(case.localRequiringProject.directory() + "/py/namespace/__init__.py", "w") as f:
            f.write("import upseto.pythonnamespacejoin\n"
                    "__path__.extend(upseto.pythonnamespacejoin.join(globals()))\n")
        with open(case.localRequiringProject.directory() + "/py/namespace/module_b.py", "w") as f:
            f.write("VARIABLE='other value'\n")
        with open(case.localRequiringProject.directory() + "/test.py", "w") as f:
            f.write(
                "#this just verifies we are not using an installed version of upseto\n"
                "import upseto\n"
                "assert '/usr/' not in upseto.__file__\n"
                "#this gets called automatically with the side upseto.pth hook, \n"
                "#but since upseto is not yet installed, we call it directly\n"
                "import upseto.pythonnamespacejoin; upseto.pythonnamespacejoin.extendPath()\n"
                "#this is how it's really used\n"
                "import namespace.module_a\n"
                "import namespace.module_b\n"
                "assert namespace.module_a.VARIABLE == 'value'\n"
                "assert namespace.module_b.VARIABLE == 'other value'\n"
                "import withoutnamespace\n"
                "assert withoutnamespace.VARIABLE == 'yetanothervalue'\n")
        return case

    def test_pythonNamespaceJoining(self):
        case = self.pythonNamespacesTestcase()
        case.localRequiringProject.run(
            'UPSETO_JOIN_PYTHON_NAMESPACES=yes PYTHONPATH=py:$PYTHONPATH python test.py')

    def test_recursiveGitInvocation(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)
        case.addThirdTier()
        firstCommitFile = os.path.join(case.localClone1.directory(), "firstCommitFile")
        self.assertTrue(os.path.exists(firstCommitFile))
        with open(firstCommitFile, "a") as f:
            f.write("\n")
        self.assertIn('M firstCommitFile', case.localClone1.shortStatus())
        result = upsetowrapper.run(case.localRecursiveProject, "git status -s")
        print "\nupseto git status -s"
        print result
        self.assertIn('M firstCommitFile', result)

    def test_packegg(self):
        case = self.pythonNamespacesTestcase()
        temp = tempfile.NamedTemporaryFile(suffix=".egg")
        upsetowrapper.packEgg(
            case.localRequiringProject,
            "--joinPythonNamespaces --entryPoint=test.py --output=%s" % temp.name,
            "py:%s/py" % case.localClone1.directory())
        upsetowrapper.runWhatever('/', "PYTHONPATH=%s python -m test" % temp.name)

    def test_packegg_replacesInitFileWithEmptyFile(self):
        case = self.pythonNamespacesTestcase()
        temp = tempfile.NamedTemporaryFile(suffix=".egg")
        upsetowrapper.packEgg(
            case.localRequiringProject,
            "--joinPythonNamespaces --entryPoint=test.py --output=%s" % temp.name,
            "py:%s/py" % case.localClone1.directory())
        with zipfile.ZipFile(temp.name) as z:
            for name in z.namelist():
                if name.endswith('__init__.py'):
                    contents = z.read(name).strip()
                    self.assertEqual(contents, "")

    def test_checkWorkspaceUnsullied(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)
        case.addThirdTier()
        upsetowrapper.run(case.localRecursiveProject, "checkRequirements --unsullied")
        os.mkdir(os.path.join(gitwrapper.localClonesDir(), "projectoutsideofupseto"))
        upsetowrapper.runShouldFail(case.localRecursiveProject, "checkRequirements --unsullied", "sullied")

    def test_checkWorkspaceClean(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)
        case.addThirdTier()
        upsetowrapper.run(case.localRecursiveProject, "checkRequirements --gitClean")
        output = upsetowrapper.run(case.localRecursiveProject, "git status -s")
        self.assertEquals(len([l for l in output.strip().split("\n") if not l.startswith("#")]), 0)
        with open(case.localClone1.directory() + "/notcheckedin", "w") as f:
            f.write("i'm here to make things dirty")
        output = upsetowrapper.run(case.localRecursiveProject, "git status -s")
        self.assertEquals(len([l for l in output.strip().split("\n") if not l.startswith("#")]), 1)
        upsetowrapper.runShouldFail(case.localRecursiveProject, "checkRequirements --gitClean", "clean")

        os.unlink(case.localClone1.directory() + "/notcheckedin")
        upsetowrapper.run(case.localRecursiveProject, "checkRequirements --gitClean")

        with open(case.localRecursiveProject.directory() + "/notcheckedin", "w") as f:
            f.write("i'm here to make things dirty")
        upsetowrapper.runShouldFail(case.localRecursiveProject, "checkRequirements --gitClean", "clean")

    def test_checkRequirementsOnNonUpsetoedProjects(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)
        case.addThirdTier()
        upsetowrapper.runShouldFail(case.localClone1, "checkRequirements", "manifest")
        upsetowrapper.runShouldFail(case.localClone2, "checkRequirements", "manifest")
        upsetowrapper.run(case.localRequiringProject, "checkRequirements")
        upsetowrapper.run(case.localRecursiveProject, "checkRequirements")

        upsetowrapper.run(case.localClone1, "checkRequirements --allowNoManifest")
        upsetowrapper.run(case.localClone2, "checkRequirements --allowNoManifest")
        upsetowrapper.run(case.localRequiringProject, "checkRequirements --allowNoManifest")
        upsetowrapper.run(case.localRecursiveProject, "checkRequirements --allowNoManifest")

    def test_Bugfix_reloadManifestAfterFulfillingRequirements_AlsoTestsDiamondAddRequirement(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)
        case.addThirdTier()

        betweenProject = gitwrapper.GitHub("between")
        localBetweenProject = gitwrapper.LocalClone(betweenProject)
        upsetowrapper.run(localBetweenProject, "addRequirement requiringProject")
        localBetweenProject.addCommitPushManifest()
        upsetowrapper.run(case.localRecursiveProject, "addRequirement between")
        case.localRecursiveProject.addCommitPushManifest()
        previousHash = case.localRecursiveProject.hash()

        case.localClone1.createAddCommitPush("nextgeneration")
        upsetowrapper.run(case.localRequiringProject, "addRequirement project1")
        case.localRequiringProject.addCommitPushManifest()
        upsetowrapper.run(localBetweenProject, "addRequirement requiringProject")
        localBetweenProject.addCommitPushManifest()
        upsetowrapper.run(case.localRecursiveProject, "addRequirement requiringProject between")
        case.localRecursiveProject.addCommitPushManifest()

        case.localRecursiveProject.checkout(previousHash)
        upsetowrapper.run(case.localRecursiveProject, "fulfillRequirements")
        case.localRecursiveProject.checkout('master')
        upsetowrapper.run(case.localRecursiveProject, "fulfillRequirements")

    def test_resolveParadoxByLocalManifestRequirements(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)
        case.addThirdTier()

        case.localClone1.createAddCommitPush("anotherfile")
        upsetowrapper.run(
            case.localRecursiveProject, "addRequirement project1 --dirtyParadoxResolution project1")
        upsetowrapper.run(case.localRecursiveProject, "checkRequirements")
        self.assertTrue(os.path.exists(os.path.join(case.localClone1.directory(), "anotherfile")))
        upsetowrapper.run(case.localRecursiveProject, "fulfillRequirements")
        upsetowrapper.run(case.localRecursiveProject, "checkRequirements")
        self.assertTrue(os.path.exists(os.path.join(case.localClone1.directory(), "anotherfile")))
        upsetowrapper.runShouldFail(case.localRecursiveProject, "addRequirement project1", "hash paradox")
        upsetowrapper.run(
            case.localRecursiveProject, "addRequirement project1 --dirtyParadoxResolution project1")

    def test_resolveParadoxByLocalManifestRequirements_CollisionBetweenResolutions(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)
        case.addThirdTier()
        case.addFourthTier()
        upsetowrapper.run(case.localFourthTierProject, "addRequirement project1")

        hashBefore = case.localClone1.hash()
        case.localClone1.createAddCommitPush("anotherfile")
        upsetowrapper.run(
            case.localRecursiveProject, "addRequirement project1 --dirtyParadoxResolution project1")
        case.localRecursiveProject.addCommitPushManifest()
        self.assertTrue(os.path.exists(os.path.join(case.localClone1.directory(), "anotherfile")))

        upsetowrapper.runShouldFail(
            case.localFourthTierProject, "addRequirement recursiveProject", "hash paradox")
        upsetowrapper.runShouldFail(
            case.localFourthTierProject,
            "addRequirement recursiveProject --dirtyParadoxResolution project1",
            "hash")
        case.localClone1.checkout(hashBefore)
        upsetowrapper.run(
            case.localFourthTierProject,
            "addRequirement recursiveProject --dirtyParadoxResolution project1")

    def test_Bugfix_fulfillRequirementChecksOutWrongVersionOnDirtyParadoxResolution(self):
        case = self.SimpleManifest_OneProjectDependsOnTwoOthers(self)

        case.localClone1.createAddCommitPush("anotherfile")
        correct = case.localClone1.hash()

        case.recursiveProject = gitwrapper.GitHub("recursiveProject")
        case.localRecursiveProject = gitwrapper.LocalClone(case.recursiveProject)
        upsetowrapper.run(case.localRecursiveProject, "addRequirement project1")
        upsetowrapper.run(
            case.localRecursiveProject,
            "addRequirement requiringProject --dirtyParadoxResolution project1")
        case.localRecursiveProject.addCommitPushManifest()
        with open(case.localRecursiveProject.manifestFilename()) as f:
            manifestContents = f.read()
        dirtyParadoxIsFirstLineOrBugIsNotRecreated = 'dirty' in manifestContents.split("\n")[1].lower()
        self.assertTrue(dirtyParadoxIsFirstLineOrBugIsNotRecreated)

        upsetowrapper.run(case.localRecursiveProject, "fulfillRequirements")
        self.assertEquals(case.localClone1.hash(), correct)
        upsetowrapper.run(case.localRecursiveProject, "checkRequirements")

    def test_normalizeURL(self):
        self.assertEquals(upseto.gitwrapper.normalizeOriginURL('https://github.com/Strato/project.git'),
                          "https://github.com/Strato/project")
        self.assertEquals(upseto.gitwrapper.normalizeOriginURL('https://github.com/Strato/project'),
                          "https://github.com/Strato/project")
        self.assertEquals(upseto.gitwrapper.normalizeOriginURL('git@github.com:Strato/project'),
                          "https://github.com/Strato/project")
        self.assertEquals(upseto.gitwrapper.normalizeOriginURL('git@github.com:Strato/project.git'),
                          "https://github.com/Strato/project")
        self.assertEquals(upseto.gitwrapper.normalizeOriginURL('file:///a/directory/with/repo'),
                          "file:///a/directory/with/repo")


# temporary deps that resolve paradoxes - for clashes in recursive deps that are not direct deps
# test no project can be added file not found or not git
# test can not remove
# test basenames collision
# test manifest files must not be in modified state - either committed or unknown

if __name__ == '__main__':
    unittest.main()
