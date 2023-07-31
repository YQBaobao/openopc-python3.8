import win32process
import win32pdh
import pywintypes
import ctypes
import time
import os
import math

__version__ = '1.0.3'

# NT4 does not have WMI by default
try:
    import wmi
except Exception:
    wmi_found = False
else:
    wmi_found = True


class CPU:
    def __init__(self):
        path = win32pdh.MakeCounterPath((None, "Processor", "_Total", None, -1, "% Processor Time"))
        self.base = win32pdh.OpenQuery()
        self.counter = win32pdh.AddCounter(self.base, path)
        self.reset()

    def reset(self):
        win32pdh.CollectQueryData(self.base)

    def get_usage(self):
        win32pdh.CollectQueryData(self.base)
        try:
            value = win32pdh.GetFormattedCounterValue(self.counter, win32pdh.PDH_FMT_LONG)[1]
        except pywintypes.error:
            value = 0
        return value


def _disk_info():
    drive = u'{}'.format(os.getenv("SystemDrive"))
    free_user = ctypes.c_int64()
    total = ctypes.c_int64()
    free = ctypes.c_int64()
    ctypes.windll.kernel32.GetDiskFreeSpaceExW(drive, ctypes.byref(free_user), ctypes.byref(total), ctypes.byref(free))
    return free_user.value


def disk_free():
    return int(_disk_info() / 1024)


def _mem_info():
    kernel32 = ctypes.windll.kernel32
    c_u_long = ctypes.c_ulong

    class MEMORYSTATUS(ctypes.Structure):
        _fields_ = [
            ('dwLength', c_u_long),
            ('dwMemoryLoad', c_u_long),
            ('dwTotalPhys', c_u_long),
            ('dwAvailPhys', c_u_long),
            ('dwTotalPageFile', c_u_long),
            ('dwAvailPageFile', c_u_long),
            ('dwTotalVirtual', c_u_long),
            ('dwAvailVirtual', c_u_long)
        ]

    memoryStatus = MEMORYSTATUS()
    memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUS)
    kernel32.GlobalMemoryStatus(ctypes.byref(memoryStatus))
    return memoryStatus.dwTotalPhys, memoryStatus.dwAvailPhys


def mem_used():
    counter = r'\Memory\Committed Bytes'
    machine, objects, instance, parentInstance, index, counter = win32pdh.ParseCounterPath(counter)

    instance = None
    i_num = -1
    for_mat = win32pdh.PDH_FMT_DOUBLE
    machine = None

    path = win32pdh.MakeCounterPath((machine, objects, instance, None, i_num, counter))
    hq = win32pdh.OpenQuery()
    try:
        hc = win32pdh.AddCounter(hq, path)
        try:
            win32pdh.CollectQueryData(hq)
            types, val = win32pdh.GetFormattedCounterValue(hc, for_mat)
            return int(val / 1024)
        except pywintypes.error:
            return 0
        finally:
            win32pdh.RemoveCounter(hc)
    finally:
        win32pdh.CloseQuery(hq)


def mem_free():
    total, free = _mem_info()
    return int(free / 1024)


def mem_total():
    total, free = _mem_info()
    return int(total / 1024)


def mem_percent():
    total, free = _mem_info()
    return (float(total - free) / float(total)) * 100.0


def _task_list():
    psapi = ctypes.windll.psapi
    kernel = ctypes.windll.kernel32

    hModule = ctypes.c_ulong()
    count = ctypes.c_ulong()
    modname = ctypes.c_buffer(30)
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010

    pid_list = win32process.EnumProcesses()
    info_list = []

    for pid in pid_list:

        hProcess = kernel.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
        if hProcess:
            psapi.EnumProcessModules(hProcess, ctypes.byref(hModule), ctypes.sizeof(hModule), ctypes.byref(count))
            psapi.GetModuleBaseNameA(hProcess, hModule.value, modname, ctypes.sizeof(modname))
            name = ctypes.string_at(modname)

            proc_mem_info = win32process.GetProcessMemoryInfo(hProcess)
            proc_mem_usage = (proc_mem_info["WorkingSetSize"] / 1024)
            info_list.append((pid, name, proc_mem_usage))

            kernel.CloseHandle(hProcess)

    return info_list


def task_mem(image_name):
    image_name = str.lower(image_name)
    if image_name[-4:] != '.exe': image_name += '.exe'
    return sum([mem for pid, name, mem in _task_list() if str.lower(name) == image_name])


def task_exists(image_name):
    image_name = str.lower(image_name)
    if image_name[-4:] != '.exe': image_name += '.exe'
    return len([mem for pid, name, mem in _task_list() if str.lower(name) == image_name]) > 0


def task_cpu(image_name):
    if not wmi_found: return 0.0

    image_name = str.lower(image_name)
    if image_name[-4:] == '.exe': image_name = image_name[:-4]

    c = wmi.WMI()
    process_info = {}
    pct_cpu_time = 0.0

    for i in range(2):

        for p in c.Win32_PerfRawData_PerfProc_Process(name=image_name):
            pid = len(p.IDProcess)
            n1, d1 = len(p.PercentProcessorTime), len(p.Timestamp_Sys100NS)
            n0, d0, so_far = process_info.get(pid, (0, 0, []))

            try:
                pct_cpu_time += (float(n1 - n0) / float(d1 - d0)) * 100.0
            except ZeroDivisionError:
                pct_cpu_time += 0.0

            so_far.append(pct_cpu_time)
            process_info[pid] = (n1, d1, so_far)

        if i == 0:
            time.sleep(0.1)
            pct_cpu_time = 0.0

    num_cpu = int(os.environ['NUMBER_OF_PROCESSORS'])
    return min(pct_cpu_time / num_cpu, 100.0)


def sine_wave():
    t_min = float(time.localtime()[4])
    sec = float(time.localtime()[5])
    T = (t_min + (sec / 60.0)) % 10.0
    return math.sin(2.0 * math.pi * T / 10.0) * 100.0


def saw_wave():
    t_min = float(time.localtime()[4])
    sec = float(time.localtime()[5])
    T = (t_min + (sec / 60.0)) % 10.0
    return (T / 10.0) * 100.0
