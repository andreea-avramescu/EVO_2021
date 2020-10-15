import pandas as pd
import numpy as np

locations = pd.read_csv('C:/Users/andre/OneDrive - UOM/Data/EVO_2021/1000_largest_us_cities_raw_cost.csv')
# Merge random construction data with locations dataframe and sort by index; drop index

# Create construction costs per State for MANU and CRYO
    # Construction cost is created randomly between 700k and 1mil for manufacturing and 
    # between 100k and 250k for cryopreservation
construction_df = pd.DataFrame(locations.State.unique(),columns=['State'])
construction_df['Constr_manu'] = np.random.randint(700,1000, size = len(construction_df))*1000
construction_df['Constr_cryo'] = np.random.randint(100,250, size = len(construction_df))*1000

locations = pd.merge(locations.reset_index(),construction_df,
                     on = 'State').sort_values(['index']).drop(columns = ['index']).reset_index(drop = True)
# turn into array; City, Rank, State, and Population are not relevant anymore
loc_array = np.array(locations[['Longitude','Latitude','Cost_order','Constr_manu','Constr_cryo']])

def unique_sol(pareto_front_ind):    
    # intilize a null list 
    uniq_pareto_front = [] 
      
    # traverse for all elements
    for sol in pareto_front_ind:
        ordered_sol = [sorted(sol[0]),sorted(sol[1])]
        # check if exists in unique_list or not 
        if ordered_sol not in uniq_pareto_front: 
            uniq_pareto_front.append(ordered_sol)
    
    return uniq_pareto_front

def sol_to_df(solution):
    indexes = []
    indexes.extend(solution[0])
    indexes.extend(solution[1])
    
    coord = loc_array[indexes,:2]
    
    sol_df = pd.DataFrame(coord,columns=['Longitude','Latitude'])
    
    sol_df['Type'] = np.array(['Manufacturing']*len(solution[0]) + ['Cryopreservation']*len(solution[1])) 
    
    return sol_df

def pareto_front_coordinates(pareto_front_ind):
    final_df = pd.DataFrame(columns=['Solution','Longitude','Latitude','Type'])
    
    pareto_front_clean = unique_sol(pareto_front_ind)
    for i,sol in enumerate(pareto_front_clean):
        sol_df = sol_to_df(sol)
        sol_df.insert(0,'Solution',i)
        final_df = pd.concat([final_df, sol_df], ignore_index=True)
    
    return final_df
