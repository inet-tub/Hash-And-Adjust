import datetime
import json
import copy

from params import param
from implementation.circle import Circle
from data_handling.real_data_handler import get_n_items, fetch_ctr_seq_time_100k, fetch_simple_seq
from data_handling.temporal_handler import fetch_temp_seq
from implementation.push_down_algo import Push_down_algo
from implementation.static_algo import Static_algo
from implementation.push_down_algo_adj import Push_down_algo_adj
import data_handling.json_handler as jh
import implementation.plotter as pl
import implementation.algo_utils as au

def run_paper_experiment_1():
    capacities = ["4"]
    temp_ps = ["0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.75", "0.8", "0.9"]
    param.exp_type = "temp"
    param.algorithm = "All"
    param.set_n_servers(20)
    param.set_n_items(10000)
    param.set_size_dataset(100000)
    jh.check_dataset()
    for c in capacities:
        param.addit_augm = c
        for p in temp_ps:
            param.temp_p = p
            run_experiment_temp()
    pl.sum_results_all_ps()     # puts all temp-results in one file
    param.set_n_servers(200)    
    run_server_occ()            
    run_server_occ(mult=True)
    run_server_occ(infin=True)

def run_paper_experiment_2():
    n_servers_params = [20, 40, 60, 80, 100, 150]
    param.addit_augm = "4"
    param.exp_type = 'ctr'
    param.set_n_items(1029)
    param.set_size_dataset(100000)
    for n in n_servers_params:
        param.set_n_servers(n)
        jh.generate_serv_ins_del_ctr()
        run_experiment_real()

def run_paper_experiment_3():
    stale_time_params = [50, 100, 150, 200, 300]
    param.addit_augm = "4"
    param.exp_type = 'ctr'
    param.set_n_servers(20)
    param.set_n_items(1029)
    param.set_size_dataset(100000)
    for s in stale_time_params:
        param.stale_time=s
        run_experiment_real()

def run_experiment_real_diff_c():
    capacities = ["1", "2", "4", "8", "16"]
    param.exp_type = "caida"
    param.algorithm = "All"
    param.set_n_items(5000)
    param.set_size_dataset(150000)
    param.set_n_servers(50)
    param.delete_items = False
    res_dict = {}
    for c in capacities:
        param.addit_augm = c
        run_experiment_real_with_res(res_dict)
    with open(f"results/{param.exp_type}_results_n{param.init_servers}_f{param.serv_ins_freq}_s{param.stale_time}.json", "w") as fp:
        json.dump(res_dict, fp)

def run_server_occ(mult=False, infin=False):
    """
    Test server occupancy with various capacity on temporal data
    or on real data
    """
    serve_seq_first = True
    param.addit_augm = "4"
    param.exp_type = "temp"             # used in paper
    param.initial_occup_factor = 1      # load all items initially
    jh.check_dataset()
    if param.exp_type == "temp":
        temp_ps = ["0.75"]
        param.set_size_dataset(100000)
        param.set_n_items(10000)
        sequences = fetch_temp_seq()
        for p in temp_ps:
            param.temp_p = p
            for seq in sequences:
                sequence = list(sequences[seq].values())
                if not seq.startswith(p):
                    continue
                m_items = int(get_n_items(seq))
                print(f"Running on seq {seq}, # items: {m_items}, # req: {len(sequence)}")
                if mult:
                    server_capacity = m_items / param.init_servers * param.initial_occup_factor * 1.25
                    param.addit_augm = "*1.25"
                elif infin:
                    server_capacity = m_items * 2
                    param.addit_augm = "inf"
                else:
                    server_capacity = m_items / param.init_servers * param.initial_occup_factor + int(param.addit_augm)
                print(f"Server capacity: {int(server_capacity)}")
                preloading_items = au.get_preloaded_items(sequence.copy())
                static_c = Circle(id=0, n_servers=param.init_servers, m_items=m_items)
                static_c.server_capacity = int(server_capacity)
                static_c.init_servers(preloaded_items=preloading_items.copy())
                if serve_seq_first:
                    lim = 25000
                    if mult or infin:
                        algo = Static_algo(static_c)
                    else:
                        algo = Push_down_algo(static_c)
                    algo.serve_sequence(sequence=sequence.copy(), type="temp", max_served_events=lim)
                record_circle_occupation(static_c, lim, mult=mult, infin=infin)
    else:
        if param.exp_type == "ctr":
            seq_data = fetch_ctr_seq_time_100k()
            param.set_size_dataset(100000)
            stop_after = 25000
        else:
            raise Exception("Invalid exp-type")
        seq = seq_data[0]
        sequence = seq_data[1]
        m_items = int(get_n_items(seq))
        print(f"Running on seq {seq}, # items: {m_items}, # req: {len(sequence)}")
        if mult:
            server_capacity = m_items / param.init_servers * param.initial_occup_factor * 1.25
            param.addit_augm = "*1.25"
        elif infin:
            server_capacity = m_items * 2
            param.addit_augm = "inf"
        else:
            server_capacity = m_items / param.init_servers * param.initial_occup_factor + int(param.addit_augm)
        print(f"Server capacity: {int(server_capacity)}")
        preloading_items = au.get_preloaded_items(sequence.copy())
        c1 = Circle(id=1, n_servers=param.init_servers, m_items=m_items)
        c1.server_capacity = int(server_capacity)
        c1.init_servers(preloaded_items=preloading_items.copy())
        lim = None
        if serve_seq_first:
            lim = stop_after        # add if we want to stop serving sequence after a bit
            if mult or infin:
                algo = Static_algo(c1)
            else:
                algo = Push_down_algo(c1)
            algo.serve_sequence(sequence=sequence.copy(), type=param.exp_type, max_served_events=lim)
        record_circle_occupation(c1, lim, mult=mult, infin=infin)

