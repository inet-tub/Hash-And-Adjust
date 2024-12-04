
import implementation.experiment as ex
import implementation.plotter as pl

def main():
    """
    Each experiment at the beginning of the code-block (ex.***) 
    generates the input needed for the plotting code  (pl.***)
    """
    
    # Experiment 1
    ex.run_paper_experiment_1()           
    pl.plotting_occ_all(temp_p='0.75')    # Fig. 3a) - access cost and storage utilization for one temp_p-param (temporal dataset)
    pl.plot_2d_all_ps_fixed_sever_n()     # Fig. 3b) - access costs for different temp_p-params (temporal dataset)
    
    # Experiment 2
    #ex.run_paper_experiment_2()          # may need to be re-run 2-3x (rarely fails due to server-insertion/deletion generation-file) 
    #pl.line_plot_n_servers()             # Fig. 5a) - access cost for different # of servers (CTR dataset)  
    
    # Experiment 3
    #ex.run_paper_experiment_3()
    #pl.line_plot_stale()                 # Fig. 5b) - access cost and server capacity for different stale times (CTR dataset)
    
    # Experiment 4
    #ex.run_experiment_real_failure_check()
    #pl.line_plot_m_items()               # Fig. 4a) - access cost for different # of items, after traditional failure (CAIDA dataset)
    
    # Experiment 5
    #ex.run_experiment_real_diff_c()
    #pl.line_plot_diff_c()                # Fig. 4b) - access cost for different additive capacities (CAIDA dataset)

if __name__ == '__main__':
    main()

