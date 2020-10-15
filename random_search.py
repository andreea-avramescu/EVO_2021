import random

MAX_MANU = 10
MAX_CRYO = 5

class Solution:
    def __init__(self, manu_list, cryo_list):
        self.manu_list = manu_list
        self.cryo_list = cryo_list
        
        self.allocation = copy.deepcopy(hospitals_list)  # list of hospitals

        self.avgwait_time = 0.0        # objective_1
        self.total_cost = 0.0        # objective_2
        self.uncovered = 0.0          # objective_3

    def calc_objectives(self):   # default is haversine distance function (in km)
                                                                # and 110 km/h speed
        if self.avgwait_time == 0:
            manu_cover = set()
            for manu in self.manu_list:
                # add manufacturing constuction cost
                self.total_cost += loc_array[manu,3]
                
                # reunion of hospitals within shelf-life of manu locations
                manu_cover |= hosp_for_manu[manu]
            
            cryo_cover = set()
            for cryo in self.cryo_list:
                # add cryo constuction cost
                self.total_cost += loc_array[cryo,4]
                
                # reunion of hospitals within shelf-life of cryo locations
                cryo_cover |= hosp_for_cryo[cryo]
            
            # remove hospitals covered by manu
            cryo_cover -= manu_cover
            
            # total coverage (hospitals covered by manufacturing or cryo)
            total_cover = manu_cover | cryo_cover
            
            # calculate coverage (objective #3)
            self.uncovered = 1 - len(total_cover)/len(self.allocation)
            
            total_time = 0
            total_demand = 0
            # Allocation and objective functions for manu_covered hospitals (MANUFACTURING)
            for hosp in manu_cover:
                hospital = self.allocation[hosp]
                
                hospital.manu = hospital.preference(self.manu_list)[0]  # closest manufacturing
                
                hospital.cost = loc_array[hospital.manu,2] * hospital.demand
                self.total_cost += hospital.cost
                
                # travel time is a RETURN ROUTE
                hospital.time = DIST(hospital.x,hospital.y,
                                        loc_array[hospital.manu,0],loc_array[hospital.manu,1]) / SPEED * 2
                
                total_time += hospital.time * hospital.demand
                total_demand += hospital.demand
            
            
            # Allocation and objective functions for cryo_covered hospitals (CRYOPRESERVATION)
            for hosp in cryo_cover:
                hospital = self.allocation[hosp]
                
                hospital.manu = hospital.preference(self.manu_list)[0]  # closest manufacturing
                hospital.cryo = hospital.preference(self.cryo_list)[0]  # closest cryo
                
                # multiply cost order (per state) * hospital demand
                hospital.cost = loc_array[hospital.manu,2] * hospital.demand
                self.total_cost += hospital.cost
                
                # travel time is a H->C->M->H ROUTE
                hospital.time = (DIST(hospital.x,hospital.y,
                                        loc_array[hospital.cryo,0],loc_array[hospital.cryo,1]) + 
                                 DIST(loc_array[hospital.cryo,0],loc_array[hospital.cryo,1],
                                        loc_array[hospital.manu,0],loc_array[hospital.manu,1]) +
                                 DIST(hospital.x,hospital.y,
                                        loc_array[hospital.manu,0],loc_array[hospital.manu,1])) / SPEED
                
                total_time += hospital.time * hospital.demand
                total_demand += hospital.demand
            
            # demand-weighted avg waiting time
            self.avgwait_time = total_time / total_demand

    def __repr__(self):
        return str(self.manu_list)

# create random solution of MANUFACTURING and CRYOPRESERVATION facilities
def createRandSol(max_manu = MAX_MANU, max_cryo = MAX_CRYO):
    M = random.randint(1,max_manu)
    C = random.randint(1,max_cryo)
    
    manu_list = random.sample(range(len(loc_array)), M)
    cryo_list = random.sample(range(len(loc_array)), C)
    
    # Ensure no common location between M and C
    while set(manu_list) & set(cryo_list) != set():
        manu_list = random.sample(range(len(loc_array)), M)
        cryo_list = random.sample(range(len(loc_array)), C)
    
    return sorted(manu_list),sorted(cryo_list)

def RandomSearchFLP(N):
    pareto_front = []
    fitness = []
    
    for i in range(N):
        manu_list,cryo_list = createRandSol()
        
        # ensure solution is not repeated in pareto_front
        while [manu_list,cryo_list] in pareto_front:
            manu_list,cryo_list = createRandSol()
        
        sol = Solution(manu_list,cryo_list)
        sol.calc_objectives()
        
        # ensure demand met by solution is non-zero
        while sol.uncovered == 1:
            manu_list,cryo_list = createRandSol()
            sol = Solution(manu_list,cryo_list)
            sol.calc_objectives()
        
        new_fit = np.array([sol.avgwait_time,sol.total_cost,sol.uncovered])
        dominated = False
        
        for i,fit in enumerate(fitness):
            # if new_fit dominates any of the fits in the pareto front, the dominated old fits are discarded
            while all(fit>new_fit):
                del pareto_front[i]
                del fitness[i]
                if i<len(fitness):
                    fit = fitness[i]
                else:
                    break
            
            # if new_fit is dominated by any of the fits in the pareto front, the solution is discarded
            if all(fit<new_fit):
                dominated = True
                break
        
        if not dominated:
            pareto_front.append([manu_list,cryo_list])
            fitness.append(new_fit)
    
    return pareto_front, fitness