def run_experiment_temp():
    """
    Run a temporal experiment for one given temporal parameter and one n_servers parameter
    """
    capacities = [param.addit_augm]
    server_n = [param.init_servers]
    tmp_p = param.temp_p
    res_dict = {}
    sequences = fetch_temp_seq()
    for seq in sequences:
        sequence = list(sequences[seq].values())
        if not seq.startswith(tmp_p+"_"):
           continue
        m_items = int(get_n_items(seq))
        print(f"Running on seq {seq}, # items: {m_items}, # req: {len(sequence)}")
        res_dict[seq] = {}
        for c in capacities:
            res_dict[seq][c] = {}
            for n in server_n:
                res_dict[seq][c][n] = {}
                n_servers = n
                if param.unbounded_capacity:
                    server_capacity = m_items * 2
                elif c == "*1.25":
                    server_capacity = m_items / n_servers * 1.25 * param.initial_occup_factor
                else:
                    server_capacity = int((m_items/n_servers + int(c))*param.initial_occup_factor)
                if param.algorithm == "AdjustHash" or param.algorithm == "All":
                    algo_c = Circle(id=0, n_servers=n_servers, m_items=m_items, serv_ins_del=True)
                    algo_c.server_capacity = int(server_capacity)
                if param.algorithm == "WBL" or param.algorithm == "All":
                    wbl_c = Circle(id=2, n_servers=n_servers, m_items=m_items, serv_ins_del=True)
                    wbl_c.server_capacity = int(m_items / n_servers * 1.25 * param.initial_occup_factor)   # wbl
                print("Runnning for c=" + c + ", server_n="+ str(n)+", server capacity = " + str(server_capacity))
                logger = open("results/n"+str(param.init_servers)+"_h"+str(m_items)+"_m"+str(len(sequence))+
                              "_p"+tmp_p+"_s"+str(param.stale_time)+"_f"+str(param.serv_ins_freq)+"_res.txt", 'a')
                logger.write(f"Running on seq {seq}, # items: {m_items}, # req: {len(sequence)}, stale: {param.stale_time}"
                             f", serv_ins_freq: {param.serv_ins_freq}, serv_del_freq: {param.serv_del_freq}"
                             f", \n")
                logger.write("Starting at " + str(datetime.datetime.now())+"\n")
                logger.write(f"Additive capacity= {c} , server capacity= {server_capacity}, n_servers= {n_servers} \n")
                preloading_items = au.get_preloaded_items(sequence.copy())
                if param.algorithm == "AdjustHash" or param.algorithm == "All":
                    algo_c.init_servers(preloaded_items=preloading_items)
                    algo = Push_down_algo(algo_c)
                    if param.unbounded_capacity:
                        algo.serve_sequence_unbounded_cap(sequence=sequence.copy(), type="temp")
                        record_circle_occupation(algo_c)
                    else:
                        algo.serve_sequence(sequence=sequence.copy(), type="temp")
                    res_dict[seq][c][n]["algo_access"] = algo.access_cost
                    res_dict[seq][c][n]["algo_reconfig"] = algo_c.reconfig_cost
                    res_dict[seq][c][n]["algo_max_acc"] = algo.max_iteration
                    res_dict[seq][c][n]["algo_mean_serv_c"] = sum(algo_c.server_c_record) / len(algo_c.server_c_record)
                    logger.write(f"Algo access-cost: {algo.access_cost}\n"
                    f"Algo reconfig-cost: {algo_c.reconfig_cost}\n"
                    f"Items-stats: \n"
                    f"algo-deleted: {algo.sum_del_items}, "
                    f"algo-reinserted: {algo.sum_reinserted_items}\n")
                if param.algorithm == "WBL" or param.algorithm == "All":
                    wbl_c.init_servers(preloaded_items=preloading_items)
                    wbl_algo = Static_algo(wbl_c)
                    if param.unbounded_capacity:
                        wbl_algo.serve_sequence_unbounded_cap(sequence=sequence.copy(), type="temp")
                        record_circle_occupation(wbl_c)
                    else:
                        wbl_algo.serve_sequence(sequence=sequence.copy(), type="temp")
                    res_dict[seq][c][n]["wbl_access"] = wbl_algo.access_cost
                    res_dict[seq][c][n]["wbl_reconfig"] = wbl_c.reconfig_cost
                    res_dict[seq][c][n]["wbl_max_acc"] = wbl_algo.max_iteration
                    res_dict[seq][c][n]["wbl_mean_serv_c"] = sum(wbl_c.server_c_record) / len(wbl_c.server_c_record)
                    logger.write(f"wbl access-cost: {wbl_algo.access_cost} \n"
                     f"wbl reconfig-cost: {wbl_c.reconfig_cost}\n"
                     f"Items-stats: \n"
                     f"wbl-deleted: {wbl_algo.sum_del_items}, "
                     f"wbl-reinserted: {wbl_algo.sum_reinserted_items}\n")
                    if param.unbounded_capacity and param.show_circle_occup:
                        record_circle_occupation(wbl_c)
                logger.write("Finished at " + str(datetime.datetime.now())+"\n\n")
                logger.close()
        print(res_dict)
        dir = "results"
        jh.add_temp_res_to_json(path=dir+"/n"+str(param.init_servers)+"_h"+str(m_items)+"_m"+str(len(sequence))+
                              "_p"+tmp_p+"_s"+str(param.stale_time)+"_f"+str(param.serv_ins_freq)
                                     +"_alg"+param.algorithm+"_results.json", data=res_dict)


