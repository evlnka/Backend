import zmq

def main():
    packet_count = 0
    
    # Загружаем предыдущее количество пакетов из файла
    try:
        with open("data.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            packet_count = len(lines)
            print(f"Загружено {packet_count} предыдущих пакетов")
    except FileNotFoundError:
        packet_count = 0
        print("Файл не найден, начинаем с 0")
    
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REP)
    socket.bind("tcp://*:2222")
    
    print("Сервер запущен на порту 2222")
    print("Ожидание подключения...")
    
    try:
        while True:
            # Получаем данные от Android
            message = socket.recv_string()
            print(f"Получено: {message}")

            # Увеличиваем счетчик пакетов
            packet_count += 1
            
            # СОХРАНЯЕМ каждый блок данных в файл
            with open("data.txt", "a", encoding="utf-8") as f:
                f.write(f"Пакет #{packet_count}: {message}\n")
            
            print(f"Сохранено в файл: Пакет #{packet_count}")

            # Отправляем ответ
            socket.send_string("Hello from Server!")
            
            # Выводим количество полученных пакетов
            print(f"Всего получено пакетов: {packet_count}")
            
            # Показываем все сохраненные данные
            print("Все данные из файла:")
            with open("data.txt", "r", encoding="utf-8") as f:
                print(f.read())
            
    except KeyboardInterrupt:
        print(f"\nСервер остановлен. Итоговое количество пакетов: {packet_count}")
    finally:
        socket.close()
        ctx.term()

if __name__ == "__main__":
    main()