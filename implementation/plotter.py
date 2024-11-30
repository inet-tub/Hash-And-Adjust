import os

import math
import numpy as np
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from params import param

def sum_results_all_ps():
    """
    Take the result-files of different temporal parameters and put them in one file
    Pick one server-n parameter which got to be present in all single files
    This one will serve as basis for the 3d plotting all p's.
    """
    files = os.listdir("results")
    sel_files = []
    for f in files:
        if f.startswith(f"n{int(param.init_servers)}") and f.endswith(f"_alg{param.algorithm}_results.json"):
            sel_files.append(f)
    curr_data = {}
    if os.path.exists(f"results/n{param.init_servers}_h{param.n_items}_m"
                  f"{param.size_dataset}_all_tmp_results.json"):
        with open(f"results/n{param.init_servers}_h{param.n_items}_m"
                  f"{param.size_dataset}_all_tmp_results.json", "r") as fp:
            curr_data = json.load(fp)
    new_dict = curr_data
    for f in sel_files:
        with open("results/"+f, "r") as fr:
            data = json.load(fr)
            for p in data:      # take all temp-param, just # servers is fixed to given param
                if p[3] == '_':     # case of 0.9, 0.3, ...
                    if p[:3] not in new_dict:
                        new_dict[p[:3]] = {}
                    for ad in data[p]:
                        new_dict[p[:3]][str(ad)] = data[p][str(ad)][str(param.init_servers)]
                else:               # 0.75, 0.15, ...
                    if p[:4] not in new_dict:
                        new_dict[p[:4]] = {}
                    for ad in data[p]:
                        new_dict[p[:4]][str(ad)] = data[p][str(ad)][str(param.init_servers)]
    sorted_dict_keys = list(reversed(sorted(new_dict)))
    saving_dict = {}
    for key in sorted_dict_keys:
        saving_dict[key] = new_dict[key]
    with open("results/n" + str(param.init_servers) + "_h" + str(param.n_items)
              + "_m" + str(param.size_dataset) + "_all_tmp_results.json", "w") as fw:
        json.dump(new_dict, fw)

def plot_2d_all_ps_fixed_sever_n():
    wbl_tot = {}
    algo_tot = {}
    param.init_servers = 20     # paper-demo (one simulation)
    param.n_items = 10000
    param.size_dataset = 100000
    with open(f"results/n{param.init_servers}_h{param.n_items}_m"
          f"{param.size_dataset}_all_tmp_results.json", "r") as fp:
        data = json.load(fp)
    for p in data:
        is_not_p =  any(not (char.isdigit() or char in ".") for char in p)
        if is_not_p:
            continue
        algo_tot[p] = 0
        wbl_tot[p] = 0
        for c in data[p]:
            if str(c) == param.addit_augm:
                for algo in data[p][c]:
                    if algo == "algo_access":
                        algo_tot[p] += data[p][c][algo] / param.n_items
                    elif algo == "wbl_access":
                        wbl_tot[p] += data[p][c][algo] / param.n_items
    plot_data = []
    for p in algo_tot:
        is_not_p =  any(not (char.isdigit() or char in ".") for char in p)
        if is_not_p:
            continue
        plot_data.append(["H&A", round(float(p), 1), algo_tot[p]+1])
        plot_data.append(["WBL", round(float(p), 1), wbl_tot[p]+1])
    df = pd.DataFrame(plot_data, columns=['name', 'p', 'cost'])
    print(df)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xticks(df.p.unique())
    fs = 30
    filled_markers = ['o', 'D', 'P', '*', 'H']
    sns.lineplot(x='p', y='cost', data=df, hue='name', markers=filled_markers)
    plt.ylabel('Average Access Cost per Item', fontsize=fs*0.75)
    plt.xlabel('Temporal Locality', fontsize=fs)
    plt.tick_params(axis='both', which='major', labelsize=fs)
    leg = ax.legend(bbox_to_anchor=(0.8, 0), loc='lower right', fontsize=fs, ncol=2)
    leg_lines = leg.get_lines()
    for line in range(0, len(ax.lines)):
        if line == 1:  # 1.25
            ax.lines[line].set_linewidth(2.5)
            ax.lines[line].set_color('#FFB570')  # orange
            ax.lines[line].set_marker('o')
            ax.lines[line].set_markersize(10)
            leg_lines[line].set_color('#FFB570')  
            leg_lines[line].set_linewidth(2.5)
            leg_lines[line].set_marker('o')
            leg_lines[line].set_markersize(10)

        if line == 0:  # c2
            color = '#67AB9F'
            ax.lines[line].set_marker('x')
            ax.lines[line].set_markerfacecolor(color)
            ax.lines[line].set_markeredgecolor(color)
            ax.lines[line].set_markersize(10)
            ax.lines[line].set_markeredgewidth(2)
            ax.lines[line].set_linewidth(2.5)
            ax.lines[line].set_color(color)  # green
            ax.lines[line].set_alpha(0.9)
            leg_lines[line].set_color(color)  # green
            leg_lines[line].set_alpha(0.9)
            leg_lines[line].set_marker('x')
            leg_lines[line].set_markerfacecolor(color)
            leg_lines[line].set_markeredgecolor(color)
            leg_lines[line].set_markersize(10)
            leg_lines[line].set_linewidth(2.5)
            leg_lines[line].set_markeredgewidth(2)
    plt.savefig(f"plots/2d_all_ps_n{param.n_items}_m{param.size_dataset}_access.pdf", bbox_inches='tight')
    plt.show()


