from datetime import date
from datetime import datetime
import psutil
import numpy as np
import json
import pymongo


# MONGODB CLIENT
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["pymon"]
cpu_col = mydb["cpu"]
memory_col = mydb["memory"]
disk_col = mydb["disk"]

# PROCESSOR
json_cpu = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
    "cpu_times": [],
    "cpu_percent": [],
    "cpu_times_percent": [],
    "cpu_count": '',
    "cpu_stats": '',
    "cpu_freq": [],
    "cpu_avg_load": []
}
cpu_times = psutil.cpu_times(percpu=True)
for cpui in cpu_times:
    json_cpu['cpu_times'].append(cpui._asdict())

cpu_percent = psutil.cpu_percent(percpu=True)
for cpuperi in range(len(cpu_percent)):
    json_cpu['cpu_percent'].append(cpu_percent[cpuperi])

cpu_times_percent = psutil.cpu_times_percent(percpu=True)
for ctpi in range(len(cpu_times_percent)):
    json_cpu['cpu_times_percent'].append(cpu_times_percent[ctpi]._asdict())

json_cpu['cpu_count'] = psutil.cpu_count(logical=True)

json_cpu['cpu_stats'] = psutil.cpu_stats()

cpu_freq = psutil.cpu_freq(percpu=True)
for cfi in range(len(cpu_freq)):
    json_cpu['cpu_freq'].append(cpu_freq[cfi]._asdict())

str_info = "last {} minute ago"
avg_min = 5
cpu_avg_load = [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]
for cpavl in cpu_avg_load:
    json_cpu['cpu_avg_load'].append({
        str_info.format(avg_min): cpavl
    })
    avg_min += 5

cpu_col.insert_one(json_cpu)

# RAM
info_ram = 'normal'
json_ram = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
    "memory_vm": {
        "detail": '',
        "threshold": 2*pow(1028, 3),
        "info": info_ram
    },
    "memory_swap": {}
}
memory_vm = psutil.virtual_memory()
json_ram['memory_vm']['detail'] = memory_vm._asdict()
if memory_vm.available <= json_ram['memory_vm']['threshold']:
    json_ram['memory_vm']['info'] = 'warning'

json_ram['memory_swap'] = psutil.swap_memory()._asdict()

memory_col.insert_one(json_ram)

# DISK
json_disk = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
    "disk_partition": [],
    "disk_io_counter": {},
}

disk_partition = psutil.disk_partitions(all=False)
for dpe in disk_partition:
    temp_dpe = dpe._asdict()
    temp_dpe['usage'] = psutil.disk_usage(temp_dpe['mountpoint'])._asdict()
    json_disk['disk_partition'].append(temp_dpe)

disk_io_counter = psutil.disk_io_counters(perdisk=True)
for dioe in disk_io_counter:
    json_disk['disk_io_counter'][dioe] = disk_io_counter[dioe]._asdict()

disk_col.insert_one(json_disk)

print('end')
