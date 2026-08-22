"""Centralized deterministic pseudo-random state wrapper for ClaimIQ Generator."""

import random
from typing import Sequence, TypeVar, List
from faker import Faker

T = TypeVar("T")


class GeneratorRandomState:
    """Encapsulates deterministic random number generation and localized Faker instances."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        Faker.seed(seed)
        self.faker = Faker("en_US")
        # Ensure faker internal generator uses the same seed
        self.faker.random.seed(seed)

    def random(self) -> float:
        """Return random float in [0.0, 1.0)."""
        return self.rng.random()

    def uniform(self, a: float, b: float) -> float:
        """Return random float in [a, b]."""
        return self.rng.uniform(a, b)

    def randint(self, a: int, b: int) -> int:
        """Return random integer in [a, b] including both endpoints."""
        return self.rng.randint(a, b)

    def choice(self, seq: Sequence[T]) -> T:
        """Return a random element from non-empty sequence."""
        return self.rng.choice(seq)

    def choices(self, population: Sequence[T], weights: Sequence[float], k: int = 1) -> List[T]:
        """Return a k-sized list of population elements chosen with replacement according to relative weights."""
        return self.rng.choices(population, weights=weights, k=k)

    def sample(self, population: Sequence[T], k: int) -> List[T]:
        """Return a k-length list of unique elements chosen from the population sequence."""
        return self.rng.sample(population, k)

    def shuffle(self, x: list) -> None:
        """Shuffle list x in place."""
        self.rng.shuffle(x)

    def first_name(self, gender: str = None) -> str:
        if gender == "M":
            return self.faker.first_name_male()
        elif gender == "F":
            return self.faker.first_name_female()
        return self.faker.first_name()

    def last_name(self) -> str:
        return self.faker.last_name()

    def company_name(self) -> str:
        return self.faker.company()

    def state_abbr(self) -> str:
        return self.faker.state_abbr()
