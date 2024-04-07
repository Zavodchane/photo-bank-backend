## Запуск
1. Склонируйте репозиторий:
```
git clone https://github.com/sunrekay/photo-bank-backend
```
2. Перейдите в него:
```
cd photo-bank-backend
```
3. Смените имя: ".env-example" -> ".env"

4. Создайте публичный и приватный ключ:
```
openssl genrsa -out ./certs/jwt-private.pem 2048
```
```
openssl rsa -in ./certs/jwt-private.pem -outform PEM -pubout -out ./certs/jwt-public.pem
```
5. Соберите контейнеры:
```
docker compose build
```
6. Запустите:
```
docker compose up
```
7. Перейти по ссылке: http://127.0.0.1:8000/docs