def plot_2d_all_ps_fixed_sever_n_more_sim():
    """
    Take the results of more simulations on temporal data and plot mean
    """
    files = os.listdir("results_more_sim")    # used for paper, more files like the one used above in one folder
    wbl_tot = {}
    algo_tot = {}

    for f in files:
        if not f.__contains__(str(param.n_items)):
            continue
        with open("results8/" + f, 'r') as fr:
            data = json.load(fr)
        for p in data:
            algo_tot[p] = 0
            wbl_tot[p] = 0
            for c in data[p]:
                if str(c) == param.addit_augm:
                    for algo in data[p][c]:
                        if algo == "algo_access":
                            algo_tot[p] += data[p][c][algo] / param.n_items
                        elif algo == "wbl_access":
                            wbl_tot[p] += data[p][c][algo] / param.n_items
    plot_data = []
    for p in algo_tot:
        plot_data.append(["H&A", float(p), algo_tot[p]+1])
        plot_data.append(["WBL", float(p), wbl_tot[p]+1])
    df = pd.DataFrame(plot_data, columns=['name', 'p', 'cost'])
    print(df)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xticks(df.p.unique())
    fs = 30
    filled_markers = ['o', 'D', 'P', '*', 'H']
    sns.lineplot(x='p', y='cost', data=df, hue='name', markers=filled_markers)
    plt.ylabel('Average Access Cost per Item', fontsize=fs*0.75)
    plt.xlabel('Temporal Locality', fontsize=fs)
    plt.tick_params(axis='both', which='major', labelsize=fs)
    leg = ax.legend(bbox_to_anchor=(0.8, 0), loc='lower right', fontsize=fs, ncol=2)
    leg_lines = leg.get_lines()
    for line in range(0, len(ax.lines)):
        if line == 1:  # 1.25
            ax.lines[line].set_linewidth(2.5)
            ax.lines[line].set_color('#FFB570')  # orange
            ax.lines[line].set_marker('o')
            ax.lines[line].set_markersize(10)
            leg_lines[line].set_color('#FFB570')
            leg_lines[line].set_linewidth(2.5)
            leg_lines[line].set_marker('o')
            leg_lines[line].set_markersize(10)

        if line == 0:  # c2
            color = '#67AB9F'   # green
            ax.lines[line].set_marker('x')
            ax.lines[line].set_markerfacecolor(color)
            ax.lines[line].set_markeredgecolor(color)
            ax.lines[line].set_markersize(10)
            ax.lines[line].set_markeredgewidth(2)
            ax.lines[line].set_linewidth(2.5)
            ax.lines[line].set_color(color)
            ax.lines[line].set_alpha(0.9)
            leg_lines[line].set_color(color)
            leg_lines[line].set_alpha(0.9)
            leg_lines[line].set_marker('x')
            leg_lines[line].set_markerfacecolor(color)
            leg_lines[line].set_markeredgecolor(color)
            leg_lines[line].set_markersize(10)
            leg_lines[line].set_linewidth(2.5)
            leg_lines[line].set_markeredgewidth(2)
    plt.savefig(f"plots/2d_nsim{len(files)}_all_ps_n{param.n_items}_m{param.size_dataset}_access.pdf", bbox_inches='tight')
    plt.show()

