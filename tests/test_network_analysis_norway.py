#%%
from pathlib import Path

import geopandas as gpd
import cProfile

def not_test_network_analysis_norway():

    from tests.test_od_cost_matrix import test_od_cost_matrix
    from tests.test_shortest_path import test_shortest_path
    from tests.test_service_area import test_service_area

    test_shortest_path()
    test_service_area()
    test_od_cost_matrix()


def main():

    import cProfile

    cProfile.run("not_test_network_analysis_norway()", sort="cumtime")

if __name__ == "__main__":
    main()