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

        pop, stats, hof = main(gens=1, pop_size=400)
        pop = sorted(pop, key=lambda i: i.fitness.values[0])

        for ind in [hof[0], pop[0], pop[-1]]:
            adfdraw(ind)
