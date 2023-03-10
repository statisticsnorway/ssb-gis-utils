# %%
import sys
from pathlib import Path

import geopandas as gpd


src = str(Path(__file__).parent).strip("tests") + "src"

sys.path.insert(0, src)

import sgis as sg


def test_node_ids(points_oslo, roads_oslo):
    p = points_oslo
    p = sg.clean_clip(p, p.geometry.iloc[0].buffer(500))
    p["idx"] = p.index
    p["idx2"] = p.index

    r = roads_oslo
    r = sg.clean_clip(r, p.geometry.iloc[0].buffer(600))

    r, nodes = sg.make_node_ids(r)
    print(nodes)
    r, nodes = sg.make_node_ids(r, wkt=False)
    print(nodes)

    nw = sg.DirectedNetwork(r)
    rules = sg.NetworkAnalysisRules(weight="meters")
    nwa = sg.NetworkAnalysis(nw, rules=rules)

    nwa.od_cost_matrix(p.sample(5), p.sample(5), id_col="idx")

    nwa.network = nwa.network.close_network_holes(2, fillna=0)
    nwa.network = nwa.network.get_component_size()
    nwa.network = nwa.network.remove_isolated()
    nwa.network.gdf["col"] = 1
    nwa.network.gdf = nwa.network.gdf.drop("col", axis=1)

    nwa.network.gdf = nwa.network.gdf.sjoin(
        sg.buff(p[["geometry"]].sample(1), 2500)
    ).drop("index_right", axis=1, errors="ignore")

    p = (
        p.sjoin(sg.buff(nwa.network.gdf[["geometry"]], 2500))
        .drop("index_right", axis=1, errors="ignore")
        .drop_duplicates("idx")
    )

    nwa.od_cost_matrix(p.sample(5), p.sample(5), id_col="idx")
    nwa.od_cost_matrix(p.sample(5), p.sample(5), id_col="idx")
    nwa.od_cost_matrix(p.sample(5), p.sample(5), id_col="idx")
    nwa.od_cost_matrix(p.sample(5), p.sample(5), id_col="idx")
    nwa.od_cost_matrix(p.sample(5), p.sample(5), id_col="idx")


def main():
    """Check how many times make_node_ids is run."""
    import cProfile

    from oslo import points_oslo, roads_oslo

    test_node_ids(points_oslo(), roads_oslo())
    quit()
    cProfile.run("test_node_ids()", sort="cumtime")


if __name__ == "__main__":
    main()

# %%