def line_plot_m_items():
    """
    Plots data according to init_server-parameters
    Plot will search for data for stale time and server ins/del-frequency- parameters given on param.py

    data_format = [ ['Algo', '0', 121], ['Static', '0', 117],
            ['Algo', '100', 103], ['Static', '100', 117] ]
    """
    data = []
    folder = "results/"
    files = os.listdir(folder)
    failed_at = -99
    param.exp_type = 'caida'    # for paper
    param.n_items = 5000
    for f in files:
        if not f.__contains__(f'm{param.n_items}') or not f.__contains__(param.exp_type):
            continue
        with open(folder + f, 'r') as fr:
            single_res = json.load(fr)
        for cap in single_res:
            if cap == 'Failure_at':
                failed_at = single_res[cap]
                continue
            for n_server in single_res[cap]:
                for m_items in single_res[cap][n_server]:
                    print(single_res[cap][n_server][m_items])
                    if param.exp_type == "AdjustHash" or param.algorithm == "All":
                        data.append(['H&A', int(m_items), int(single_res[cap][n_server][m_items]['algo_access'])/int(m_items)+1])
                    if param.exp_type == "WBL" or param.algorithm == "All":
                        data.append(['WBL', int(m_items), int(single_res[cap][n_server][m_items]['wbl_access'])/int(m_items)+1])

    data.append(['H&A', failed_at, 1])
    data.append(['WBL', failed_at, 1])

    df = pd.DataFrame(data, columns=['name', 'm_items', 'cost'])
    print(df)
    fig, ax = plt.subplots(figsize=(10, 6))
    
    
    fs = 25
    
    sns.lineplot(x='m_items', y='cost', hue='name', data=df)

    ax.set_ylabel('Average Access Cost per Item', fontsize=fs*0.9)
    ax.set_xlabel('Number of Items', fontsize=fs)

    x_labels = ax.get_xticks()
    ax.set_xticklabels(labels=x_labels, fontsize=fs)

    # change labels to be integer
    yint = []
    labels = ax.get_yticks()
    for each in labels:
        if param.exp_type == 'unbca':
            yint.append(round(each,2))
        else:
            yint.append(int(each))
    ax.set_yticklabels(labels=yint, fontsize=fs)
    yint = []
    
    xpos = failed_at
    if param.exp_type == 'caida':
        ypos = 2.9
        ticks = [4200, 4400, 4600, 4800, 5000]  # Customize these as needed
        ax.hlines(y=1, xmin = xpos-xpos*0.01, xmax = xpos, color='purple', linestyle='-', label = "Traditional", linewidth=5)
        ax.vlines(x=xpos, ymin=1, ymax=ypos, color = 'black', linestyles="dashed")
        ax.text(x=xpos, y=ypos,s="Server capacity reached",ha='center',va='center',rotation='vertical',backgroundcolor='white',fontsize=fs*0.55)
    else:
        ypos = 1.5
        ticks = [3750, 4000, 4250, 4500, 4750, 5000]  # Customize these as needed
        ax.hlines(y=1, xmin = xpos-xpos*0.01, xmax = xpos, color='purple', linestyle='-', label = "Traditional", linewidth=5)
        ax.vlines(x=xpos, ymin=1, ymax=ypos, color = 'black', linestyles="dashed")
        ax.text(x=xpos, y=ypos,s="Server capacity reached",ha='center',va='center',rotation='vertical',backgroundcolor='white',fontsize=fs*0.55)
    
    ax.set_xticks(df.m_items.unique())
    
    ax.set_xticks(ticks)
    ax.set_xticklabels([f'{t:.0f}' for t in ticks])  # Format ticks without decimal
    
    # add legend
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(bbox_to_anchor=(0, 1), loc='upper left', fontsize=fs, ncol=2)
    leg_lines = leg.get_lines()
    print(leg_lines)
    for line in range(0, len(ax.lines)):
        if line == 1:  # 1.25
            ax.lines[line].set_linewidth(2.5)
            ax.lines[line].set_color('#FFB570')  # orange
            ax.lines[line].set_marker('o')
            ax.lines[line].set_markersize(10)
            leg_lines[line].set_color('#FFB570')  
            leg_lines[line].set_linewidth(2.5)
            leg_lines[line].set_marker('o')
            leg_lines[line].set_markersize(10)


        if line == 0:  # c2
            color = '#67AB9F'
            ax.lines[line].set_marker('x')
            ax.lines[line].set_markerfacecolor(color)
            ax.lines[line].set_markeredgecolor(color)
            ax.lines[line].set_markersize(10)
            ax.lines[line].set_markeredgewidth(2)
            ax.lines[line].set_linewidth(2.5)
            ax.lines[line].set_color(color)  # green
            ax.lines[line].set_alpha(0.9)
            leg_lines[line].set_color(color)  # green
            leg_lines[line].set_alpha(0.9)
            leg_lines[line].set_marker('x')
            leg_lines[line].set_markerfacecolor(color)
            leg_lines[line].set_markeredgecolor(color)
            leg_lines[line].set_markersize(10)
            leg_lines[line].set_linewidth(2.5)
            leg_lines[line].set_markeredgewidth(2)
        
        if line == 2:  # traditional
            ax.lines[line].set_linestyle('-')
            ax.lines[line].set_linewidth(5)
            ax.lines[line].set_color('purple')  
            ax.lines[line].set_alpha(0.5)
            leg_lines[line].set_color('purple')  
            leg_lines[line].set_alpha(0.5)
            leg_lines[line].set_linestyle('-')
            leg_lines[line].set_linewidth(5)
    
    plt.savefig(f"plots/m_items_{param.exp_type}_{failed_at}.pdf", bbox_inches='tight')
    plt.show()

