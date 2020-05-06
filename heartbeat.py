# -*- coding: utf-8 -*-
import os
import subprocess
import re
import shutil
import psutil
import speedtest
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def get_cpuload():
    """
        Получаем время работы компьютера, загруженность процессора, видеокарты,
        оперативной памяти.
    """
    average = 0
    for x in range(3):
        average += float(psutil.cpu_percent(interval=1))
    return(average/3)

def check_cuda():
    if os.path.exists('C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA'):
        return 'Installed'
    else:
        return 'Not Installed'


def get_statistics():
    statistics = {}
    matcher = re.compile('\d+')
    # Top command on mac displays and updates sorted information about processes.


    # Get Physical and Logical CPU Count
    physical_and_logical_cpu_count = os.cpu_count()
    statistics['physical_and_logical_cpu_count'] = physical_and_logical_cpu_count



    cpu_load = get_cpuload()
    statistics['cpu_load'] = round(cpu_load)

    # Memory usage
    ram_info = dict(psutil.virtual_memory()._asdict())
    statistics['ram'] = {'total':ram_info['total'],'available':ram_info['available'],'used':ram_info['used'],'percent':ram_info['percent']}

    st = speedtest.Speedtest()

    st.get_best_server()
    st.download()
    st.upload()
    res = st.results.dict()
    statistics['network_latency'] = {'ping':res['ping'],'upload':res['upload'],\
                                     'download':res['download']}
    statistics['cuda'] = check_cuda()
    return statistics