def record_circle_occupation(circle, max_served_events=param.size_dataset, mult=False, infin=False):
    occ = {}
    s = circle.root
    sum = 0
    for n in range(0, circle.n_servers):
        occ[s.id] = s.get_current_occupation()
        sum += s.get_current_occupation()
        s = s.child_pointer
    if param.exp_type == "temp":
        if param.unbounded_capacity:
            with open(f"results/circle_inf_h{param.hash_f}_lim{max_served_events}_p{param.temp_p}_occupation.json", "w") as fp:
                json.dump(occ, fp)
        else:
            if mult:
                with open(f"results/circle_1.25_h{param.hash_f}_lim{max_served_events}_p{param.temp_p}_n{param.init_servers}_occupation.json", "w") as fp:
                    json.dump(occ, fp)
            elif infin:
                with open(f"results/circle_infin_h{param.hash_f}_lim{max_served_events}_p{param.temp_p}_n{param.init_servers}_occupation.json", "w") as fp:
                    json.dump(occ, fp)
            else:
                with open(f"results/circle_c{param.addit_augm}_h{param.hash_f}_lim{max_served_events}_p{param.temp_p}_n{param.init_servers}_occupation.json", "w") as fp:
                    json.dump(occ, fp)
    elif param.exp_type == "ctr" or param.exp_type == "fb":
        if param.unbounded_capacity:
            with open(f"results/circle_inf_h{param.hash_f}_lim{max_served_events}_{param.exp_type}_occupation.json", "w") as fp:
                json.dump(occ, fp)
        else:
            if mult:
                with open(f"results/circle_1.25_h{param.hash_f}_lim{max_served_events}_{param.exp_type}_occupation.json", "w") as fp:
                    json.dump(occ, fp)
            elif infin:
                with open(f"results/circle_infin_h{param.hash_f}_lim{max_served_events}_{param.exp_type}_occupation.json", "w") as fp:
                    json.dump(occ, fp)
            else:
                with open(f"results/circle_c{param.addit_augm}_h{param.hash_f}_lim{max_served_events}_{param.exp_type}_occupation.json", "w") as fp:
                    json.dump(occ, fp)
    else:
        raise Exception("Please rerun with valid exp_type param")
        
