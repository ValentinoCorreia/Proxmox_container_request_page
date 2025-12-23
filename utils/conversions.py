def convertCPUSpeedStrToLimit(cpu_speed: str):
    if (cpu_speed == "slow"):
        return 1
    elif (cpu_speed == "fast"):
        return 0
    else:
        return 2