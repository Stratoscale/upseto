import upseto.pythonnamespacejoin
import sys
import re


for module in sys.modules.values():
    if 'upseto' not in getattr(module, "__file__", ""):
        continue
    filename = module.__file__
    if filename.endswith(".pyc") or filename.endswith(".pyo"):
        filename = filename[: -len("c")]
    with open(filename) as f:
        contents = f.read()
    if re.search(r"\blogging\b", contents) is not None:
        raise Exception("File %s imported from upseto.pythonnamespacejoin contains calls to logging"
                        ". This is as it might create handlers before pycommonlog" % (
                            filename, ))
    print filename