def run_experiment_real_with_res(res_dict):
    if param.exp_type == "ctr":
        param.size_dataset = 100000
        seq_data = fetch_ctr_seq_time_100k()
        logger = open("results/ctr_results.txt", 'a')
        m_items = 1029
        serv_ins_del = True
    elif param.exp_type == "caida":
        param.size_dataset = 150000
        seq_data = fetch_simple_seq('data/caida_grouped.csv')
        logger = open("results/caida_results.txt", 'a')
        m_items = 5000
        serv_ins_del = False

    seq_name = seq_data[0]
    sequence = seq_data[1]
    capacities = [param.addit_augm]
    server_n = [param.init_servers]
    if not m_items:
        m_items = int(get_n_items(seq_name))
    print("m_items = " + str(m_items))
    for c in capacities:
        res_dict[c] = {}
        for n in server_n:
            res_dict[c][n] = {}
            n_servers = n
            algo_c = Circle(id=0, n_servers=n_servers, m_items=m_items, serv_ins_del=serv_ins_del)
            wbl_c = Circle(id=2, n_servers=n_servers, m_items=m_items, serv_ins_del=serv_ins_del)
            server_capacity = m_items / n_servers + int(c)
            algo_c.server_capacity = int(server_capacity)
            wbl_c.server_capacity = int(server_capacity)
            print("Runnning for c=" + c + ", server_n="+ str(n)+", server capacity = " + str(algo_c.server_capacity))
            logger.write(f"\nRunning for c = {c} , server capacity = {algo_c.server_capacity}, n_servers = {n_servers} \n")
            logger.write("Starting at " + str(datetime.datetime.now()) + "\n")
            preloading_items = au.get_preloaded_items(sequence.copy())
            
            if param.algorithm == "AdjustHash" or param.algorithm == "All":
                algo_c.init_servers(preloaded_items=preloading_items)
                algo = Push_down_algo(algo_c)
                algo.serve_sequence(sequence.copy(), type=param.exp_type, max_served_events=param.size_dataset)
                res_dict[c][n]["algo_access"] = algo.access_cost
                res_dict[c][n]["algo_max_acc"] = algo.max_iteration
            
            if param.server_ins_del and algo_c.server_c_record:
                res_dict[c][n]["algo_mean_serv_c"] = sum(algo_c.server_c_record) / len(algo_c.server_c_record)
                
            if param.algorithm == "WBL" or param.algorithm == "All":
                wbl_c.init_servers(preloaded_items=preloading_items)
                wbl_algo = Static_algo(wbl_c)
                wbl_algo.serve_sequence(sequence.copy(), type=param.exp_type, max_served_events=param.size_dataset)
                res_dict[c][n]["wbl_access"] = wbl_algo.access_cost
                res_dict[c][n]["wbl_max_acc"] = wbl_algo.max_iteration
            if param.server_ins_del and wbl_c.server_c_record:
                res_dict[c][n]["wbl_mean_serv_c"] = sum(wbl_c.server_c_record) / len(wbl_c.server_c_record)
            logger.write(f"Algo: {algo.access_cost}, "
                         f"WBL: {wbl_algo.access_cost}\n")
            logger.write("Finished at " + str(datetime.datetime.now()) + "\n")
    logger.close()
    
