"""

@authors:

# =============================================================================
 Information: 

    The functions in this script are used to import and fetch values and arrays 
    from text files, or export and create array files
        
# =============================================================================
"""

# =============================================================================
# LIBRARIES
# =============================================================================
import numpy as np
from numpy import pi, sin, cos

from GH_convert import cart2sphA


data_path = "../data"

# =============================================================================
# FUNCTIONS TO STORE FILES
# =============================================================================
def Store_array(data, title):  
    """
    Stores an array into a text file that can later be imported again
    
    Input: 
        data : the array in question
        title : a string, of the desired title for the file. 
                Must incluse ".txt"
    To import use: 
        data = np.loadtxt(title)
    
    """   
    length = len(data)
    file = open(title, "w+")
    for n in range (len(data)):
        print("Writing", n, "\tof", length-1)
        for m in range(len(data[0])):
            file.write(str(data[n, m]))
            file.write("\t")
        file.write("\n")
    file.close()
    print("\n\tWriting done\n")


# =============================================================================
# FUNCTIONS - GEODESY
# =============================================================================
def Get_Radius(angle):
    """
    Returns the radius of the reference elipsoid in meters
    
    Input: 
        angle: latitude, inclination from the z axis in degrees
    Output: 
        R: Radius in meters
        
    """    
    theta = pi/2 -angle
    Radius_eq = 6378137 # m
    Radius_pol = 6356752.3142 # m
    a = Radius_eq
    b = Radius_pol     
    deno = np.sqrt(a**2*sin(theta)**2 + b**2*np.cos(theta)**2)
    R = a*b/deno    
    return R


# =============================================================================
# FUNCTIONS FOR COORDINATES MANIPULATION
# =============================================================================
def Fetch_Pos(file_name, days = 0.7):
    """
    Imports coordinates from file_name text file (generated from GMAT)
    
    Input:
        file_name: well, the file's name! remove all header text
        days: what time duration the outplut file should correspond to 
              regardless of the sampling rate
    Output: 
        Pos: The position of the satellite in spherical coordinates
        Time: Associated time sampling of each position
    
    """
    Eph = np.loadtxt(f"{data_path}/{file_name}")
    t = np.array(Eph[:,0]) #time in seconds
    x = np.array(Eph[:,1]) #  \
    y = np.array(Eph[:,2]) #  | cordinates, in km
    z = np.array(Eph[:,3]) # /
    dt = np.int(t[1]*100)/100
    L = np.int(days*(86400/dt))
    # convert coord system and shorten array if needed 
    pts = np.transpose(np.array([x,y,z])) 
    if L >= len(pts):
        L = len(pts)
    Pos = cart2sphA(pts[:L]) 
    Time = t[:L]
    
    return Pos, Time


# =============================================================================
# FUNCTIONS TO GENERATE ACCELERATION ARRAYS
# =============================================================================
def Fetch_Coef():
    """
    returns the official spherical harmonic coefficients I downloaded
    Data originally extracted from : Coeff_Height_and_Depth_to2190_DTM2006.txt
    These coefs are already normalized
    files exist with a degree up to lmax = 2190
    """    
    data_path = "../data"
    HC = np.loadtxt(f"{data_path}/GeoPot_Coef_cos_deg30.txt")
    HS = np.loadtxt(data_path+"/GeoPot_Coef_sin_deg30.txt")
    return HC, HS


# =============================================================================
# TEST FUNCTIONS
# =============================================================================
  
# =============================================================================
# MAIN 
# =============================================================================
if __name__ == '__main__':
    HC, HS = Fetch_Coef()
    print("\nGH_import done")
