"""

@authors:

# =============================================================================
 Information:

    The purpose of this script is to calculate the sums from spherical 
    harmonic coefficients, and generate grids of data mapped out over the 
    surface of the Earth
    
    Generally used variables:
        R, Lat, Long, lmax, HC, HS, lmax_topo, HC_topo, HS_topo

todo:
    write in w_0 as an argument in get_isopot
# =============================================================================
"""
# =============================================================================
# LIBRARIES
# =============================================================================
import matplotlib.pyplot as plt 
import numpy as np
from numpy import pi, sin, cos
from time import sleep

import GH_import       as imp
import GH_convert      as conv
#import GH_generate     as gen
#import GH_solve        as solv
#import GH_displayGeoid as dgeo
#import GH_displaySat   as dsat
#import GH_export       as exp
#import GH_displayTopo  as dtopo
import GH_terminal     as term
#import GH_basemap      as bmp
#import GH_harmonics    as harm
import GH_geoMath      as gmath


# =============================================================================
# FUNCTIONS TO CALCULATE SPHERICAL HARMONIC SUMS
# =============================================================================
def Get_Topo_Height (R, Lat, Long,    lmax_topo, HC_topo, HS_topo):
    """
    This function returns the height of Earth's estimated topography at Lat/Long 
    coordinates
    The solution is calculated up to degree lmax in the [HC, HS] model
    """
    Sum1 = 0
    P_lm, _ = gmath.Pol_Legendre(lmax_topo, lmax_topo, cos(Lat)) # I am allowed to write that.
    for l in range (0, lmax_topo+1):
        Sum2 = 0
        for m in range (0, l+1):
            Sum2 += (HC_topo[l,m]*cos(m*Long) + HS_topo[l,m]*sin(m*Long)) * P_lm[m, l] * gmath.Normalize(l, m)
        Sum1 += Sum2

    return Sum1


def Get_Geo_Pot (R, Lat, Long,    lmax, HC, HS, lmax_topo, HC_topo, HS_topo):
    """
    This function returns the potential at given height/Lat/Long coordinates
    The solution is calculated up to degree lmax in the HC HS model
    """
    cst = gmath.Constants()
    
    R+= Get_Topo_Height (R, Lat, Long,    lmax_topo, HC_topo, HS_topo)
    Sum1 = 0
    P_lm, _ = gmath.Pol_Legendre(lmax, lmax, cos(Lat))
    for l in range (2, lmax+1):
        Sum2 = 0
        for m in range (0, l+1):
            Sum2 += (HC[l,m]*cos(m*Long) + HS[l,m]*sin(m*Long)) * P_lm[m, l] * gmath.Normalize(l, m)
        Sum1 += (cst.a_g/R)**l * Sum2

    geopot = cst.GM_g/R*(1 + Sum1)

    return geopot


def Get_Geoid_Height (R, Lat, Long,    lmax, HC, HS):
    """
    This function returns the potential at given height/Lat/Long coordinates
    The solution is calculated up to degree lmax in the HC HS model
    
    Equations from the geoid cook book
    """
    cst = gmath.Constants()    
    g_0 = gmath.Get_Normal_Gravity(Lat)
    Lat_gc = conv.geodes2geocen(Lat)
    
    R = cst.a_g 
    g_0 = cst.g 
    Lat_gc = Lat
    
    Sum1 = 0
    P_lm, _ = gmath.Pol_Legendre(lmax, lmax, sin(Lat_gc) )
    for l in range (2, lmax+1):
        Sum2 = 0
        for m in range (0, l+1):
            Sum2 += (HC[l,m]*cos(m*Long) + HS[l,m]*sin(m*Long)) * P_lm[m, l] * gmath.Normalize(l, m)
        Sum1 +=  (cst.a_g/R)**l * Sum2 

    Geo_H = cst.GM_g * Sum1 / (R*g_0)

    return Geo_H


def Get_Geoid_Height2 (R, Lat, Long,    lmax, HC, HS, lmax_topo, HC_topo, HS_topo):
    """
    This function returns the potential at given height/Lat/Long coordinates
    The solution is calculated up to degree lmax in the HC HS model
    
    Equations from the GHZ handbook
    """
    c = gmath.Constants() 
    a_g=c.a_g; GM_g=c.GM_g; # g_e=c.g 
    G=c.G; ro=c.ro;  
    
    R_e = gmath.Get_Ellipsoid_Radius(Lat)
    g_e = gmath.Get_Normal_Gravity(Lat)
#    Lat_gc = conv.geodes2geocen(Lat)
    Lat_gc = Lat
    
    Sum_geo = 0
    P_lm, _ = gmath.Pol_Legendre(lmax, lmax, sin(Lat_gc) )
    for l in range (2, lmax+1):
        Sum2 = 0
        for m in range (0, l+1):
            Sum2 += (HC[l,m]*cos(m*Long)+HS[l,m]*sin(m*Long)) * P_lm[m, l] * gmath.Normalize(l, m)
        Sum_geo +=  (a_g/R_e)**l * Sum2 

    Sum_topo = 0
    P_lm, _ = gmath.Pol_Legendre(lmax_topo, lmax_topo, cos(Lat))
    for l in range (0, lmax_topo+1):
        Sum2 = 0
        for m in range (0, l+1):
            Sum2 += (HC_topo[l,m]*cos(m*Long) + HS_topo[l,m]*sin(m*Long)) * P_lm[m, l] * gmath.Normalize(l, m)
        Sum_topo += Sum2

    Geo_H = GM_g/(R_e*g_e) * Sum_geo  -  2*pi*G*ro/g_e * (R_e*Sum_topo)**2

    return Geo_H


