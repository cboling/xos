import os
import glob
import unittest


def create_test_suite():
    # Get the relative directory path to this subdirectory
    rel_path = os.path.dirname(os.path.relpath(__file__))

    test_files = glob.glob('%s/test_*.py' % rel_path)

    module_strings = [module.replace('/', '.')[:len(module) - 3] for module in test_files]

    suites = [unittest.defaultTestLoader.loadTestsFromName(name)
              for name in module_strings]

return unittest.TestSuite(suites) if len(suites) > 0 else None