import psycopg2
import folium
import branca.colormap as cm
from datetime import datetime

# Параметры подключения к вашей БД
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "mobile_measurements",
    "user": "evlnka",
    "password": "1234"
}

# Загружаем данные из БД
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT latitude, longitude, altitude, timestamp, network_type,
               tac_lac, pci_bsic_psc, ci, earfcn_arfcn, signal
        FROM measurements
    """)
    results = cursor.fetchall()
    conn.close()
except Exception as e:
    print(f"Ошибка подключения к БД: {e}")
    exit()

if not results:
    print("Нет данных для отображения на карте!")
    exit()

# Создаем карту
avg_lat = sum([row[0] for row in results]) / len(results)
avg_lon = sum([row[1] for row in results]) / len(results)
m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

# Цветовая шкала для сигнала
colormap = cm.LinearColormap(
    colors=['red', 'yellow', 'green'],
    vmin=-125, vmax=-70,
    caption='Уровень сигнала (dBm)'
).to_step(n=6)
colormap.add_to(m)

# Добавляем точки на карту
for row in results:
    lat, lon, alt, ts, net, tac, pci, ci, earfcn, signal = row
    try:
        signal_value = int(signal.split()[0])
    except:
        signal_value = -120

    # Преобразуем timestamp в читаемую дату-время
    try:
        ts_datetime = datetime.fromtimestamp(ts / 1000).strftime("%d.%m.%Y %H:%M:%S")
    except:
        ts_datetime = "-"

    popup_text = (
        f"Широта: {lat:.6f}<br>"
        f"Долгота: {lon:.6f}<br>"
        f"Высота: {alt:.1f} м<br>"
        f"Время: {ts_datetime}<br>"
        f"Тип сети: {net}<br>"
        f"Зона (TAC): {tac}<br>"
        f"ID соты (PCI): {pci}<br>"
        f"CI: {ci}<br>"
        f"Канал (EARFCN): {earfcn}<br>"
        f"Сигнал (RSRP): {signal_value} dBm"
    )

    folium.CircleMarker(
        location=(lat, lon),
        radius=5,
        color=colormap(signal_value),
        fill=True,
        fill_opacity=0.8,
        popup=folium.Popup(popup_text, max_width=300)
    ).add_to(m)

# Сохраняем карту
output_file = "signal_map.html"
m.save(output_file)
print(f"Карта сохранена в {output_file}")
