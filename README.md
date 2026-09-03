1. CPU (psutil): modelo vía platform.processor()/WMI, uso con cpu_percent(interval=0.5), frecuencia con cpu_freq().
2. RAM y Discos (psutil): uso, total y porcentaje con barras gráficas.
3. GPU (GPUtil): carga, temperatura y VRAM; solo si hay GPU NVIDIA compatible.
4. Temperatura CPU (wmi): consulta MSAcpi_ThermalZoneTemperature bajo root\wmi; convierte de décimas de Kelvin a °C y filtra valores irreales (0–120°C). Todo en try-except, mostrando "N/A (Requiere Admin/Driver)" si falla.
5. Formato: refresco cada segundo con cls y dashboard en texto con barras.
Ejecutar
pip install psutil wmi pypiwin32 GPUtil
python monitor_pc.py