def line_plot_stale():
    """
    Plots data according to server stale_time parameters
    Plot will search for data for init_servers- and server ins/del-frequency- parameters given on param.py

    data_format = [ ['Algo', '0', 121], ['Static', '0', 117],
            ['Algo', '200', 103], ['StaticStatic', '200', 117] ]
    """
    param.exp_type = 'ctr'          # for paper
    data = []
    dir = "results/"
    files = os.listdir(dir)
    capacity = param.addit_augm
    n_servers = param.init_servers
    for f in files:
        if param.exp_type == "temp" and not f.endswith("all_tmp_results.json"):
            if f.startswith(f"n{int(param.init_servers)}") and f.endswith("_results.json") \
                    and get_freq(f) == str(param.serv_ins_freq):
                with open(dir + f, 'r') as fr:
                    single_res = json.load(fr)
                for trace in single_res:
                    print(single_res[trace][capacity])
                    data.append(['Algo', int(get_stale(f)), single_res[trace][capacity][str(n_servers)]['algo_access']])
                    data.append(
                        ['Wbl', int(get_stale(f)), single_res[trace][capacity][str(n_servers)]['wbl_access']])
        elif param.exp_type == "ctr" and f.__contains__("ctr"):
            if f.__contains__(f"n{int(param.init_servers)}_"):
                with open(dir + f, 'r') as fr:
                    single_res = json.load(fr)
                    print(single_res[capacity])
                    data.append(['H&A', int(get_stale(f)), single_res[capacity][str(n_servers)]['algo_access']/1029+1,
                                     single_res[capacity][str(n_servers)]['algo_mean_serv_c'], 2])
                    data.append(
                        ['WBL', int(get_stale(f)), single_res[capacity][str(n_servers)]['wbl_access']/1029+1,
                                    single_res[capacity][str(n_servers)]['wbl_mean_serv_c'], 0.5])
    df = pd.DataFrame(data, columns=['name', 'stale', 'cost', 'mean_server_c', 'size_p'])
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xticks(df.stale.unique())
    fs = 25
    sns.lineplot(x='stale', y='cost', hue='name', data=df)
    ax2 = plt.twinx()
    sns.scatterplot(x='stale', y='mean_server_c', s=200 * df['size_p'], hue='name', data=df, ax=ax2, legend=False,
                    palette=['#67AB9F', '#FFB570'])
    ax.set_ylabel('Average Access Cost per Item', fontsize=fs*0.9)
    ax.set_xlabel('Stale Time', fontsize=fs)
    ax2.set_ylabel('Mean Server Capacity', fontsize=fs)
    x_labels = ax.get_xticks()
    ax.set_xticklabels(labels=x_labels, fontsize=fs)

    # change labels to be integer
    yint = []
    labels = ax.get_yticks()
    for each in labels:
        yint.append(int(each))
    ax.set_yticklabels(labels=yint, fontsize=fs)
    yint = []
    labels = ax2.get_yticks()
    for each in labels:
        yint.append(int(each))
    ax2.set_yticklabels(labels=yint, fontsize=fs)

    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(bbox_to_anchor=(0.62, 0.8), loc='lower right', fontsize=fs, ncol=2)
    leg_lines = leg.get_lines()
    for line in range(0, len(ax.lines)):
        if line == 1:  # 1.25
            ax.lines[line].set_linewidth(2.5)
            ax.lines[line].set_color('#FFB570')  # orange
            ax.lines[line].set_marker('o')
            ax.lines[line].set_markersize(10)
            leg_lines[line].set_color('#FFB570')  
            leg_lines[line].set_linewidth(2.5)
            leg_lines[line].set_marker('o')
            leg_lines[line].set_markersize(10)

        if line == 0:  # c2
            color = '#67AB9F'       # green
            ax.lines[line].set_marker('x')
            ax.lines[line].set_markerfacecolor(color)
            ax.lines[line].set_markeredgecolor(color)
            ax.lines[line].set_markersize(10)
            ax.lines[line].set_markeredgewidth(2)
            ax.lines[line].set_linewidth(2.5)
            ax.lines[line].set_color(color)  
            ax.lines[line].set_alpha(0.9)
            leg_lines[line].set_color(color)  
            leg_lines[line].set_alpha(0.9)
            leg_lines[line].set_marker('x')
            leg_lines[line].set_markerfacecolor(color)
            leg_lines[line].set_markeredgecolor(color)
            leg_lines[line].set_markersize(10)
            leg_lines[line].set_linewidth(2.5)
            leg_lines[line].set_markeredgewidth(2)

    plt.tick_params(axis='both', which='major', labelsize=fs)

    if param.exp_type == "temp":
        plt.savefig(f"plots/stale_line_n{n_servers}_c{capacity}_p{param.temp_p}.pdf", bbox_inches='tight')
    else:
        plt.savefig(f"plots/stale_line_n{n_servers}_c{capacity}_ctr.pdf", bbox_inches='tight')
    plt.show()


