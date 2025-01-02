import random
from .strategy import SchedulingStrategy
from .node import Node
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class GeneticAlgorithm(SchedulingStrategy):
    def __init__(self, generations=10, population_size=10):
        self.generations = generations
        self.population_size = population_size
        
    def schedule_deployments(self, node, deployments):
        logger.info("Scheduling deployments using Genetic Algorithm with deployment size: %d", len(deployments))
        def evaluate_fitness(individual, best_fitness):
            node_copy = Node(node.id, node.cpu, node.memory, node.gpu)
            scheduled_deployments = []
            for deployment in individual:
                if node_copy.schedule(deployment):
                    scheduled_deployments.append(deployment)
                if len(scheduled_deployments) + len(individual) - len(scheduled_deployments) <= best_fitness:
                    break  # No point in continuing
            return len(scheduled_deployments), scheduled_deployments

        if not deployments:
            return []

        self.population_size = min(self.population_size, len(deployments))
        population = [random.sample(deployments, len(deployments)) for _ in range(self.population_size)]
        best_solution = []
        best_fitness = 0

        for _ in range(self.generations):
            fitness_scores = []
            for individual in population:
                fitness, scheduled_deployments = evaluate_fitness(individual, best_fitness)
                fitness_scores.append((fitness, individual))
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_solution = scheduled_deployments

            fitness_scores.sort(key=lambda x: x[0], reverse=True)
            population = [individual for _, individual in fitness_scores[:self.population_size]]

            next_population = []
            for _ in range(self.population_size):
                parent1, parent2 = random.sample(population, 2)
                
                crossover_point = random.randint(1, len(deployments) - 1) if len(deployments) > 1 else 0
                child = parent1[:crossover_point] + [d for d in parent2 if d not in parent1[:crossover_point]]

                if len(child) > 1:
                    idx1, idx2 = random.sample(range(len(child)), 2)
                    child[idx1], child[idx2] = child[idx2], child[idx1]  # Swap mutation
                next_population.append(child)

            population = next_population

            if best_fitness == len(deployments):  # Early stopping
                break
        print(f"fitness: {best_fitness}")
        return best_solution