def run_experiment_real():
    if param.exp_type == "ctr":
        param.size_dataset = 100000
        seq_data = fetch_ctr_seq_time_100k()
        logger = open("results/ctr_results.txt", 'a')
        m_items = 1029
        serv_ins_del = True
    elif param.exp_type == "caida":
        param.size_dataset = 150000
        seq_data = fetch_simple_seq('data/caida_grouped.csv')
        logger = open("results/caida_results.txt", 'a')
        m_items = 5000

    seq_name = seq_data[0]
    sequence = seq_data[1]
    capacities = [param.addit_augm]
    server_n = [param.init_servers]
    if not m_items:
        m_items = int(get_n_items(seq_name))
    print("m_items = " + str(m_items))
    res_dict = {}
    for c in capacities:
        res_dict[c] = {}
        for n in server_n:
            res_dict[c][n] = {}
            n_servers = n
            algo_c = Circle(id=0, n_servers=n_servers, m_items=m_items, serv_ins_del=serv_ins_del)  # algo_c = 10,000 req
            wbl_c = Circle(id=2, n_servers=n_servers, m_items=m_items, serv_ins_del=serv_ins_del)
            if param.unbounded_capacity:
                server_capacity = m_items * 2
            elif c == "*1.25":
                server_capacity = m_items / n_servers * 1.25 * param.initial_occup_factor
            else:
                server_capacity = (m_items / n_servers + int(c)) * param.initial_occup_factor
            if param.algorithm == "H&A" or param.algorithm == "All":
                algo_c.server_capacity = int(server_capacity)
            if param.algorithm == "WBL" or param.algorithm == "All":
                wbl_c.server_capacity = int(m_items / n_servers * 1.25 * param.initial_occup_factor)
            print("Runnning for c=" + c + ", server_n="+ str(n)+", server capacity = " + str(algo_c.server_capacity))
            logger.write(f"\nRunning for c = {c} , server capacity = {algo_c.server_capacity}, n_servers = {n_servers} \n")
            logger.write("Starting at " + str(datetime.datetime.now()) + "\n")
            preloading_items = au.get_preloaded_items(sequence.copy())
            
            if param.algorithm == "AdjustHash" or param.algorithm == "All":
                algo_c.init_servers(preloaded_items=preloading_items)
                algo = Push_down_algo(algo_c)
                algo.serve_sequence(sequence.copy(), type=param.exp_type, max_served_events=None)
                res_dict[c][n]["algo_access"] = algo.access_cost
                res_dict[c][n]["algo_max_acc"] = algo.max_iteration
            
            if param.server_ins_del:
                res_dict[c][n]["algo_mean_serv_c"] = sum(algo_c.server_c_record) / len(algo_c.server_c_record)
            if param.algorithm == "WBL" or param.algorithm == "All":
                wbl_c.init_servers(preloaded_items=preloading_items)
                wbl_algo = Static_algo(wbl_c)
                wbl_algo.serve_sequence(sequence.copy(), type=param.exp_type, max_served_events=None)
                res_dict[c][n]["wbl_access"] = wbl_algo.access_cost
                res_dict[c][n]["wbl_max_acc"] = wbl_algo.max_iteration
            if param.server_ins_del:
                res_dict[c][n]["wbl_mean_serv_c"] = sum(wbl_c.server_c_record) / len(wbl_c.server_c_record)
            logger.write(f"Algo: {algo.access_cost}, "
                         f"WBL: {wbl_algo.access_cost}\n")
            logger.write("Finished at " + str(datetime.datetime.now()) + "\n")
    with open(f"results/{param.exp_type}_results_n{param.init_servers}_f{param.serv_ins_freq}_s{param.stale_time}.json", "w") as fp:
        json.dump(res_dict, fp)
    logger.close()