def line_plot_n_servers():
    """
    Plots data according to init_server-parameters
    Plot will search for data for stale time and server ins/del-frequency- parameters given on param.py

    data_format = [ ['Algo', '0', 121], ['Static', '0', 117],
            ['Algo', '100', 103], ['Static', '100', 117] ]
    """
    param.exp_type = 'ctr'      # for paper
    data = []
    folder = "results/"
    files = os.listdir(folder)
    capacity = param.addit_augm
    for f in files:
        if param.exp_type=="temp" and f.endswith("_results.json") and not f.endswith("all_tmp_results.json"):
            if get_freq(f) == str(param.serv_ins_freq) and get_stale(f) == str(param.stale_time):
                with open(folder + f, 'r') as fr:
                    single_res = json.load(fr)
            for trace in single_res:
                for n_servers_str in single_res[trace][capacity]:
                    n_servers = int(n_servers_str)
                    if param.exp_type == "AdjustHash" or param.algorithm == "All":
                        data.append(['H&A', n_servers, single_res[trace][capacity][str(n_servers)]['algo_access']])
                    if param.exp_type == "WBL" or param.algorithm == "All":
                        data.append(['WBL', n_servers, single_res[trace][capacity][str(n_servers)]['wbl_access']])
        elif param.exp_type == "ctr" and f.__contains__("ctr"):
            if get_stale(f) == str(param.stale_time):
                with open(folder + f, 'r') as fr:
                    single_res = json.load(fr)
                for n_servers_str in single_res[capacity]:
                    n_servers = int(n_servers_str)
                    print(single_res[capacity])
                    if param.exp_type == "AdjustHash" or param.algorithm == "All":
                        data.append(['H&A', n_servers, single_res[capacity][str(n_servers)]['algo_access']/1029+1,
                                     single_res[capacity][str(n_servers)]['algo_max_acc'], 2])
                    if param.exp_type == "WBL" or param.algorithm == "All":
                        data.append(['WBL', n_servers, single_res[capacity][str(n_servers)]['wbl_access']/1029+1,
                                    single_res[capacity][str(n_servers)]['wbl_max_acc'], 0.5])
    df = pd.DataFrame(data, columns=['name', 'n_servers', 'cost', 'max_cost', 'size_p'])
    print(df)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xticks(df.n_servers.unique())
    fs = 30
    sns.lineplot(x='n_servers', y='cost', hue='name', data=df)
    ax.set_ylabel('Average Access Cost per Item', fontsize=fs*0.75)
    ax.set_xlabel('Number of Servers', fontsize=fs)

    x_labels = ax.get_xticks()
    ax.set_xticklabels(labels=x_labels, fontsize=fs)
    
    # change labels to be integer
    yint = []
    labels = ax.get_yticks()
    for each in labels:
        yint.append(int(each))
    ax.set_yticklabels(labels=yint, fontsize=fs)
    yint = []
    
    # add legend
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(bbox_to_anchor=(1, 0.73), loc='lower right', fontsize=fs, ncol=2)

    leg_lines = leg.get_lines()
    for line in range(0, len(ax.lines)):
        if line == 1:  # 1.25
            ax.lines[line].set_linewidth(2.5)
            ax.lines[line].set_color('#FFB570')  # orange
            ax.lines[line].set_marker('o')
            ax.lines[line].set_markersize(10)
            leg_lines[line].set_color('#FFB570')  
            leg_lines[line].set_linewidth(2.5)
            leg_lines[line].set_marker('o')
            leg_lines[line].set_markersize(10)

        if line == 0:  # c2
            color = '#67AB9F'           # green
            ax.lines[line].set_marker('x')
            ax.lines[line].set_markerfacecolor(color)
            ax.lines[line].set_markeredgecolor(color)
            ax.lines[line].set_markersize(10)
            ax.lines[line].set_markeredgewidth(2)
            ax.lines[line].set_linewidth(2.5)
            ax.lines[line].set_color(color)  
            ax.lines[line].set_alpha(0.9)
            leg_lines[line].set_color(color) 
            leg_lines[line].set_alpha(0.9)
            leg_lines[line].set_marker('x')
            leg_lines[line].set_markerfacecolor(color)
            leg_lines[line].set_markeredgecolor(color)
            leg_lines[line].set_markersize(10)
            leg_lines[line].set_linewidth(2.5)
            leg_lines[line].set_markeredgewidth(2)
    if param.exp_type == "temp":
        plt.savefig(f"plots/n_servers_p{param.temp_p}_c{capacity}_f{param.serv_ins_freq}_s"
                    f"{param.stale_time}.pdf", bbox_inches='tight')
    else:
        plt.savefig(f"plots/n_servers_ctr_c{capacity}_f{param.serv_ins_freq}_s"
                    f"{param.stale_time}.pdf", bbox_inches='tight')
    plt.show()

