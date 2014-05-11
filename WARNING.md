WARNING
-------

i would like to draw your intention to a specific design decision i made with
upseto:
it does not verify your git repos are "clean", in any operation.

this means:
- fulfillRequirements - will 'git checkout' into a different hash, leaving
  uncommited patches in place (or failing or merge issues)
- checkRequirements - will reports "everything is ok" even when you have
  uncommited changes
- addRequirements - might add "the wrong hash" if you have uncommited changes
  in your dependecy repo.

the point is: i left "dirtyness" tracking to the developers. at any case, the
CI will catch your booboos, but i also recommend the following: upseto has
the command "git" to run a git command at all dependencies. so the command
line:
```
upseto git status -s
```
will show you if any such modifications exist in any of your dependencies.
so when you are "pushing to master" / "pullrequesting", i recommend running
this command line just in case.

why was this decision made: if upseto will enforce "clean" hash checkout of
dependencies, that you would not be able to "play around" with the sources
of dependant packages - the moment one if your scripts uses upseto - any
"print"/"trace"/"breakpoint" added will cause your scripting to break.
