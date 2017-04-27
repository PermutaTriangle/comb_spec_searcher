import os
import subprocess
import time

from atrap import MetaTree
from atrap.strategies import *
from atrap.ProofTree import ProofTree

def nice_time_format(sec):
    if sec < 60:
        return str(round(sec, 2))+" seconds"
    if sec < 60*60:
        return str(round(sec/60, 2))+" minutes"
    else:
        return str(round(sec/60/60, 2))+" hours"

def list_median(L):
    S = sorted(L)
    
    if len(L) % 2 == 0:
        return (S[len(S)//2-1]+S[len(S)//2])/2
    else:
        return S[(len(S)-1)//2]

testing_task = '123'
num_repetions = 10
tick_wait = 0.01
remove_temp_files = True

hunt_file_location = "./hunt.py"
status_print_frequency_in_seconds = 30

summary_output_file = "./spectrum_results/summary_"+testing_task+"_"+str(num_repetions)+"_repetitions.txt"

num_parallel = 2
show_completed = True

next_task_num = 1
tasks_running = []
tasks_left = num_repetions
tasks_completed = []

start_time = time.time()

active_processes = []

ticks = 0

while tasks_left > 0:
    # start a new task if there are any left and I'm running < max
    if len(active_processes) < num_parallel and next_task_num <= num_repetions:

        active_processes.append(subprocess.Popen(["python3", hunt_file_location, "spectrum", str(next_task_num)]+testing_task.split("_"), preexec_fn=lambda : os.nice(20)))
        tasks_running.append([next_task_num, time.time()])
        
        print("Starting repetition #", next_task_num)
        next_task_num += 1

    # check on existing processes
    i = 0
    while i < len(active_processes):
        if active_processes[i].poll() is not None:
            print("Completed: #",tasks_running[i][0],"("+str(round(time.time()-tasks_running[i][1],2)),"seconds)")
            active_processes.remove(active_processes[i])
            tasks_completed.append([tasks_running[i][0], time.time()-tasks_running[i][1]])
            tasks_running.remove(tasks_running[i])
            tasks_left -= 1
            
        else:
            i += 1

    time.sleep(tick_wait)
    ticks += 1

    if ticks % (status_print_frequency_in_seconds * int(1/tick_wait)) == 0:
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("==============")
        print("=== STATUS ===")
        print("==============")
        print("")
        if show_completed:
            print("Tasks completed:")
            for task in tasks_completed:
                print("\t("+str(round(task[1],2)),"seconds):",task[0])
        else:
            print("Tasks completed:",len(tasks_completed),"\t("+str(round(time.time()-start_time,2)),"seconds)")
        print("")
        print("Tasks running:")
        for task in tasks_running:
            print("\t("+str(round(time.time()-task[1],2)),"seconds):",task[0])
        print("")
        print("Queued tasks:",tasks_left-len(active_processes))
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")

        ticks = 0

## Now we need to read in all the files and process the results
file_names = ['spectrum_results/spectrum_'+testing_task+'_'+str(task_num)+'_results.txt' for task_num in range(1, num_repetions+1)]
results = []
for fn in file_names:
    result_file = open(fn, "r")
    duration = result_file.readline().rstrip()
    json_tree = "".join(result_file.readlines())
    results.append([float(duration), json_tree])

# now partition by proof tree type
proof_tree_partition = []
tiling_set_lookup = {}
tiling_set_json_lookup = {}
for result in results:
    tiling_set = frozenset(ProofTree.from_json(result[1]).set_of_tilings())
    if tiling_set not in tiling_set_lookup:
        tiling_set_lookup[tiling_set] = len(proof_tree_partition)
        tiling_set_json_lookup[tiling_set] = result[1]
        proof_tree_partition.append([])
    proof_tree_partition[tiling_set_lookup[tiling_set]].append(result[0])

strats_file = open('spectrum_results/stratsused.txt', 'r')
strats_used = strats_file.readlines()
strats_file.close()

# Now collect results and print to file
summary_file = open(summary_output_file, "w")
summary_file.write("Task: "+testing_task+"\n")
summary_file.write("Repetitions: "+str(num_repetions)+"\n\n")
summary_file.write("Strategies Used:\n")
summary_file.write("\tBatch stragies: "+strats_used[0])
summary_file.write("\tEquivalence stragies: "+strats_used[1])
summary_file.write("\tInferral stragies: "+strats_used[2])
summary_file.write("\tRecursive stragies: "+strats_used[3])
summary_file.write("\tVerification stragies: "+strats_used[4])
summary_file.write("\n")

summary_file.write("Number of distinct proof trees: "+str(len(proof_tree_partition))+"\n\n")
summary_file.write("Fastest Proof Tree: \t"+nice_time_format(min([result[0] for result in results]))+"\n")
summary_file.write("Slowest Proof Tree: \t"+nice_time_format(max([result[0] for result in results]))+"\n")
summary_file.write("Mean Proof Tree: \t\t"+nice_time_format(sum([result[0] for result in results])/len(results))+"\n")
summary_file.write("Median Proof Tree: \t\t"+nice_time_format( (list_median([result[0] for result in results]) ))+"\n")
summary_file.write("\n\n")
summary_file.write("=========================="+"\n")
summary_file.write("=== PROOF TREE SUMMARY ==="+"\n")
summary_file.write("==========================\n"+"\n")
summary_file.flush()

for (index, tree_part) in enumerate(sorted(proof_tree_partition,key=len, reverse=True)):
    summary_file.write("Tree #"+str(index+1)+":"+"\n")
    summary_file.write("\t\tnumber of occurrences: \t"+str(len(tree_part))+"\n")
    summary_file.write("\t\tfastest occurrence: \t"+nice_time_format(min(tree_part))+"\n")
    summary_file.write("\t\tslowest occurrence: \t"+nice_time_format(max(tree_part))+"\n")
    summary_file.write("\t\tmean occurrence: \t\t"+nice_time_format(sum(tree_part)/len(tree_part))+"\n")
    summary_file.write("\t\tmedian occurrence: \t\t"+nice_time_format( list_median(tree_part) )+"\n")
    summary_file.write("\t\ttree written to: \t\t"+'spectrum_results/spectrum_'+testing_task+'_results_tree_number_'+str(index+1)+'.txt'+"\n\n")
    summary_file.flush()

    tree_output_file = open('spectrum_results/spectrum_'+testing_task+'_results_tree_number_'+str(index+1)+'.txt', "w")
    tree_output_file.write(tiling_set_json_lookup[([k for k in tiling_set_lookup.keys() if tiling_set_lookup[k]==proof_tree_partition.index(tree_part)])[0]])
    tree_output_file.close()

summary_file.close()

if remove_temp_files:
    for temp_file in file_names:
        os.remove(temp_file)

