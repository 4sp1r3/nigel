import unittest

class ADFFiveParityTestCase(unittest.TestCase):
    """
    Run the adf version of five parity
    """
    def test_one(self):
        from app.adffiveparity import main
        pop, stats, hof = main(gens=20, pop_size=300)
        print(hof)

        from app.ourMods import adfdraw
        adfdraw(hof[0])

    def test_two(self):
        from app.madffiveparity import main
        from app.ourMods import adfdraw

        pop, stats, hof = main(gens=100, pop_size=400)

        for ind in hof:
            print(ind.fitness)
            adfdraw(ind)

        # print(pop[0].fitness)
        # adfdraw(pop[0])
        # print(pop[-1].fitness)
        # adfdraw(pop[-1])
