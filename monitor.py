import os
import time
import platform
import sys

import psutil
import wmi

try:
    import GPUtil
except ImportError:
    GPUtil = None


def limpiar_consola():
    os.system("cls" if os.name == "nt" else "clear")


def get_cpu_modelo():
    try:
        modelo = platform.processor()
        if modelo:
            return modelo
        info = wmi.WMI()
        cpu = info.Win32_Processor()[0]
        return cpu.Name.strip()
    except Exception:
        return "N/A"


def get_cpu_uso():
    return psutil.cpu_percent(interval=0.5)


def get_cpu_frecuencia():
    try:
        f = psutil.cpu_freq()
        if f:
            return f.current, f.max
    except Exception:
        pass
    return None, None


def get_ram():
    vm = psutil.virtual_memory()
    return vm.used, vm.total, vm.percent


def get_discos():
    partes = psutil.disk_partitions()
    discos = []
    for p in partes:
        try:
            uso = psutil.disk_usage(p.mountpoint)
            discos.append((p.mountpoint, uso.used, uso.total, uso.percent))
        except Exception:
            continue
    return discos


def get_gpus():
    gpus = []
    if GPUtil is None:
        return gpus
    try:
        for g in GPUtil.getGPUs():
            gpus.append({
                "nombre": g.name,
                "carga": g.load * 100,
                "temp": g.temperature,
                "mem_used": g.memoryUsed,
                "mem_total": g.memoryTotal,
            })
    except Exception:
        pass
    return gpus


def get_temperatura_cpu():
    """
    Lee la temperatura de la CPU via WMI / root\\wmi / MSAcpi_ThermalZoneTemperature.
    Frecuentemente falla o devuelve valores irreales en Windows, por eso va
    envuelto en try-except.
    """
    try:
        w = wmi.WMI(namespace="root\\wmi")
        zones = w.MSAcpi_ThermalZoneTemperature()
        if zones and len(zones) > 0:
            temps = []
            for z in zones:
                try:
                    # Los valores vienen en décimas de Kelvin (x10)
                    temp_k = float(z.CurrentTemperature)
                    temp_c = (temp_k / 10.0) - 273.15
                    if 0 <= temp_c <= 120:
                        temps.append(round(temp_c, 1))
                except Exception:
                    continue
            if temps:
                return max(temps)
        return None
    except Exception:
        return None


def formatear_bytes(b):
    for unidad in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024 or unidad == "TB":
            return f"{b:.1f} {unidad}"
        b = b / 1024.0
    return f"{b:.1f} TB"


def barra(percent, ancho=20, char="|"):
    p = max(0, min(100, percent))
    lleno = int(round(p / 100 * ancho))
    return char * lleno + "." * (ancho - lleno)


def main():
    modelo = get_cpu_modelo()
    print("Computando datos... espere un momento")
    time.sleep(1)

    while True:
        limpiar_consola()

        cpu_percent = get_cpu_uso()
        freq_cur, freq_max = get_cpu_frecuencia()
        ram_used, ram_total, ram_percent = get_ram()
        discos = get_discos()
        gpus = get_gpus()
        temp_cpu = get_temperatura_cpu()

        ancho = 62
        sep = "=" * ancho

        print(sep)
        print(" MONITOR DE SISTEMA - WINDOWS".ljust(ancho // 2 + len(" MONITOR DE SISTEMA - WINDOWS")))
        print(sep)

        # CPU
        print("\n[CPU]")
        print(f"  Modelo          : {modelo}")
        print(f"  Uso             : {cpu_percent:5.1f} %  {barra(cpu_percent)}")
        if freq_cur:
            freq_str = f"{freq_cur:.0f} MHz"
            if freq_max:
                freq_str += f" / {freq_max:.0f} MHz (max)"
            print(f"  Frecuencia      : {freq_str}")

        # Temperatura CPU
        print("\n[TERMICA]")
        if temp_cpu is not None:
            print(f"  CPU             : {temp_cpu} °C")
        else:
            print("  CPU             : N/A (Requiere Admin/Driver)")

        # RAM
        print("\n[MEMORIA RAM]")
        print(f"  Usada          : {formatear_bytes(ram_used)} / {formatear_bytes(ram_total)}")
        print(f"  Uso            : {ram_percent:5.1f} %  {barra(ram_percent)}")

        # Discos
        print("\n[DISCOS]")
        for punto, used, total, percent in discos:
            print(f"  {punto} : {formatear_bytes(used)} / {formatear_bytes(total)}  {percent:5.1f} %  {barra(percent)}")

        # GPU
        print("\n[GPU]")
        if gpus:
            for g in gpus:
                print(f"  {g['nombre']}")
                print(f"    Carga        : {g['carga']:5.1f} %  {barra(g['carga'])}")
                if g["temp"] >= 0:
                    print(f"    Temperatura  : {g['temp']} °C")
                else:
                    print(f"    Temperatura  : N/A")
                if g["mem_total"] > 0:
                    print(f"    VRAM         : {g['mem_used']:.0f} / {g['mem_total']:.0f} MB")
        else:
            print("  No se detecto GPU compatible (GPUtil/NVIDIA).")

        print("\n" + sep)
        print(" Presione Ctrl+C para salir")
        print(sep)

        try:
            time.sleep(1)
        except KeyboardInterrupt:
            limpiar_consola()
            print("Monitoreo finalizado.")
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        limpiar_consola()
        print("Monitoreo finalizado.")