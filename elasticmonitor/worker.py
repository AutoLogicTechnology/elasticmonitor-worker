
import yaml
import psutil
import json
import socket
import datetime

from elasticsearch import Elasticsearch
from elasticmonitor import helpers

def collect_cpu_stats():
    times = psutil.cpu_times()
    per_core_snapshot = psutil.cpu_times_percent(interval=1, percpu=True)

    data = {
        "system_cpu_times": {
            "user":         times.user,
            "nice":         times.nice,
            "system":       times.system,
            "idle":         times.idle,
            "iowait":       times.iowait,
            "irq":          times.irq,
            "softirq":      times.softirq,
            "steal":        times.steal,
            "guest":        times.guest,
            "guest_nice":   times.guest_nice
        },
        "percore_cpu_times": []
    }

    for cpu in per_core_snapshot:
        data['percore_cpu_times'].append({
            "user":         cpu.user,
            "nice":         cpu.nice,
            "system":       cpu.system,
            "idle":         cpu.idle,
            "iowait":       cpu.iowait,
            "irq":          cpu.irq,
            "softirq":      cpu.softirq,
            "steal":        cpu.steal,
            "guest":        cpu.guest,
            "guest_nice":   cpu.guest_nice
        })

    return data

def collect_ram_stats():
    system_memory   = psutil.virtual_memory()
    swap_memory     = psutil.swap_memory()

    data = {
        "system_memory": {
            "total":        helpers.bytes2human(system_memory.total),
            "available":    helpers.bytes2human(system_memory.available),
            "percent":      system_memory.percent,
            "used":         helpers.bytes2human(system_memory.used),
            "free":         helpers.bytes2human(system_memory.free),
            "active":       helpers.bytes2human(system_memory.active),
            "inactive":     helpers.bytes2human(system_memory.inactive),
            "buffers":      helpers.bytes2human(system_memory.buffers),
            "cached":       helpers.bytes2human(system_memory.cached)
        },

        "swap_memory": {
            "total":    helpers.bytes2human(swap_memory.total),
            "used":     helpers.bytes2human(swap_memory.used),
            "free":     helpers.bytes2human(swap_memory.free),
            "percent":  swap_memory.percent,
            "sin":      helpers.bytes2human(swap_memory.sin),
            "sout":     helpers.bytes2human(swap_memory.sout)
        }
    }

    return data

def collect_dsk_stats():
    disks = []

    for partition in psutil.disk_partitions():
        # disks["disks"].append({partition.device:partition.mountpoint: psutil.disk_usage})
        usage = psutil.disk_usage(partition.mountpoint)

        disks.append({
            partition.device: {
                partition.mountpoint: {
                        "total":    helpers.bytes2human(usage.total),
                        "used":     helpers.bytes2human(usage.used),
                        "free":     helpers.bytes2human(usage.free),
                        "percent":  usage.percent
                    }
                }
            })

    return disks 

def push_to_es(server, data, id):
    es = Elasticsearch([{'host': server['Host'], 'port': server['Port']}])
    return es.index(index=server['Index'], doc_type=server['DocType'], id=id, body=data)

def go(configuration):
    with open(configuration) as fd:
        config = yaml.load(fd)

    now = datetime.datetime.now()

    data = {
        "timestamp":    str(now),
        "server":       socket.gethostname(),
        "cpu":          collect_cpu_stats(), 
        "ram":          collect_ram_stats(),
        "disk":         collect_dsk_stats() 
    }

    return push_to_es(config['ElasticSearch'], data, id="{0}_{1}".format(data['server'], now.strftime('%Y%m%d-%H.%M.%S')))
