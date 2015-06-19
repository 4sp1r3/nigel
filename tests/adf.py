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

        pop, stats, hof = main(gens=50,
                               pop_size=1000,
                               adf_range=(0,3),
                               adf_nargs=(1,4),
                               mmc=(80,10,10),
                               best_of_class=20,
                               growth=(30,4))

        pop = sorted(pop, key=lambda i: i.fitness.values[0])
        for ind in [pop[0], pop[-1]]:
            adfdraw(ind)

        # for i in pop:
        #     print(i.fitness.values[0], i.signature)


        # import cProfile
        # cProfile.runctx('main(gens=1, pop_size=2, growth=(30,10))', None, locals(), sort='tottime')