def Get_acceleration (R, Lat, Long,    lmax, HC, HS):
    """
    This function returns the acceleration at given height/Lat/Long coordinates
    The solution is calculated up to degree lmax in the HC HS model
    The acceleration is the gratient of the geopotential, and is calculated 
    over a distance "d" 
    """
    c = gmath.Constants()
    a_g=c.a_g; GM_g=c.GM_g; 
    
    d = 1 # m
    R_1 = R - d/2
    R_2 = R + d/2
    
    Sum1 = 0
    P_lm, _ = gmath.Pol_Legendre(lmax, lmax, cos(Lat))
    for l in range (2, lmax+1):
        Sum2 = 0
        for m in range (0, l+1):
            Sum2 += (HC[l,m]*cos(m*Long) + HS[l,m]*sin(m*Long)) * P_lm[m, l] * gmath.Normalize(l, m)
        Sum1 += (a_g/R)**l * Sum2

    PG_1 = GM_g/R_1*(1 + Sum1)
    PG_2 = GM_g/R_2*(1 + Sum1)
    
    local_acc = (PG_1 - PG_2) / d
    
    return local_acc


def Get_isopot (R, Lat, Long,    W_0, lmax, HC, HS, lmax_topo, HC_topo, HS_topo): 
    """
    This function returns the Height at given Lat/Long coordinates at which the 
    geopotential is equal to the given W_0
    The solution is calculated up to degree lmax in the HC HS model
    The approach is a dichotomy within a width of "e" m error
    """    
    de = 10
    grad = -10 # 9.81
    
    arg_after = [Lat, Long, lmax, HC, HS, lmax_topo, HC_topo, HS_topo]
    R_iso = gmath.dichotomy_grad (Get_Geo_Pot, [], R, arg_after, W_0, de, grad)
    Height = R_iso - R
    return Height # , R_iso 



# =============================================================================
# FUNCTIONS TO GENERATE DATA ARRAYs
# =============================================================================
def init_grid (tens):
    """
    Initiates the grid variables based on the number of points wanted
    """
    size_long = 1 + 36*tens
    size_lat  = 1 + 18*tens

    Line_long = np.linspace(0, 2*pi, size_long) # 0 to 360 ; must subtract 180
    Line_lat  = np.linspace(0, pi, size_lat) # 0 to 180 ; must do 90 - theta
    G_Long, G_Lat = np.meshgrid((Line_long - pi), (pi/2 - Line_lat))

    G_Grid = np.zeros((size_lat, size_long))
    
    return G_Grid, G_Long, G_Lat


def Gen_Grid (tens, Get_FUNCTION, in_args): 
    """
    This function generates a grid of the desired spherical harmonic model
    at Lat/Long coordinates
    Input: 
        tens: how large the array should be
        Get_FUNCTION: the callable function that must be used
        *inargs: the arguments to the callable function besides R, Lat, Long
    Output:
        G_Gridt: grid of Get_FUNCTION(R,Lat,Long,*in_args)
        G_Long: grid of longitudes
        G_Lat: grid of lattitudes

    """
    G_Grid, G_Long, G_Lat = init_grid(tens)   
    print(f"Making a grid with \"{Get_FUNCTION.__name__}()\", with {G_Grid.size} points")

#    if (measure == "geopot"):
    HC_topo, HS_topo = imp.Fetch_Topo_Coef()
    
    for j in range(0, G_Lat.shape[0]):
        term.printProgressBar(j+1, G_Lat.shape[0])
        Lat = pi/2 - G_Lat[j][0]
        R = gmath.Get_Ellipsoid_Radius(Lat)
        
        for i in range(0, G_Long.shape[1]):
            Long = G_Long[0][i] - pi

            G_Grid[j,i] = Get_FUNCTION(R, Lat, Long, *in_args)
          
    return G_Grid, G_Long*180/pi, G_Lat*180/pi # in degrees now



# =============================================================================
# TEST FUNCTIONS
# =============================================================================    
def Math_calc_geopot_basic(z):
    """ some function needed in TEST_plot_radius """
    G = 6.673E-11
    M = 5.975E24
    a = 6.378E6    
    P = G*M*(1/a + 1/(a+float(z)))
    return P

