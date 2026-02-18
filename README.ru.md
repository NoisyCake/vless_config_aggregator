<div align="center" markdown>

<p align="center">
    <a href="https://github.com/NoisyCake/3x-ui_subscriptions_aggregator/blob/main/README.md"><u><b>ENGLISH</b></u></a> •
    <a href="https://github.com/NoisyCake/3x-ui_subscriptions_aggregator/blob/main/README.ru.md"><u><b>РУССКИЙ</b></u></a>
</p>

# vless_config_aggregator

Ревёрс-прокси, предоставляющий доступ к множеству различных VLESS-конфигураций с разных серверов через единую ссылку.

Подробное описание проекта доступно [на сайте автора](https://noisycake.ru/projects/subs_aggregator)
</div>

## Подготовка

> [!NOTE]
> Инструкция актуальна для Debian-based дистрибутивов Linux. Тестирование проводились в основном с клиентом sing-box Hiddify

### Сертификат
Сервис подразумевает обязательное наличие SSL сертификата, поэтому сначала необходимо его получить. Для этого потребуется привязать домен к IP целевого сервера.

После получения домена выполните следующие команды (80 или 443 порты должны быть открыты):
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install certbot

sudo certbot certonly --standalone -d <domain> --register-unsafely-without-email
```

Ключи будут лежать в директории "/etc/letsencrypt/live/<domain>/"

### Подписки
Если вы собираетесь использовать не только прямые ссылки на конфигурации (`vless://`), но и "подписочные" ссылки, то в каждой панели 3x-ui нужно настроить функцию подписки.  
Для клиентов, подписки которых вы хотите объединить, требуется установить одинаковый **subscription ID**.

![Сервер 1](https://i.ibb.co/672ypTMt/image.png)

![Сервер 2](https://i.ibb.co/sSn9byZ/2025-03-18-153330.png)

### Файл с конфигами
Чтобы всё заработало, также необходимо создать и разместить на GitHub или локально текстовый файл со списком всех конфигураций.

Как уже упоминалось, поддерживаются два вида ссылок: подписки и прямые. Прямые вставляются как есть.  
Для подписок нужно удалить subscription ID из URL. То есть от `https://<domain>:<port>/<url>/<subscription_id>` должно остаться только `https://<domain>:<port>/<url>/` (обратите внимание на наличие конечного слэша).

Пример:
```txt
https://subscription_link_example:1/imy/
https://subscription_link_example:2/sub/
vless://...
vless://...
vless://...
```

---
## Установка и настройка

Скачайте и установите необходимые инструменты:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git curl

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

Скачайте репозиторий и перейдите в него:
```bash
git clone https://github.com/NoisyCake/vless_config_aggregator.git
cd vless_config_aggregator
cp .env.template .env
```

### Переменные окружения
В файле `.env` содержится несколько переменных, которые нужно настроить:
|variable|description|example|
|:--:|:--|:--|
|LOCAL_MODE|Если включено, ищет файл на хосте. Иначе пытается достать из удалённого репозитория|on|
|FILE_PATH|Абсолютный путь к `.txt` файлу конфигураций|/path/to/configs.txt|
|CONFIG_URL|Ссылка на `.txt` файл конфигураций|https://api.github.com/.../file.txt|
|GITHUB_TOKEN|Токен доступа GitHub (если файл находится в приватном репозитории)|ghp_dhoauigc7898374yduisdhSDHFHGf7|
|SUB_NAME|Имя подписки, которое будет отображаться в клиенте. Если не указано, им станет subscription ID из 3x-ui|HFK|
|PROFILE_TITLE| Название профиля в Happ. Если не указано, используется SUB_NAME. Можно писать base64:... чтобы безопасно передавать Unicode.|base64:WmVyZ29uR2F0ZSDwn46A|
|SUPPORT_URL| Ссылка на поддержку.|https://t.me/naixzergon
|PROFILE_WEB_PAGE_URL|Ссылка на сайт в Happ|https:t.me/Komaru_GIF|
|ANNOUNCE|Текст баннера. Можно обычный текст или base64:....|Hello, world!|
|PROFILE_UPDATE_INTERVAL|Интервал обновления профиля в часах|24|
|PROVIDER_ID|ID провайдера Happ|example|
|SERVER_NAME|Доменное имя сервера, на котором установлен сервис|domain.or.subdomain|
|PORT|Порт, на котором будет работать сервис|443|
|URL|Часть пути новой подписки|sub|
|CERT_PATH|Абсолютный путь к SSL-сертификату|/etc/letsencrypt/live/domain.or.subdomain|

---
## Запуск

Запуск производится командой `sudo docker compose up --build -d`.

Общая ссылка на объединение конфигов может выглядеть по-разному:
1. Если в `.txt` нет подписочных ссылок или их не требуется использовать: `https://{SERVER_NAME}:{PORT}/{URL}/{SUB_NAME}`;
2. Иначе, ожидаемое будет находиться по адресу `https://{SERVER_NAME}:{PORT}/{URL}/subscription_id/{SUB_NAME}`, где subscription_id — имя подписки на 3x-ui серверах.

В обоих случаях часть `/{SUB_NAME}`, очевидно, не нужна, если переменная пуста.

---
## Лицензия

Проект распространяется под лицензией MIT. Подробности в файле `LICENSE`.

---
## Изменения и предложения

Вы можете отслеживать изменения версий на странице Релизов.
Предложения, сообщения об ошибках и pull requests приветствуются!
