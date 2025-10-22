# Instructions :
# This challenge is about Biology that will put emphasis on your knowledge of classes, inheritance and polymorphism.

# Build a DNA object. DNA is composed of chromosomes which is itself composed of Genes.
# A Gene is a single value 0 or 1, it can mutate (flip).
# A Chromosome is a series of 10 Genes. It also can mutate, meaning a random number of genes can randomly flip (1/2 chance to flip).
# A DNA is a series of 10 chromosomes, and it can also mutate the same way Chromosomes can mutate.

# Implement these classes as you see fit.

# Create a new class called Organism that accepts a DNA object and an environment parameter that sets the probability for its DNA to mutate.

# Instantiate a number of Organism and let them mutate until one gets to a DNA which is only made of 1s. Then stop and record the number of generations (iterations) it took.
# Write your results in you personal biology research notebook and tell us your conclusion :).


import random
from dataclasses import dataclass
from typing import List, Tuple

random.seed(4242)  # reproducibility; remove for natural randomness

@dataclass
class Gene:
    value: int  # 0 or 1
    def mutate(self) -> None:
        self.value = 1 - self.value  # flip

@dataclass
class Chromosome:
    genes: List[Gene]  # length 10

    @classmethod
    def random(cls, length: int = 10) -> "Chromosome":
        return cls([Gene(random.randint(0, 1)) for _ in range(length)])

    def mutate(self, per_gene_rate: float = 0.02) -> None:
        # Flip a random subset of genes (each gene selected with small probability)
        for g in self.genes:
            if random.random() < per_gene_rate:
                g.mutate()

    def is_all_ones(self) -> bool:
        return all(g.value == 1 for g in self.genes)

    def copy(self) -> "Chromosome":
        return Chromosome([Gene(g.value) for g in self.genes])

@dataclass
class DNA:
    chromosomes: List[Chromosome]  # length 10

    @classmethod
    def random(cls, n_chromosomes: int = 10, chromo_length: int = 10) -> "DNA":
        return cls([Chromosome.random(chromo_length) for _ in range(n_chromosomes)])

    def mutate(self, per_gene_rate: float = 0.02) -> None:
        for c in self.chromosomes:
            c.mutate(per_gene_rate=per_gene_rate)

    def is_all_ones(self) -> bool:
        return all(c.is_all_ones() for c in self.chromosomes)

    def copy(self) -> "DNA":
        return DNA([c.copy() for c in self.chromosomes])

    def ones_count(self) -> int:
        return sum(g.value for c in self.chromosomes for g in c.genes)

class Organism:
    def __init__(self, dna: DNA, environment: float, per_gene_rate: float = 0.02):
        """
        environment: probability in [0,1] that this organism's DNA mutates this generation.
        per_gene_rate: probability a gene flips when mutation happens.
        """
        self.dna = dna
        self.environment = environment
        self.per_gene_rate = per_gene_rate

    def maybe_mutate(self) -> None:
        if random.random() < self.environment:
            self.dna.mutate(per_gene_rate=self.per_gene_rate)

    def fitness(self) -> int:
        return self.dna.ones_count()

    def clone(self) -> "Organism":
        return Organism(self.dna.copy(), self.environment, self.per_gene_rate)

# --- Evolution utilities ---
def crossover(p1: Organism, p2: Organism) -> DNA:
    # single-point crossover inside each chromosome
    child_chromosomes: List[Chromosome] = []
    for c1, c2 in zip(p1.dna.chromosomes, p2.dna.chromosomes):
        point = random.randint(1, len(c1.genes) - 1)
        genes = [Gene(g.value) for g in c1.genes[:point]] + [Gene(g.value) for g in c2.genes[point:]]
        child_chromosomes.append(Chromosome(genes))
    return DNA(child_chromosomes)

def evolve_to_all_ones(
    population_size: int = 250,
    environment: float = 1.0,     # try mutation each generation
    per_gene_rate: float = 0.02,  # gentle flips
    max_generations: int = 3000,
    tournament_k: int = 3,
) -> Tuple[int, Organism]:
    # init pop
    pop = [Organism(DNA.random(), environment, per_gene_rate) for _ in range(population_size)]
    generation = 0
    best = max(pop, key=lambda o: o.fitness())

    while generation < max_generations and best.fitness() < 100:
        generation += 1

        # tournament selection
        def tournament() -> Organism:
            group = random.sample(pop, tournament_k)
            return max(group, key=lambda o: o.fitness())

        # next gen with elitism
        new_pop: List[Organism] = []
        elite = max(pop, key=lambda o: o.fitness())
        new_pop.append(Organism(elite.dna.copy(), elite.environment, elite.per_gene_rate))

        while len(new_pop) < population_size:
            p1, p2 = tournament(), tournament()
            child = Organism(crossover(p1, p2), environment, per_gene_rate)
            child.maybe_mutate()
            new_pop.append(child)

        pop = new_pop
        best = max(pop, key=lambda o: o.fitness())

    return generation, best

# --- Run a demo ---
if __name__ == "__main__":
    gens, champ = evolve_to_all_ones(population_size=250, environment=1.0, per_gene_rate=0.02, max_generations=3000)
    print(f"Stopped at generation: {gens}")
    print(f"Champion fitness: {champ.fitness()} / 100")
    print(f"All ones? {champ.dna.is_all_ones()}")
