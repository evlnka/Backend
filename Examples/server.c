#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define PORT 8080
#define BUFFER_SIZE 1024

int main(int argc, char const* argv[])
{
    int server_fd, new_socket;
    ssize_t valread;
    struct sockaddr_in address;
    int opt = 1;
    socklen_t addrlen = sizeof(address);
    char buffer[BUFFER_SIZE] = {0};
    char* hello = "Hello from server";

    // Создание файлового дескриптора сокета
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("ошибка создания сокета");
        exit(EXIT_FAILURE);
    }

    // Установка опций сокета
    if (setsockopt(server_fd, SOL_SOCKET,
                   SO_REUSEADDR | SO_REUSEPORT, &opt,
                   sizeof(opt))) {
        perror("ошибка setsockopt");
        exit(EXIT_FAILURE);
    }

    // Настройка адреса сервера
    address.sin_family = AF_INET;          // IPv4
    address.sin_addr.s_addr = INADDR_ANY;  // Принимать соединения с любого IP
    address.sin_port = htons(PORT);        // Порт 8080

    // Привязка сокета к порту
    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        perror("ошибка привязки");
        exit(EXIT_FAILURE);
    }

    // Прослушивание входящих соединений
    if (listen(server_fd, 3) < 0) {
        perror("ошибка прослушивания");
        exit(EXIT_FAILURE);
    }

    printf("Сервер слушает на порту %d\n", PORT);

    // Основной цикл сервера
    while (1) {
        // Принятие входящего соединения
        if ((new_socket = accept(server_fd, (struct sockaddr*)&address, &addrlen)) < 0) {
            perror("ошибка принятия соединения");
            continue; // Продолжаем работу вместо завершения
        }

        printf("Соединение установлено\n");

        // Очистка буфера
        memset(buffer, 0, BUFFER_SIZE);

        // Чтение данных от клиента
        valread = read(new_socket, buffer, BUFFER_SIZE - 1);
        if (valread > 0) {
            buffer[valread] = '\0'; // Добавляем нулевой терминатор
            printf("Получено: %s\n", buffer);
            
            // Отправка ответа клиенту
            send(new_socket, hello, strlen(hello), 0);
            printf("Ответ отправлен: %s\n", hello);
        } else if (valread == 0) {
            printf("Клиент отключился\n");
        } else {
            perror("ошибка чтения");
        }

        // Закрытие соединенного сокета
        close(new_socket);
        printf("Соединение закрыто\n\n");
    }

    // Закрытие слушающего сокета
    close(server_fd);
    return 0;
}