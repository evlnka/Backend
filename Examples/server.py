import zmq
import json
import psycopg2
import signal
import sys

DB_CONFIG = {
    "dbname": "mobile_measurements",
    "user": "evlnka",
    "password": "1234",
    "host": "localhost",
    "port": "5432"
}

running = True

def signal_handler(sig, frame):
    global running
    running = False

signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C для завершения

def main():
    global running
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    ctx = zmq.Context()
    socket = ctx.socket(zmq.REP)
    socket.bind("tcp://*:2222")

    print("Сервер запущен на порту 2222")
    print("Ожидание данных...\n")

    try:
        while running:
            try:
                # Проверяем, есть ли сообщение без блокировки
                if socket.poll(timeout=1000):  # таймаут 1 секунда
                    message = socket.recv_string()
                    data = json.loads(message)
                    records = data if isinstance(data, list) else [data]

                    for record in records:
                        cur.execute(
                            """
                            INSERT INTO measurements (
                                latitude, longitude, altitude, timestamp, accuracy,
                                network_type, tac_lac, pci_bsic_psc,
                                ci, earfcn_arfcn, signal
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                record.get("latitude"),
                                record.get("longitude"),
                                record.get("altitude"),
                                record.get("timestamp"),
                                record.get("accuracy"),
                                record.get("networkType"),
                                record.get("tac_lac"),
                                record.get("pci_bsic_psc"),
                                record.get("ci"),
                                record.get("earfcn_arfcn"),
                                record.get("signal"),
                            )
                        )

                    conn.commit()
                    socket.send_string(f" Сохранено {len(records)} записей")
                    print(f"Сохранено {len(records)} записей в БД")

            except Exception as e:
                conn.rollback()
                print("Ошибка:", e)
                socket.send_string("ERROR")

    finally:
        cur.close()
        conn.close()
        socket.close()
        ctx.term()
        print("Сервер остановлен")

if __name__ == "__main__":
    main()
