"""Unit tests for deterministic pseudo-random sampling and seed reproducibility."""

import pytest
from generator.random_state import GeneratorRandomState


def test_sampling_determinism_same_seed():
    population = [f"ITEM_{i}" for i in range(100)]
    
    rng1 = GeneratorRandomState(42)
    sample1 = rng1.sample(population, 10)
    choice1 = [rng1.choice(population) for _ in range(5)]
    
    rng2 = GeneratorRandomState(42)
    sample2 = rng2.sample(population, 10)
    choice2 = [rng2.choice(population) for _ in range(5)]
    
    assert sample1 == sample2
    assert choice1 == choice2


def test_sampling_divergence_different_seeds():
    population = [f"ITEM_{i}" for i in range(100)]
    
    rng_a = GeneratorRandomState(42)
    sample_a = rng_a.sample(population, 15)
    
    rng_b = GeneratorRandomState(99)
    sample_b = rng_b.sample(population, 15)
    
    assert sample_a != sample_b


def test_float_and_int_determinism():
    rng1 = GeneratorRandomState(12345)
    floats1 = [rng1.uniform(10.0, 500.0) for _ in range(10)]
    ints1 = [rng1.randint(1, 1000) for _ in range(10)]
    
    rng2 = GeneratorRandomState(12345)
    floats2 = [rng2.uniform(10.0, 500.0) for _ in range(10)]
    ints2 = [rng2.randint(1, 1000) for _ in range(10)]
    
    assert floats1 == floats2
    assert ints1 == ints2