def plotting_occ_all(temp_p=param.temp_p):
    param.exp_type = "temp"         # for paper
    if param.exp_type == "ctr":
        dir = 'results2_7/'
        param.size_dataset = 10000
        param.init_servers = 200
        param.n_items = 1029
    elif param.exp_type == "temp":
        dir = 'results/'
        param.size_dataset = 100000
        param.init_servers = 200
        param.n_items = 10000
    files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    data = []
    extremes = {}
    map_input = []
    access_costs = {}
    tot_items = -99
    max_unbound = -99
    print(files)
    for f in files:
        if f.__contains__("results"):
            with open(f"{dir}{f}", 'r') as fr:
                res = json.load(fr)
            if param.exp_type == 'temp':
                if f.__contains__("algAll"):
                    for c in res:
                        for s in res[c]:
                            for m in res[c][s]:
                                for algo in res[c][s][m]:
                                    if algo == "algo_access":
                                        access_costs["H&A"] = res[c][s][m][algo]      
                                    elif algo == "wbl_access":
                                        access_costs["WBL"] = res[c][s][m][algo]
                else:
                    for c in res:
                        if c != param.temp_p:   
                            continue
                        for s in res[c]:
                            for algo in res[c][s]:
                                print(algo)
                                if algo == "algo_access":
                                    access_costs["H&A"] = res[c][s][algo]      
                                elif algo == "wbl_access":
                                    access_costs["WBL"] = res[c][s][algo]
                                elif algo == "static_access":
                                    access_costs["Traditional"] = 0
                access_costs["Traditional"] = 0                   
            else:
                for c in res:
                    for s in res[c]:
                        for algo in res[c][s]:
                            print(algo)
                            if algo == "algo_access":
                                access_costs["H&A"] = res[c][s][algo]      
                            elif algo == "wbl_access":
                                access_costs["WBL"] = res[c][s][algo]
                access_costs["Traditional"] = 0
    for f in files:
        if f.__contains__(temp_p) or f.__contains__("ctr") or f.__contains__("fb") or f.__contains__("unbca"):
            if f.__contains__("results"):
                continue
            with open(dir + f, 'r') as fr:
                single_res = json.load(fr)
            sorted_dict = {k: int(v) for k, v in sorted(single_res.items(), key=lambda item: item[1])}
            if tot_items == -99:
                tot_items = sum(sorted_dict.values())
            count = 0
            test_sum = 0
            for req in sorted_dict:
                if f.__contains__("inf"):
                    struct_type = 'Traditional'
                    plot_desc = 'Traditional Consistent Hashing'
                elif f.__contains__("1.25"):
                    struct_type = 'WBL'
                    plot_desc = 'Consistent Hashing with \nBounded Loads'
                elif f.__contains__("c4"):
                    struct_type = 'H&A'
                    plot_desc = 'Hash & Adjust'
                else:
                    raise Exception("File type in results not valid")
                data.append([struct_type, count, sorted_dict[req]])
                if count == 0:
                    extremes[struct_type] = {}
                    extremes[struct_type]['first'] = sorted_dict[req]
                elif count == len(sorted_dict) - 1:
                    extremes[struct_type]['last'] = sorted_dict[req]
                    if param.exp_type == 'temp':
                        map_input.append((tot_items/(extremes[struct_type]['last']*param.init_servers),      
                                          access_costs[struct_type]/param.n_items+1, plot_desc))   
                    else:
                        map_input.append((tot_items/(extremes[struct_type]['last']*param.init_servers),    
                                          access_costs[struct_type]/param.n_items+1, plot_desc))     
                    if struct_type == 'Traditional':
                        max_unbound = extremes[struct_type]['last']
                count += 1
                test_sum += sorted_dict[req]
            print("Circle counts " + str(test_sum) + " items")
    count = 0
    for i in range(0, param.init_servers):
        data.append(['M.L. WBL', count, math.ceil(tot_items / param.init_servers * 1.25)])
        data.append(['M.L. H&A', count, math.ceil(tot_items/param.init_servers)+int(param.addit_augm)])
        data.append(['M.L. Traditional', count, max_unbound])
        count += 1

    # plot ratios
    fs=32
    for i in map_input:
        print(i)
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.grid()
    util, cost, size = [], [], []

    for i in range(len(map_input)):
        util.append(map_input[i][0])
        cost.append(map_input[i][1])
        size.append(100)

    plt.xlabel('Average Access Cost per Item', fontsize=fs)
    plt.ylabel('Storage Utilization', fontsize=fs)

    font = {'family': 'normal',
            'size': fs}
    plt.rc('font', **font)
    colors = ['#FFB570', '#67AB9F', '#A680B8']
    markers = ['o','x','D','P', '*', 'H', '2']
    for i in range(len(cost)):
        ax.scatter(cost[i], util[i], s=size[i], c=colors[i % len(colors)], marker=markers[i % len(markers)], clip_on=False)
    plt.tick_params(axis='both', which='major', labelsize=fs)
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.xticks(np.arange(0, 35, 5))
    vals = ax.get_yticks()
    print(vals)
    ax.set_yticklabels(['{:,.0%}'.format(x) for x in vals])
    plt.xlim(0, 30)
    plt.ylim(0.45, 1)
    plt.gca().invert_xaxis()

    fs=25
    for i, e in enumerate(map_input):
        if i == 0:      # WBL
            plt.annotate(e[2], (cost[i]-0.3, util[i]-0.08), weight='bold', color=colors[i], fontsize=fs)
        if i == 1:      # H&A
            plt.annotate(e[2], (cost[i]+2.4, util[i] + 0.02), weight='bold', color=colors[i], fontsize=fs)
        if i == 2:      # Traditional
            plt.annotate(e[2], (cost[i] + 24, util[i] + 0.02), weight='bold', color=colors[i], fontsize=fs)
    if param.exp_type == "temp":
        plt.savefig(f"plots/util&cost_p{param.temp_p}.pdf", bbox_inches='tight')
    else:
        plt.savefig(f"plots/util&cost_{param.exp_type}.pdf", bbox_inches='tight')
    plt.show()

