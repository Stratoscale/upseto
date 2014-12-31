Upseto:
-------

What does it do?
- Allows creating complex digraph dependency graphs (unlike git submodule
  which is always a tree). This is useful if common libraries are shared
  between subprojects, to enforce them to use the same version
- Helps with splitting python namespaceses across such repositories

Setup:
------
Run make install. Make sure you have your github account setup in
~/.netrc, for all the git fetch operations
```
machine github.com
  login <your username>
  password <your password or key>
```
http://stackoverflow.com/questions/5343068/is-there-a-way-to-skip-password-typing-when-using-https-github

Command Line Usage:
-------------------
enter the following for command line usage message
```
upseto --help
```
WARNING: please read WARNING.md

Joining Python Namespaces:
--------------------------
This is a development time feature. When packing your code to production
it is recomended not to use it. Upseto python namespace joining will
only work if the environment variable UPSETO_JOIN_PYTHON_NAMESPACES
is defined, for this reason.

copy paste the following into a __init__.py file:
```
import upseto.pythonnamespacejoin
__path__.extend(upseto.pythonnamespacejoin.join(globals()))
```

upseto will look in all depedant projects, recursively, and will add
the search paths, possibly under the "py/" directory as well from all
of them.