def TEST_plot_radius(fignum, lmax, Lat, Long, HC, HS, lmax_topo, HC_topo, HS_topo):
    """
    Plots the geopotential at given coordinates from Earth's center to the 
    surface, and beyond into space.
    """    
    R_earth = gmath.Get_Ellipsoid_Radius(Lat)
    Rs = np.linspace(95, 105, 100)
    G_Pot = np.zeros(Rs.shape)
    G_Pot_Basic = np.zeros(Rs.shape)
    
    for i in range (len(Rs)):
        G_Pot[i] = Get_Geo_Pot (Rs[i]*R_earth, Lat*pi/180, Long*pi/180, lmax, HC, HS, lmax_topo, HC_topo, HS_topo)
        G_Pot_Basic[i] = Get_Geo_Pot (Rs[i]*R_earth, Lat*pi/180, Long*pi/180, 2, HC, HS, lmax_topo, HC_topo, HS_topo)
#        G_Pot_Basic[i] = Math_calc_geopot_basic(Rs[i]*R_earth)
       
    plt.figure(fignum)
    plt.plot(Rs*R_earth, G_Pot, label=f"{Lat}-{Long}; {lmax}")
#    plt.plot(Rs, G_Pot - G_Pot_Basic, label=f"{Lat}-{Long}; {lmax}")
#    plt.plot(Rs, G_Pot_Basic, label=f"basic {Lat}-{Long}; {lmax}")
    plt.title("geopotential against the radius of the Earth, loop lmax")
    plt.xlabel("Distance from the center to the surface of the Earth (in %)")
    plt.ylabel("local value of the geopotential (m^2/s^2)")
    plt.legend(fontsize = 8)
    plt.show(block=False)


def TEST_plotGeoPot_radius():
    HC, HS = imp.Fetch_Coef() 
    HC_topo, HS_topo = imp.Fetch_Topo_Coef()
    plt.figure()
    plt.clf()
    for i in range (2, 15):
        TEST_plot_radius(1, i*2, 50, 50, HC, HS, 10, HC_topo, HS_topo)
    

def TEST_lmax_loop_line():
    """ plots the geoid height at the equator, around the world """
    plt.figure()
    plt.clf()
    plt.grid(True)
    
    HC, HS = imp.Fetch_Coef()
    HC_topo, HS_topo = imp.Fetch_Topo_Coef()    
    lmax_topo = 10

    lmaxs = np.arange(3, 25, 2)
    for lmax in lmaxs:
        Lat = pi/180 * 40
        R = gmath.Get_Ellipsoid_Radius(Lat)
        Longs = np.linspace(0, 2*pi, 91)
        
        Geo_H = np.zeros(len(Longs))
        
        for i in range(len(Longs)):
            Long = Longs[i]
            Geo_H[i] = Get_acceleration   (R, Lat, Long,    lmax, HC, HS); title_spec="Acceleration"
#            Geo_H[i] = Get_Topo_Height   (R, Lat, Long,    lmax_topo, HC_topo, HS_topo); title_spec="Topography height"
#            Geo_H[i] = Get_Geo_Pot       (R, Lat, Long,    lmax, HC, HS, lmax_topo, HC_topo, HS_topo); title_spec="GeoPot"
#            Geo_H[i] = Get_Geoid_Height  (R, Lat, Long,    lmax, HC, HS); title_spec="Geoid height"
#            Geo_H[i] = Get_Geoid_Height2 (R, Lat, Long,    lmax, HC, HS, lmax_topo, HC_topo, HS_topo); title_spec="Geoid height"
        
        Longs = (Longs-pi) * 180/pi
        plt.plot(Longs, Geo_H, label=f"{lmax}")
    
    plt.suptitle(f"{title_spec} at equator (m) vs Longitude; loop lmax")
    plt.legend()
    
 
def Get_isopot_average ():
    """ Returns the geopotential average at the surface of the ellipsoid """
#    HC, HS = imp.Fetch_Coef()
#    HC_topo, HS_topo = imp.Fetch_Topo_Coef() 
    
#    lmax_av = 29; lmax_topo_av = 48; tens_av = 10
#    Grid, _, _ = Gen_Grid (tens_av, Get_Geo_Pot, [lmax_av, HC, HS, lmax_topo_av, HC_topo, HS_topo])
#    mm = np.amin(Grid)
#    MM = np.amax(Grid)
#    W_0 = np.average(Grid)   
#    print(f"lmax_av = {lmax_av}; lmax_topo_av={lmax_topo_av}; tens={tens_av}; \n\tmm={mm}; \n\tMM={MM}; \n\tW_0={W_0}")   
  
#    mm=62499132.77072437
#    MM=62680791.364166744 
    W_0=62601662.83663869
    return W_0


def TEST_Get_isopot ():
    HC, HS = imp.Fetch_Coef()
    HC_topo, HS_topo = imp.Fetch_Topo_Coef() 
    Lat =  11
    Long =  10
    lmax = 5
    lmax_topo = 10
    
    W_0 = Get_isopot_average()
    R_e = gmath.Get_Ellipsoid_Radius(Lat)
    R_iso, height = Get_isopot(R_e, pi/180*Lat, pi/180*Long, W_0, lmax, HC, HS, lmax_topo, HC_topo, HS_topo)
    
    print(f"Average potential at {Lat} {Long} is at R={R_iso}, H={height}")



# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    
#    TEST_plotGeoPot_radius()
#    TEST_lmax_loop_line()
    TEST_Get_isopot ()    
    
    print("\nGH_generate done")
