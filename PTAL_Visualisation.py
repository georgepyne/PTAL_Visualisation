
import geopandas as gpd
import bokeh
import pysal as ps
import pandas as pd
import numpy as np
import matplotlib as plt
from matplotlib import cm


def gpd_bokeh(df):
    """ Change geopandas geometries to work with bokeh mapping"""
    nan = float('nan')
    lons = []
    lats = []
    for i,shape in enumerate(df.geometry.values):
        if shape.geom_type == 'MultiPolygon':
            gx = []
            gy = []
            ng = len(shape.geoms) - 1
            for j,member in enumerate(shape.geoms):
                xy = np.array(list(member.exterior.coords))
                xs = xy[:,0].tolist()
                ys = xy[:,1].tolist()
                gx.extend(xs)
                gy.extend(ys)
                if j < ng:
                    gx.append(nan)
                    gy.append(nan)
            lons.append(gx)
            lats.append(gy)

        else:
            xy = np.array(list(shape.exterior.coords))
            xs = xy[:,0].tolist()
            ys = xy[:,1].tolist()
            lons.append(xs)
            lats.append(ys)

    return lons,lats

def main():

      # Read in LSOA shapefile
    shp_link = "LSOA_2011_London_gen_MHW.shp"
      # Set CRS for later mapping
    shp = gpd.read_file(shp_link, crs="+init=epsg:4326")
    shp = shp.to_crs(epsg=3857)

      # Read PTAL table
    PTAL_AV = pd.read_excel("LSOA2011_AvPTAI2015.xlsx")
      # Rename column for merge
    PTAL_AV = PTAL_AV.rename(columns = {'LSOA2011':'LSOA11CD'})

    PTAL = shp.merge(PTAL_AV, on='LSOA11CD')
      # Rename average PTAL col to easier name
    PTAL = PTAL.rename(columns = {'AvPTAI2015':'AV_PTAL'})

      # Read in bokeh modules
    from collections import OrderedDict
    from bokeh.plotting import figure, show, output_notebook, ColumnDataSource
    from bokeh.models import HoverTool
    from bokeh.io import output_file, show #Scatter


      # Convert geomertries from gpd to bokeh format
    lons, lats = gpd_bokeh(PTAL)


      # Create PTAL Rate quantile bins in pysal
    bins_q5 = ps.Quantiles(PTAL.AV_PTAL, k=5)

        # Creat colour classes from bins
    bwr = plt.cm.get_cmap('Reds')
    bwr(.76)
    c5 = [bwr(c) for c in [0.2, 0.4, 0.6, 0.7, 1.0]]
    classes = bins_q5.yb
    colors = [c5[i] for i in classes]



    colors5 = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77"]
    colors = [colors5[i] for i in classes]

    p = figure(title="London PTAI 2015 Quintiles", toolbar_location='left',
                plot_width=1100, plot_height=700)
    p.patches(lons, lats, fill_alpha=0.7, fill_color=colors,
                line_color="#884444", line_width=2, line_alpha=0.3)

    # Now for interactive plot
    from bokeh.models import HoverTool
    from bokeh.plotting import figure, show, output_file, ColumnDataSource
    from bokeh.tile_providers import STAMEN_TERRAIN, CARTODBPOSITRON_RETINA

    source = ColumnDataSource(data=dict(
        x=lons,
        y=lats,
        color=colors,
        name=PTAL.LSOA11NM,
        rate=PTAL.AV_PTAL
    ))
        # Add bokeh tools for interactive mapping
    TOOLS = "pan, wheel_zoom, box_zoom, reset, hover, save"
    p = figure(title="London Average PTAL Index ", tools=TOOLS,
                plot_width=900, plot_height=900)

    p.patches('x', 'y', source=source,
            fill_color='color', fill_alpha=0.7,
            line_color='white', line_width=0.5)


        # Define what info shows with mouse hover
    hover = p.select_one(HoverTool)
    hover.point_policy = 'follow_mouse'
    hover.tooltips = [
        ("Name", "@name"),
        ("PTAL rank", "@rate"),
    ]

        # Turn off axis
    p.axis.visible = False
        # Add basemap
    p.add_tile(CARTODBPOSITRON_RETINA)
    # Output file to html
    output_file("London_PTAL2015.html", title="Average_PTAL_2015")
    show(p)


if __name__ == '__main__':
        main()
