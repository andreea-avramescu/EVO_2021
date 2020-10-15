import pandas as pd 
import numpy as np
import math
import random
from distances import haversine
hospitals = pd.read_csv('C:/Users/andre/OneDrive - UOM/Data/EVO_2021/treatment_centers.csv') # turn into array
hospitals_array = np.array(hospitals[['Longitude','Latitude','Demand']])  # Hospital names are irrelevant

locations = pd.read_csv('C:/Users/andre/OneDrive - UOM/Data/EVO_2021/1000_largest_us_cities_raw_cost.csv')

# Create construction costs per State for MANU and CRYO
    # Construction cost is created randomly between 700k and 1mil for manufacturing and 
    # between 100k and 250k for cryopreservation
construction_df = pd.DataFrame(locations.State.unique(),columns=['State'])
construction_df['Constr_manu'] = np.random.randint(700,1000, size = len(construction_df))*1000
construction_df['Constr_cryo'] = np.random.randint(100,250, size = len(construction_df))*1000

# Merge random construction data with locations dataframe and sort by index; drop index
locations = pd.merge(locations.reset_index(),construction_df,
                     on = 'State').sort_values(['index']).drop(columns = ['index']).reset_index(drop = True)
# turn into array; City, Rank, State, and Population are not relevant anymore
loc_array = np.array(locations[['Longitude','Latitude','Cost_order','Constr_manu','Constr_cryo']])

# Hospitals allocation
class Hosp:
    def __init__(self, x, y, demand):
        self.x = x
        self.y = y
        self.demand = demand
        
        self.time = 0.0
        self.cost = 0.0
        
        #self.covered = True
        self.cryo = None
        self.manu = None

    def distance(self, p2, func = haversine):
        return func(self.x, self.y, p2.x, p2.y)

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def preference(self, loc_list, func = haversine):
        locs = np.array(loc_list)

        H_x = np.full(len(locs), self.x)
        H_y = np.full(len(locs), self.y)
        L_x = loc_array[locs,0]  # longitude
        L_y = loc_array[locs,1]  # latitude

        dist  = func(H_x,H_y,L_x,L_y)

        return locs[np.argsort(dist)]

# Define list of HOSPITALS
hospitals_list = [Hosp(*row) for row in hospitals_array] #list
############################### HYPERPARAMETERS ##############################
##############################################################################

# INSERT SHELF LIFE HERE (in hours)
SHELF_LIFE = 12

POPULATION = 100
PARENTS = math.ceil(POPULATION/4)

DIST = haversine
SPEED = 110       # in km

##############################################################################
##############################################################################

# create random solution of manufacturing facilities
def createManuSol(max_manu = 10):
    M = random.randint(1,max_manu) 
    solution = random.sample(range(len(loc_array)), M)
    return solution

# Calcute radiuses for ALL candidate locations based on shelf-life
def within_shelflife(shelf_life):
    hospitals['del'] = 1 # fake identical column for merging long and lat between
    locations['del'] = 1   # locations and  hospitals
    hospitals_sl = hospitals[['del','Longitude','Latitude']].merge(locations[['del','Longitude','Latitude']],
                                                          on='del', suffixes=('_H', '_L')).drop('del', axis=1)
    hospitals.drop('del', axis=1, inplace = True)
    locations.drop('del', axis=1, inplace = True)
    
    # Calculate distance and order time for all hospitals with each candidate location
    dist_km = DIST(*np.array(hospitals_sl).T)
    order_time = dist_km / SPEED
    
    # MANUFACTURING
    # returns one dimensional coordinates that satisfy shelf life constraints
        # divided by 2 since for manufacturing the shelf life needs to be a return route
    good_locations = np.where(order_time <= shelf_life/2)
    
    # converts one dimensional array to pairs of hospital-manufacturing that satisfy shelf life
    pairs = np.asarray(np.unravel_index(good_locations, (len(hospitals),len(locations))))
    pairs = pairs.reshape(pairs.shape[0],pairs.shape[-1])
    
    # convert to dataframe
    pairs_df = pd.DataFrame(pairs.T, columns = ['Hosp','Manu'])
    # aggregate for each location the hospitals that are within the shelf-life if 
        # a MANU were to be placed there
    hospitals_for_manu = pairs_df.groupby('Manu')['Hosp'].apply(set).to_dict()
    
    # CRYO
    # returns one dimensional coordinates that satisfy shelf life constraints
        # no return needed as shelf-life is deactivated once product is frozen
    good_locations = np.where(order_time <= shelf_life)
    
    # converts one dimensional array to pairs of hospital-manufacturing that satisfy shelf life
    pairs = np.asarray(np.unravel_index(good_locations, (len(hospitals),len(locations))))
    pairs = pairs.reshape(pairs.shape[0],pairs.shape[-1])
    
    # convert to dataframe
    pairs_df = pd.DataFrame(pairs.T, columns = ['Hosp','Cryo'])
    # aggregate for each location the hospitals that are within the shelf-life if 
        # a CRYO were to be placed there
    hospitals_for_cryo = pairs_df.groupby('Cryo')['Hosp'].apply(set).to_dict()

    return hospitals_for_manu, hospitals_for_cryo