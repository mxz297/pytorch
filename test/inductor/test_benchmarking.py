# Owner(s): ["module: inductor"]

import unittest

import torch
from torch._dynamo.utils import counters
from torch._inductor.runtime.benchmarking import Benchmarker
from torch._inductor.test_case import run_tests, TestCase
from torch.testing._internal.common_utils import parametrize
from torch.testing._internal.inductor_utils import GPU_TYPE, HAS_CPU, HAS_GPU


class TestBenchmarker(TestCase):
    ThisBenchmarker = Benchmarker

    @classmethod
    def setUpClass(cls):
        return super().setUpClass()

    @classmethod
    def setUp(cls):
        torch.manual_seed(12345)
        counters.clear()

    def make_sum(device, size=100):
        fn, args, kwargs = torch.sum, (torch.randn(size, device=device)), {}
        _callable = lambda: fn(*args, **kwargs)
        return (fn, args, kwargs), _callable

    @unittest.skipIf(not HAS_CPU or not HAS_GPU)
    @parametrize("device", (GPU_TYPE, "cpu"))
    def test_benchmark(self, device):
        benchmarker = self.ThisBenchmarker()
        fn, args, kwargs, _ = self.make_sum(device)
        if device == "cpu":
            _ = benchmarker.benchmark(fn, *args, **kwargs)
            self.assertEqual(
                counters["inductor"][
                    f"benchmarking-{type(self.ThisBenchmarker)}.benchmark"
                ],
                1,
            )
            self.assertEqual(
                counters["inductor"][
                    f"benchmarking-{type(self.ThisBenchmarker)}.benchmark_cpu"
                ],
                1,
            )
        else:
            self.assertExpectedRaises(
                NotImplementedError, lambda: benchmarker.benchmark(fn, *args, **kwargs)
            )
            self.assertEqual(
                counters["inductor"][
                    f"benchmarking-{type(self.ThisBenchmarker)}.benchmark"
                ],
                1,
            )
            self.assertEqual(
                counters["inductor"][
                    f"benchmarking-{type(self.ThisBenchmarker)}.benchmark_gpu"
                ],
                1,
            )

    @unittest.skipIf(not HAS_CPU)
    def test_benchmark_cpu(self):
        benchmarker = self.ThisBenchmarker()
        _, _callable = self.make_sum("cpu")
        _ = benchmarker.benchmark_cpu(_callable)
        self.assertEqual(
            counters["inductor"][
                f"benchmarking-{type(self.ThisBenchmarker)}.benchmark_cpu"
            ],
            1,
        )

    @unittest.skipIf(not HAS_GPU)
    def test_benchmark_gpu(self):
        benchmarker = self.ThisBenchmarker()
        _, _callable = self.make_sum(GPU_TYPE)
        self.assertExpectedRaises(
            NotImplementedError, lambda: benchmarker.benchmark_gpu(_callable)
        )
        self.assertEqual(
            counters["inductor"][
                f"benchmarking-{type(self.ThisBenchmarker)}.benchmark_gpu"
            ],
            1,
        )


if __name__ == "__main__":
    run_tests()
