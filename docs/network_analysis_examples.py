# %%--
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
# %%--

import os
import warnings

import numpy as np
import pandas as pd


os.chdir("../src")
import sgis as sg


os.chdir("..")

# ignore some warnings to make it cleaner
pd.options.mode.chained_assignment = None
warnings.filterwarnings(action="ignore", category=UserWarning)
warnings.filterwarnings(action="ignore", category=FutureWarning)
import geopandas as gpd

r = gpd.read_file(
    r"C:\Users\ort\Downloads\vegnettRuteplan_FGDB_20230109.gdb",
    layer="ruttger_link_geom",
    engine="pyogrio",
    where="municipality in ('3416')",
)
r.to_parquet(r"C:\Users\ort\git\ssb-sgis\tests\testdata\roads_eidskog_2022.parquet")

r2 = (
    r.sample(40)
    .assign(geometry=lambda x: x.centroid.buffer(np.arange(1, 41)))
    .pipe(sg.to_multipoint)
    .explode()
    .sample(100)
    .reset_index()
    .assign(idx=range(100))[["idx", "geometry"]]
)

r2.to_parquet(r"C:\Users\ort\git\ssb-sgis\tests\testdata\points_eidskog.parquet")
r2.explore()
# %%
import sgis as sg

roads = sg.read_parquet_url(
    "https://media.githubusercontent.com/media/statisticsnorway/ssb-sgis/main/tests/testdata/roads_oslo_2022.parquet"
)

nw = (
    sg.DirectedNetwork(roads)
    .remove_isolated()
    .make_directed_network(
        direction_col="oneway",
        direction_vals_bft=("B", "FT", "TF"),
        minute_cols=("drivetime_fw", "drivetime_bw"),
    )
)

rules = sg.NetworkAnalysisRules(weight="minutes")

nwa = sg.NetworkAnalysis(network=nw, rules=rules)

nwa
# %%

points = sg.read_parquet_url(
    "https://media.githubusercontent.com/media/statisticsnorway/ssb-sgis/main/tests/testdata/points_oslo.parquet"
)

# %% [markdown]
# # sgis
# sgis builds on the geopandas package, providing functions for making it easier to do advanced, high quality GIS in python.
#
# A core feature is network analysis. Other features include vector operations like finding k nearest neighbours, splitting
# lines by points, snapping geometries and closing holes in polygons by area.
#
# Another feature is exploring multiple GeoDataFrames in a layered interactive map.
#
# ### Network analysis
#
# Road data can be prepared for network analysis like this:
#
# %%
import sgis as sg

roads = sg.read_parquet_url(
    "https://media.githubusercontent.com/media/statisticsnorway/ssb-sgis/main/tests/testdata/roads_oslo_2022.parquet"
)

nw = (
    sg.DirectedNetwork(roads)
    .remove_isolated()
    .make_directed_network(
        direction_col="oneway",
        direction_vals_bft=("B", "FT", "TF"),
        minute_cols=("drivetime_fw", "drivetime_bw"),
    )
)

rules = sg.NetworkAnalysisRules(weight="minutes")

nwa = sg.NetworkAnalysis(network=nw, rules=rules)

nwa
# %% [markdown]
# Road data for Norway can be downloaded here: https://kartkatalog.geonorge.no/metadata/nvdb-ruteplan-nettverksdatasett/8d0f9066-34f9-4423-be12-8e8523089313
#
# #### get_route_frequencies: get the number of times each line segment was visited

# %%
freq = nwa.get_route_frequencies(points.sample(75), points.sample(75))

sg.qtm(
    sg.buff(freq, 15),
    "n",
    scheme="naturalbreaks",
    cmap="plasma",
    title="Number of times each road was used.",
)

# %% [markdown]
# #### od_cost_matrix: fast many-to-many travel times/distances

# %%
od = nwa.od_cost_matrix(points.iloc[[0]], points, id_col="idx", lines=True)

print(od.head(3))

sg.qtm(od, "minutes", title="Travel time (minutes) from 1 to 1000 points.")
# %% [markdown]
# #### service_area: get the area that can be reached within one or more breaks

# %%
sa = nwa.service_area(
    points.iloc[[0]],
    breaks=np.arange(1, 11),
)

sg.qtm(sa, "minutes", k=10, title="Roads that can be reached within 1 to 10 minutes")
# %% [markdown]
# #### get_route and get_k_routes: get one or more route per origin-destination pair

# %%
routes = nwa.get_k_routes(
    points.iloc[[0]], points.iloc[[1]], k=5, drop_middle_percent=50
)

sg.qtm(sg.buff(routes, 15), "k", title="k=5 low-cost routes", legend=False)

# %% [markdown]
# More network analysis examples can be found here: https://github.com/statisticsnorway/ssb-sgis/blob/main/network_analysis_demo_template.md
# And in the docs: TODO
