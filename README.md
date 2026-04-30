## observability_example

Локальный стенд для скриншотов по урокам про Prometheus, Grafana, Netdata, Zabbix и Nagios.

### Что внутри

* `shop-api` — заглушка приложения на Python (`uv`, FastAPI) с эндпоинтами `/`, `/checkout`, `/health`, `/metrics`
* `nginx` — входная точка для трафика к приложению
* `postgres`, `redis` — инфраструктурные зависимости
* `prometheus`, `alertmanager`, `grafana` — стек мониторинга и визуализации
* `node-exporter-1..3`, `postgres-exporter`, `blackbox-exporter` — источники метрик
* `netdata` — отдельный UI для «из коробки» наблюдаемости
* `loadgen` — генератор трафика для живых графиков
* `zabbix-*` и `nagios` — запускаются отдельными профилями

### Быстрый старт

```bash
docker compose up -d --build
```

Проверка состояния:

```bash
docker compose ps
```

### URL сервисов

* App API: `http://localhost:8000`
* Nginx (входной трафик): `http://localhost:8080`
* Prometheus: `http://localhost:9090`
* Alertmanager: `http://localhost:9093`
* Grafana (`admin/admin`): `http://localhost:3000`
* Netdata: `http://localhost:19999`
* Postgres Exporter: `http://localhost:9187/metrics`

### Профили

Zabbix:

```bash
docker compose --profile zabbix up -d
```

* Zabbix Web: `http://localhost:8081`
* Логин/пароль по умолчанию: `Admin` / `zabbix`
* Хост `zabbix-agent` создается автоматически сервисом `zabbix-bootstrap`
* Проверка, что bootstrap отработал:

```bash
docker compose --profile zabbix logs zabbix-bootstrap
```

Nagios:

```bash
docker compose --profile nagios up -d
```

* Nagios Web: `http://localhost:8082`
* Логин/пароль по умолчанию: `nagiosadmin` / `nagios`
* В стенде уже есть синтетические `Warning` и `Critical` сервисы для скриншота Tactical Overview

### Что снимать для скриншотов

* Prometheus `Status -> Targets` (должно быть несколько `UP`)
* Grafana Data Source (Prometheus подключен)
* Grafana dashboard `Shop API Overview` (RED: Rate/Errors/Duration)
* Netdata overview + разделы CPU/PostgreSQL
* Zabbix стартовый экран, форма создания узла, `Latest data` (host `zabbix-agent` уже добавлен)
* Nagios обзорный экран (`Tactical Overview`)

### Остановка

```bash
docker compose down
```

Полная очистка данных:

```bash
docker compose down -v
```
