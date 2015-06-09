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

        pop, stats, hof = main(gens=500, pop_size=300)
        print(hof)

        from app.ourMods import adfdraw

        for ind in hof:
            print(ind.fitness)
            adfdraw(ind)
