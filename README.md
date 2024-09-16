# Сервис для настройки интеграции с KUMA нескольких инстансов SOAR

### Сервис можно устанавливать как на отдельную машину, так и рядом с R-Vision

## 1. Описание
Данный сервис работает по следующему принципу:
1. Сервис перехватывает алерт, который KUMA отправляет в SOAR
2. На основе поля company (название тенанта в KUMA) создается экземпляр класса RvisionAPI для работы с API инстансa
3. Запускается проверка на наличие инцидента в SOAR с таким же ID алерта
4. Если такого инцидента нет, то сервис запрашивает дополнительные поля из KUMA и создает новый инцидент
5. Если инцидент есть, то сервис запрашивает дополнительные поля и обновляет его

## 2. Установка
  ### Требования
       - python3.6+
       - pip3

### Создаем поля и категории инцидентов в SOAR

1. Создаем категорию "Алерт KUMA"
2. Добавляем поля
   * ID Алерта - tag: kuma_alert_id
   * Ссылка на алерт - tag: kuma_url
3. Создаем типы инцидентов, которые соответствуют по названию с кореляционными правилами в KUMA и добавляем их в созданную категорию

![image](https://github.com/user-attachments/assets/f1286e67-875b-4990-9032-7873a0c7a1a0)

### Виртуальное окружение
Собираем виртуальное окружение python с использованием файла `requirements.txt`
```requirements.txt
anyio==3.6.2
certifi==2023.5.7
charset-normalizer==3.1.0
click==8.1.3
colorama==0.4.6
fastapi==0.95.2
h11==0.14.0
idna==3.4
pydantic==1.10.7
python-multipart==0.0.6
PyYAML==6.0
requests==2.30.0
sniffio==1.3.0
starlette==0.27.0
typing_extensions==4.5.0
urllib3==2.0.2
uvicorn==0.22.0
```

Добавляем в него библиотеку pyrvision версии 1.1

    pip3 install pyrvision-1.1.10-py3-none-any.whl

### Файлы сервиса
1. Скачиваем архив и переносим его в директорию `/opt/rvision/kuma`
2. В файлах `kuma.py`, `service.py` и `rvision.py` прописываем в `os.chdir()` путь до директории, в которой находятся файлы (в данном случае `/opt/rvision/kuma`)
3. Редактируем файл `config.yaml`
```yaml
script:
  host: script_ip # IP-адрес сервера, на котором будет работать сервис
  port: sсript_port # порт, на котором будет работать сервис
rvision:
  tenant_1:
    host: rvision1_ip  # IP-адрес инсталляции R-Vision
    tenant_1_name: tenant1_name  # указать имя первого тенанта KUMA [название тенанта в KUMA должно совпадать с наименованием организации в R-Vision]
    token: api_token_rvision1  # API-токен
  tenant_2:
    host: rvision2_ip  # IP-адрес второй инсталляции R-Vision
    tenant_2_name: tenant2_name  #указать имя второго тенанта KUMA
    token: api_token_rvision2
  protocol: https
alert:
  alert_id_tag: kuma_alert_id # тег поля ID алерта в SOAR [в конфиге менять не нужно]
  kuma_url_tag: kuma_url # тег поля ссылка на алерт в SOAR [в конфиге менять не нужно]
  category: KUMA_ALERT # категория инцидента в SOAR [в конфиге менять не нужно]
kuma:
  host: kuma_host:7223 # имя сервера KUMA
  token: api_token_kuma # API токен KUMA
```

### Настройка systemd
1. Переносим файл `kuma.service` в директорию `/etc/systemd/system/`
2. Редактируем файл `kuma.service`
```unit file (systemd)
[Unit]
Description=KUMA service
After=network.target

[Service]
Type=idle
User=your_user           # Здесь укажите непривилегированного пользователя
Group=your_group          # Опционально, если нужно указать группу
# ExecStart=путь до виртуального окружения/bin/python3 /путь до файла service.py
ExecStart=/opt/rvision_scripts/env/bin/python3 /opt/rvision_scripts/kuma/service.py
Restart=always

[Install]
WantedBy=multi-user.target

```
Пояснение:
User=your_user — замените your_user на имя непривилегированного пользователя, от имени которого вы хотите запускать сервис. Этот пользователь должен иметь доступ к необходимым файлам и директориям.
Group=your_group — если требуется, укажите группу, к которой принадлежит пользователь. Это опциональная настройка.

Дополнительно:
Убедитесь, что пользователь, указанный в директиве User, имеет права на выполнение скрипта и доступ к его файлам.
Также важно проверить, что у пользователя есть доступ к Python-интерпретатору и виртуальному окружению.


### 3. Выполняем команды
```shell
systemctl daemon-reload
systemctl enable kuma
systemctl start kuma
```

### Настройка KUMA
1. В интерфейсе переходим в раздел настройки интеграции IRP/SOAR
2. Выполним настройку
* Секрет - Токен SOAR
* URL = `http://{имя хоста, на котором установлен сервис}:{порт сервиса}`
* Поле ID алерта - alert_id
* Поле URL алерта - kuma_url
* Категория - Любая
* Поля = Любые
* Уровни важности - Как в SOAR

![image](https://github.com/user-attachments/assets/36b95fbf-5fd7-4c4b-92a0-9229c2a507c9)


P.S. Выполнять настройки в KUMA нужно с работающим сервисом, после изменения настроек сделать рестарт сервиса
