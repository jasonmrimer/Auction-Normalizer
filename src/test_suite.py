import unittest

import test_constraints
import test_triggers


def suite():
    loader = unittest.TestLoader()
    _suite = unittest.TestSuite()
    _suite.addTest(loader.loadTestsFromModule(test_triggers))
    _suite.addTest(loader.loadTestsFromModule(test_constraints))
    return _suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
