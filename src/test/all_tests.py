import glob
import unittest


def create_test_suite():
    test_file_strings = glob.glob('test/*_test.py')
    module_strings = ['test.' + str[:len(str) - 8] for str in test_file_strings]
    suites = [unittest.defaultTestLoader.loadTestsFromName(name)
              for name in module_strings]
    test_suite = unittest.TestSuite(suites)
    return test_suite

