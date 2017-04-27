import os
import subprocess
import time

tasks = ['123', '132', '123_2413', '132_1234', '2341_4312',
    '2341_2413',
    '2314_2341',
    '2341_3421',
    '2341_4123',
    '2341_3124',
    '2341_2431',
    '2341_4132',
    '2143_2341',
    '2134_2341',
    '2341_3412',
    '2341_3214',
    '2341_4321',
    '1324_2341',
    '2341_4231',
    '1234_2341',
    '2413_4312',
    '2314_4312',
    '3421_4312',
    '3124_4312',
    '2431_4312',
    '4132_4312',
    '2143_4312',
    '2134_4312',
    '3412_4312',
    '4312_4321',
    '1324_4312',
    '4231_4312',
    '1234_4312',
    '2314_2413',
    '2413_3142',
    '2413_3124',
    '2143_2413',
    '2413_4321',
    '1324_2413',
    '2314_3124',
    '2314_2431',
    '2314_4132',
    '2143_2314',
    '2314_3241',
    '2314_3412',
    '2314_4321',
    '1342_2314',
    '1423_2314',
    '1324_2314',
    '2314_4231',
    '1234_2314',
    '2143_3412',
    '2143_4321',
    '1324_2143',
    '2143_4231',
    '1234_2143',
    '1324_4321',
    '4231_4321',
    '1234_4321',
    '1324_4231']

# tasks = ['1342', '2413', '1234', '1243', '1432', '2143', '1324']

hunt_file_location = "./hunt.py"
status_print_frequency_in_seconds = 30
tick_wait = 0.01

num_parallel = 2
show_completed = True

tasks_running = []
tasks_left = len(tasks)
tasks_completed = []

start_time = time.time()

active_processes = []

ticks = 0

while tasks_left > 0:
    # start a new task if there are any left and I'm running < max
    if len(active_processes) < num_parallel and len(tasks) > 0:

        to_start = tasks[0]
        tasks = tasks[1:]

        active_processes.append(subprocess.Popen(["python3", hunt_file_location, "batch"]+to_start.split("_"), preexec_fn=lambda : os.nice(20)))
        tasks_running.append([to_start,time.time()])
        print("Starting:",to_start)

    # check on existing processes
    i = 0
    while i < len(active_processes):
        if active_processes[i].poll() is not None:
            print("Completed:",tasks_running[i][0],"("+str(round(time.time()-tasks_running[i][1],2)),"seconds)")
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