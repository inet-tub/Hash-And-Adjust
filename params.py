
class Params:
    """
    For the experiments, the params are set manually before executing the script
    Used params for each experiment can be found at the beginning of the experimentation file
    """
    def __init__(self):
        self.exp_type = "temp"              # ctr, temp, caida
        self.temp_p = "0.75"                # if exp_type="temp": e.g. 0.15, 0.3, 0.45, 0.6, 0.75, 0.9
        self.algorithm = "All"              # AdjustHash, Static, WBD; or All -> executes all 3
        self.hash_f = "sha"                 # sha, 5k, pow2
        self.addit_augm = "4"               # 4, 7, 10 are typical params
        self.stale_time = 200               # in minutes
        self.init_servers = 20              # number of servers in datastructure
        self.size_dataset = 100000          # number of requests 
        self.n_items = 10000                # number of items
        self.server_ins_del = True          # true means that servers are deleted and new ones inserted
        self.random_serv_ins_del = False    # insert/delete servers randomly if True. If False: fetch from file
        self.delete_items = True            # serve delete-events, deleting items while serving the requests
        self.serv_ins_freq = 200            # frequency of server insertion in minutes
        self.serv_del_freq = 200            # frequency of server deletion in minutes
        self.initial_occup_factor = 1       # server occupation at initialization (before serving requests) [0-1]
        self.unbounded_capacity = False     # True if capacity of servers should be infinite: always=False in paper

    def set_n_servers(self, n):
        self.init_servers = n

    def set_n_items(self, n):
        self.n_items = n

    def set_size_dataset(self, n):
        self.size_dataset = n

param = Params()