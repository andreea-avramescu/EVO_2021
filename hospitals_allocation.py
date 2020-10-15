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