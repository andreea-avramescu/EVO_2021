import pandas as pd
import numpy as np
import math
from radiuses import within_shelflife
from distances import haversine

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

# Define list of HOSPITALS
hospitals_list = [Hosp(*row) for row in hospitals_array] #list

hosp_for_manu, hosp_for_cryo = within_shelflife(SHELF_LIFE)
# list of manufacturing locations that have at least one hospital within shelf_life
inactive_manu = [manu for manu in range(len(locations)) if manu not in list(hosp_for_manu.keys())]
#active_cryo = list[hosp_for_cryo.keys()]

def full_locations(a_dict):
    # adds missing locations from dictionary
    full_dict = dict.fromkeys(range(len(locations)), set())
    for loc in a_dict:
        full_dict[loc] = a_dict[loc]
        
    return full_dict

# add missing locations that have 0 hospitals within shelf life
hosp_for_manu = full_locations(hosp_for_manu)
hosp_for_cryo = full_locations(hosp_for_cryo)

# nr of hospitals in range for each (manufacturing) location
# manu_range = np.array([len(hosp_for_manu[manu]) for manu in range(len(locations))])

# nr of hospitals in range for each (cryo) location
cryo_range = np.array([len(hosp_for_cryo[cryo]) for cryo in range(len(locations))])



def best_coverage(uncovered_dict):
    # get first item in dictionary
    best_pos = [list(uncovered_dict.keys())[0]]
    length = len(uncovered_dict[best_pos[0]])

    for pos in uncovered_dict:
        if len(uncovered_dict[pos]) > length:
            best_pos = [pos]
            length = len(uncovered_dict[pos])
        elif len(uncovered_dict[pos]) == length:
            best_pos.append(pos)
    
    return best_pos,length

def stochastic_coverage(uncovered_dict):
    solution = []
    
    # candidate locations with max of uncovered hospitals
    best_pos,length = best_coverage(uncovered_dict)

    while length > 0:
        # select total range (covered and uncovered hospitals)
        range_candidates = cryo_range[best_pos]
        
        # select locations with max total coverage
        max_range = max(range_candidates)
        indices = [i for i, x in enumerate(range_candidates) if x == max_range]
        
        # randomly select a location between locations with max coverage
        max_range_pos = np.array(best_pos)[indices]
        np.random.shuffle(max_range_pos)
        cryo_pos = max_range_pos[0]

        # append newly added cryo
        solution.append(cryo_pos)
        
        # exclude newly covered hospitals from dictionary of uncovered hospitals
        exclude = uncovered_dict[cryo_pos].copy()
        for pos in uncovered_dict:
            uncovered_dict[pos] -= exclude
        
        best_pos,length = best_coverage(uncovered_dict)
    
    return solution