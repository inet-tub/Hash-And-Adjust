
import implementation.experiment as ex
import implementation.plotter as pl

def main():
    
    # Experiment 1
    ex.run_paper_experiment_1()
    pl.plotting_occ_all(temp_p='0.75')     # Fig. 3a)
    pl.plot_2d_all_ps_fixed_sever_n()     # Fig. 3b)
    
    # Experiment 2
    #ex.run_paper_experiment_2()         # may need to be re-run 2-3x (rarely fails due to server-insertion/deletion generation-file) 
    #pl.line_plot_n_servers()            # Fig. 5a)
    
    # Experiment 3
    #ex.run_paper_experiment_3()
    #pl.line_plot_stale()                # Fig. 5b)
    
    # Experiment 4
    #ex.run_experiment_real_failure_check()
    #pl.line_plot_m_items()             # Fig. 4a)
    
    # Experiment 5
    #ex.run_experiment_real_diff_c()
    #pl.line_plot_diff_c()              # Fig. 4b)

if __name__ == '__main__':
    main()