def run_experiment_real_failure_check():
    param.exp_type = "caida"     # 40656 nodes, 311718 req
    param.size_dataset = 311718
    param.serv_ins_del = False
    param.init_servers = 50
    param.delete_items = False
    seq_data = fetch_simple_seq('data/caida_grouped.csv')
    logger = open("results/caida_results.txt", 'a')

    seq_name = seq_data[0]
    sequence = seq_data[1]
    orig_seq = sequence.copy()
    m_items = 5000
    server_capacity = 100
    max_served_events= 150000
    server_n = [param.init_servers]

    print("m_items = " + str(m_items))
    items_set = set()
    new_seq = []
    if param.exp_type == "ctr":
        for r in sequence:
            if len(items_set) < m_items:
                items_set.add(r[0])
            else:
                print(f"Sequence counts {len(items_set)} items")
                break
        for r in sequence:
            if r[0] in items_set:
                new_seq.append(r)
        print(f"# requests in seq = {len(new_seq)}")
        sequence = new_seq
    else:
        pass    # not ctr, no timestamp 
    res_dict = {}
    c = server_capacity
    res_dict[c] = {}
    for n in server_n:
        res_dict[c][n] = {}
        n_servers = n
        algo_c = Circle(id=0, n_servers=n_servers, m_items=m_items, serv_ins_del=param.serv_ins_del)
        algo_c.server_capacity = int(server_capacity)
        print("Runnning for c=" + str(c) + ", server_n="+ str(n)+", server capacity = " + str(algo_c.server_capacity))
        logger.write(f"\nRunning for c = {c} , server capacity = {algo_c.server_capacity}, n_servers = {n_servers} \n")
        logger.write("Starting at " + str(datetime.datetime.now()) + "\n")
        preloading_items = au.get_preloaded_items(sequence.copy())
        algo_c.init_servers(preloaded_items=preloading_items)
        algo = Push_down_algo_adj(circle=algo_c, check_failure=True)        # run this one until failure
        full_circle = algo.serve_sequence(sequence.copy(), type=param.exp_type, max_served_events=max_served_events)
        if not full_circle:
            raise Exception("No circle with failure returned")
        full_circle_algo = copy.deepcopy(full_circle)
        full_circle_wbl = copy.deepcopy(full_circle)
        full_circle_algo.stop_checking_failure()
        full_circle_wbl.stop_checking_failure()
        res_dict["Failure_at"] = full_circle.failed_at

        # choose <points> fairly distributed points in interval [failed_at, m_items]
        points = 10
        diff = m_items - full_circle.failed_at
        point_distance = int(diff/points)
        if diff < 1:
            raise Exception("Difference m_items-failed_at is not positive!")
        m_items_list = []
        incr_point_dist = point_distance
        for i in range(points):
            m_items_list.append(full_circle.failed_at+incr_point_dist)
            incr_point_dist += point_distance
        print(f"Chose {m_items_list} between {full_circle.failed_at} and {m_items}")
        for new_m_items in m_items_list:
            items_set.clear()
            print(f"Running for # items = {new_m_items}")
            if param.exp_type == "ctr":
                for r in orig_seq:
                    if len(items_set) < new_m_items:
                        items_set.add(r[0])
                    else:
                        print(f"Sequence counts {len(items_set)} items")
                        break
                new_seq = []
                for r in orig_seq:
                    if r[0] in items_set:
                        new_seq.append(r)
            else:
                for r in orig_seq:
                    if len(items_set) < new_m_items:
                        items_set.add(r)
                    else:
                        print(f"Sequence counts {len(items_set)} items")
                        break
                new_seq = []
                for r in orig_seq:
                    if len(new_seq) >= max_served_events: 
                        break
                    if r in items_set:
                        new_seq.append(r)
            print(f"# requests in seq = {len(new_seq)}")
            res_dict[c][n][new_m_items] = {}

            # RERUN experiments on new sequence
            algo = Push_down_algo(circle=full_circle_algo)
            if algo.serve_sequence(sequence=new_seq.copy(), type=param.exp_type, max_served_events=max_served_events):
                raise Exception("Should not happen")

            res_dict[c][n][new_m_items]["algo_access"] = algo.access_cost
            res_dict[c][n][new_m_items]["algo_max_acc"] = algo.max_iteration
            
            wbl_algo = Static_algo(circle=full_circle_wbl)
            wbl_algo.serve_sequence(sequence=new_seq.copy(), type=param.exp_type, max_served_events=max_served_events)
            res_dict[c][n][new_m_items]["wbl_access"] = wbl_algo.access_cost
            res_dict[c][n][new_m_items]["wbl_max_acc"] = wbl_algo.max_iteration

    print(res_dict)
    logger.close()
    with open(f"results/{param.exp_type}_results_m{m_items}_n{param.init_servers}_points{points}_f{full_circle.failed_at}_maxreq{max_served_events}.json", "w") as fp:
        json.dump(res_dict, fp)