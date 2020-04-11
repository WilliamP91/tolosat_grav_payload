"""

@authors:

# =============================================================================
 Information:

    The functions in this script all regard matters related to mpl Basemap

# =============================================================================
"""
# =============================================================================
# LIBRARIES
# =============================================================================
# You might need to comment these two lines out
import os
os.environ['PROJ_LIB'] = r'C:\Users\Xavier\Anaconda3\pkgs\proj4-5.2.0-ha925a31_1\Library\share'

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from numpy import pi, sin, cos


#import GH_import       as imp
#import GH_convert      as conv
#import GH_generate     as gen
#import GH_solve        as solv
#import GH_displayGeoid as dgeo
#import GH_displaySat   as dsat
#import GH_export       as exp
#import GH_displayTopo  as dtopo
#import GH_terminal     as term
#import GH_basemap      as bmp
#import GH_harmonics    as harm


# =============================================================================
# FUNCTIONS - BASEMAP PARAMETERS
# =============================================================================
def init_basemap (style = "crude mill"):

    if (style == "crude mill"):
        proj = "mill" # projection
        LatS = -90 # llcrnrlat
        LatN = 90 # urcrnrlat
        LongW = -180 # llcrnrlon
        LongE = 180 # urcrnrlon
        TS = 20 # lat_ts -- I don't know what this is but everyone online uses it so yeah
        Res = "c" # resolution, Crude, Low, [Intermediate, High, Full] > download extensions

    elif (style == "low mill"):
        proj = "mill" # projection
        LatS = -90 # llcrnrlat
        LatN = 90 # urcrnrlat
        LongW = -180 # llcrnrlon
        LongE = 180 # urcrnrlon
        TS = 20 # lat_ts -- I don't know what this is but everyone online uses it so yeah
        Res = "l" # resolution, Crude, Low, [Intermediate, High, Full] > download extensions

    else:
        proj = "mill" # projection
        LatS = -90 # llcrnrlat
        LatN = 90 # urcrnrlat
        LongW = -180 # llcrnrlon
        LongE = 180 # urcrnrlon
        TS = 20 # lat_ts -- I don't know what this is but everyone online uses it so yeah
        Res = "c" # resolution, Crude, Low, [Intermediate, High, Full] > download extensions

    # Bm_Param = [proj, LatS, LatN, LongW, LongE, TS, Res]
    return proj, LatS, LatN, LongW, LongE, TS, Res


# =============================================================================
# FUNCTIONS TO MAKE MAPS
# =============================================================================
def Gen_Basemap (fignum, style = "crude mill"):
    """
    Generates a Basemap map in the figure numbered fignum
    """
    plt.figure(fignum)

    proj, LatS, LatN, LongW, LongE, TS, Res = init_basemap(style)

    MAP = Basemap(projection = proj,
                llcrnrlat = LatS,
                urcrnrlat = LatN,
                llcrnrlon = LongW,
                urcrnrlon = LongE,
                lat_ts = TS,
                resolution = Res)
    return MAP

def Map_Earth (fignum):
    """
    Makes a map of Earth
    """
    FIG = plt.figure(fignum)
    plt.clf()
    AX = FIG.add_subplot(111)
    MAP = Gen_Basemap(FIG.number, "low mill")
    MAP.drawcoastlines(linewidth = 0.4)

    """map parameters"""
    water_color = 'lightcyan'
    land_color = 'peachpuff'
    MAP.fillcontinents(color=land_color,lake_color=water_color)
    MAP.drawmapboundary(fill_color=water_color)

    parallels = np.arange(-60.,61,30.)
    meridians = np.arange(0.,351.,30.)
    MAP.drawparallels(parallels)
    MAP.drawmeridians(meridians)

    """plot apperance"""
    plt.title("Map of the Earth")

    plt.axis('off')
    plt.show(block=False)


def init_grid(tens):
    """
    Initiates the grid variables based on the number of points wanted
    """
    size_long = 1 + 36*tens
    size_lat  = 1 + 18*tens
    points = size_long * size_lat

    Line_long = np.linspace(0, 2*pi, size_long) # 0 to 360 ; must subtract 180
    Line_lat  = np.linspace(0, pi, size_lat) # 0 to 180 ; must do 90 - theta
    G_Long, G_Lat = np.meshgrid((Line_long - pi), (pi/2 - Line_lat))

    G_Grid = np.zeros((size_lat, size_long))
    
    return G_Grid, G_Long, G_Lat, Line_long, Line_lat, size_long, size_lat, points

# =============================================================================
# DISPLAY FUNCTIONS
# =============================================================================


# =============================================================================
# TEST FUNCTIONS
# =============================================================================
def TEST_MAP():
    Map_Earth(1)

# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    TEST_MAP()

    print("\nGH_displayCoef done")

