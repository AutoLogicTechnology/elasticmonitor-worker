
import yaml
import elasticsearch
import psutil
import json
import socket
import requests
import datetime

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
            "total":        bytes2human(system_memory.total),
            "available":    bytes2human(system_memory.available),
            "percent":      system_memory.percent,
            "used":         bytes2human(system_memory.used),
            "free":         bytes2human(system_memory.free),
            "active":       bytes2human(system_memory.active),
            "inactive":     bytes2human(system_memory.inactive),
            "buffers":      bytes2human(system_memory.buffers),
            "cached":       bytes2human(system_memory.cached)
        },

        "swap_memory": {
            "total":    bytes2human(swap_memory.total),
            "used":     bytes2human(swap_memory.used),
            "free":     bytes2human(swap_memory.free),
            "percent":  swap_memory.percent,
            "sin":      bytes2human(swap_memory.sin),
            "sout":     bytes2human(swap_memory.sout)
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
                        "total":    bytes2human(usage.total),
                        "used":     bytes2human(usage.used),
                        "free":     bytes2human(usage.free),
                        "percent":  usage.percent
                    }
                }
            })

    return disks 

def push_to_es(server, data, id):
    url = "{0}:{1}/{2}/{3}/{4}".format(server['Host'], server['Port'], server['Index'], server['ObjectType'], id)
    return requests.post(url, data=data, verify=False).status_code

def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n

def go(configuration):
    config = yaml.load(open(configuration))
    now = datetime.datetime.now()

    data = {
        "timestamp":    str(now),
        "server":       socket.gethostname(),
        "cpu":          collect_cpu_stats, 
        "ram":          collect_ram_stats,
        "disk":         collect_dsk_stats 
    }

    return push_to_es(config['ElasticSearch'], data, id="{0}_{1}".format(me, now.strftime('%Y%m%d-%H.%M.%S')))