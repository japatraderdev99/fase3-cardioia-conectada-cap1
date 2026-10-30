import unittest
import numpy as np
from experiment import generate, lif, statistics
class ExperimentTests(unittest.TestCase):
    def test_generator_reproducible_and_balanced(self):
        x,y=generate();a,b=generate()
        np.testing.assert_array_equal(x,a);np.testing.assert_array_equal(y,b)
        self.assertEqual(x.shape,(1200,180));self.assertEqual(int(y.sum()),600)
    def test_lif_silent_and_active(self):
        _,silent=lif(np.full((1,180),40.),True)
        _,active=lif(np.full((1,180),150.),True)
        self.assertEqual(int(silent.sum()),0);self.assertGreater(int(active.sum()),0)
        self.assertTrue(set(np.unique(active)) <= {0,1})
    def test_lif_state_does_not_leak_between_individuals(self):
        x,_=generate(10)
        np.testing.assert_allclose(lif(x)[0],lif(x[:1])[0])
        np.testing.assert_allclose(lif(x)[::-1],lif(x[::-1]))
    def test_features_finite(self):
        x,_=generate(10)
        self.assertTrue(np.isfinite(lif(x)).all());self.assertTrue(np.isfinite(statistics(x)).all())
if __name__=='__main__':unittest.main()