def line_plot_diff_c():
    """
    Line plot for different additive capacity params
    """
    data = []
    param.exp_type = 'caida'    # for paper
    param.init_servers = 50
    param.stale_time = 200
    folder = "results/"
    files = os.listdir(folder)
    for f in files:
        if f.__contains__(param.exp_type) and f.__contains__(f'n{param.init_servers}') and f.__contains__(f's{param.stale_time}'):
            with open(folder + f, 'r') as fr:
                single_res = json.load(fr)
                for capacity in single_res:
                    for n_serv in single_res[capacity]:
                        capacity_int = int(capacity)
                        if param.exp_type == "AdjustHash" or param.algorithm == "All":
                            data.append(['H&A', capacity_int, single_res[capacity][n_serv]['algo_access']/param.n_items+1])
                        if param.exp_type == "WBL" or param.algorithm == "All":
                            data.append(['WBL', capacity_int, single_res[capacity][n_serv]['wbl_access']/param.n_items+1])
    df = pd.DataFrame(data, columns=['name', 'capacity', 'cost'])
    print(df)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xticks(df.capacity.unique())
    fs = 30
    filled_markers = ['o', 'D', 'P', '*', 'H']
    sns.lineplot(x='capacity', y='cost', hue='name', style='name', markers=filled_markers, data=df)
    ax.set_ylabel('Average Access Cost per Item', fontsize=fs*0.75)
    ax.set_xlabel('Addititve capacity', fontsize=fs)
    x_labels = ax.get_xticks()
    ax.set_xticklabels(labels=x_labels, fontsize=fs)
    
    # change labels to be integer
    yint = []
    labels = ax.get_yticks()
    for each in labels:
        yint.append(round(each, 2))
    ax.set_yticklabels(labels=yint, fontsize=fs)
    yint = []

    # add legend
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(bbox_to_anchor=(1, 0.73), loc='lower right', fontsize=fs, ncol=2)
    leg_lines = leg.get_lines()
    for line in range(0, len(ax.lines)):
        if line == 1:  # 1.25
            ax.lines[line].set_linewidth(2.5)
            ax.lines[line].set_color('#FFB570')  # orange
            ax.lines[line].set_marker('o')
            ax.lines[line].set_markersize(10)
            leg_lines[line].set_color('#FFB570')  
            leg_lines[line].set_linewidth(2.5)
            leg_lines[line].set_marker('o')
            leg_lines[line].set_markersize(10)


        if line == 0:  # c2
            color = '#67AB9F'       # green
            ax.lines[line].set_marker('x')
            ax.lines[line].set_markerfacecolor(color)
            ax.lines[line].set_markeredgecolor(color)
            ax.lines[line].set_markersize(10)
            ax.lines[line].set_markeredgewidth(2)
            ax.lines[line].set_linewidth(2.5)
            ax.lines[line].set_color(color) 
            ax.lines[line].set_alpha(0.9)
            leg_lines[line].set_color(color) 
            leg_lines[line].set_alpha(0.9)
            leg_lines[line].set_marker('x')
            leg_lines[line].set_markerfacecolor(color)
            leg_lines[line].set_markeredgecolor(color)
            leg_lines[line].set_markersize(10)
            leg_lines[line].set_linewidth(2.5)
            leg_lines[line].set_markeredgewidth(2)
    plt.savefig(f"plots/diff_c_{param.exp_type}_n{param.n_items}_m{param.size_dataset}.pdf", bbox_inches='tight')
    plt.show()

def get_p_acc(filename):
    spl_char = '_p'
    first_part = filename.split(spl_char, 1)[1]
    spl_char = '_lim'
    return first_part.split(spl_char, 1)[0]


def get_p_occ(filename):
    spl_char = '_p'
    first_part = filename.split(spl_char, 1)[1]
    spl_char = '_occ'
    return first_part.split(spl_char, 1)[0]


def get_c_occ(filename):
    spl_char = '_c'
    first_part = filename.split(spl_char, 1)[1]
    spl_char = '_p'
    return first_part.split(spl_char, 1)[0]


def get_freq(filename):
    spl_char = '_f'
    first_part = filename.split(spl_char, 1)[1]
    spl_char = '_alg'
    return first_part.split(spl_char, 1)[0]


def get_stale(filename):
    spl_char = '_s'
    first_part = filename.split(spl_char, 1)[1]
    if param.exp_type == "ctr":
        spl_char = '.json'
        return first_part.split(spl_char, 1)[0]
    else:
        spl_char = '_f'
        return first_part.split(spl_char, 1)[0]