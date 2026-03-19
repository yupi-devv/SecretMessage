# 🔐 Secret Message / Секретное Сообщение

**Secure self-destructing messages with file attachments**  
**Безопасные самоуничтожающиеся сообщения с файлами**

---

## 📖 Описание / Description

A modern, privacy-focused web application that allows you to create secure, self-destructing messages with optional file attachments. Messages automatically expire after a configurable time period, ensuring your sensitive information doesn't linger indefinitely.

Современное веб-приложение с фокусом на конфиденциальность, позволяющее создавать безопасные самоуничтожающиеся сообщения с возможностью прикрепления файлов. Сообщения автоматически удаляются после истечения настроенного времени, гарантируя, что ваша конфиденциальная информация не останется навсегда.

---

## ✨ Features / Возможности

| 🇬🇧 English | 🇷🇺 Русский |
|-------------|-------------|
| 🔒 End-to-End Privacy | 🔒 Полная конфиденциальность |
| ⏰ Custom Expiration Time | ⏰ Настраиваемое время жизни |
| 📎 File Attachments Support | 📎 Поддержка файловых вложений |
| 🎨 Modern Beautiful UI | 🎨 Современный красивый интерфейс |
| 📱 Mobile-First Design | � Дизайн для мобильных устройств |
| 🚀 High Performance (FastAPI) | � Высокая производительность (FastAPI) |
| 🔗 Cryptographically Secure URLs | 🔗 Криптографически защищённые URL |
| 🌐 Telegram WebApp Support | 🌐 Поддержка Telegram WebApp |

---

## 🚀 Quick Start / Быстрый старт

### Prerequisites / Требования

- Python 3.10 or higher / Python 3.10 или выше
- [uv](https://github.com/astral-sh/uv) package manager
- PostgreSQL database

### Installation / Установка

1. **Clone the repository / Склонируйте репозиторий**
   ```bash
   git clone https://github.com/yourusername/SecretMessage.git
   cd SecretMessage
   ```

2. **Install dependencies / Установите зависимости**
   ```bash
   uv sync
   ```

3. **Configure environment / Настройте окружение**
   
   Create a `.env` file / Создайте файл `.env`:
   ```env
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=secretmsg
   FILES_DIR=uploads
   BASE_URL=localhost:8000
   MODE=TEST
   ```

4. **Run database migrations / Запустите миграции БД**
   ```bash
   alembic upgrade head
   ```

5. **Start the server / Запустите сервер**
   ```bash
   uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Open in browser / Откройте в браузере**
   ```
   http://localhost:8000
   ```

---

## 🐳 Docker Deployment / Развёртывание в Docker

### Using Docker Compose / С помощью Docker Compose

```bash
# Start application with tests / Запустить приложение с тестами
docker-compose up -d

# Run tests only / Запустить только тесты
docker-compose up test
```

This will start both the application and PostgreSQL database.  
Это запустит приложение и базу данных PostgreSQL.

**What happens on startup / Что происходит при запуске:**
1. Database migrations run automatically / Миграции БД запускаются автоматически
2. Tests execute on every container creation / Тесты выполняются при каждом создании контейнера
3. Application starts after tests (even if they fail) / Приложение запускается после тестов (даже если они упали)

### Manual Docker / Вручную через Docker

```bash
docker build -t secret-message .
docker run -p 8000:8000 --env-file .env secret-message
```

---

## 📖 API Documentation / Документация API

Once the server is running, visit:  
После запуска сервера посетите:

- **Swagger UI**: http://localhost:8000/docs
- **Alternative / Альтернатива**: http://localhost:8000/redoc

### Endpoints / Эндпоинты

| Method | Endpoint | Description / Описание |
|--------|----------|------------------------|
| `POST` | `/v1/create` | Create a new secret message / Создать новое сообщение |
| `GET` | `/v1/view/{code}` | View a message by its code / Просмотр сообщения по коду |
| `GET` | `/v1/download/{filepath}` | Download an attached file / Скачать прикреплённый файл |

---

## ⚙️ Configuration / Конфигурация

### Environment Variables / Переменные окружения

| Variable / Переменная | Description / Описание | Default / По умолчанию |
|----------------------|------------------------|------------------------|
| `DB_USER` | PostgreSQL username / Пользователь БД | Required / Обязательно |
| `DB_PASSWORD` | PostgreSQL password / Пароль БД | Required / Обязательно |
| `DB_HOST` | Database host / Хост БД | Required / Обязательно |
| `DB_PORT` | Database port / Порт БД | `5432` |
| `DB_NAME` | Database name / Имя БД | Required / Обязательно |
| `MODE` | Application mode / Режим приложения | `TEST` |
| `BASE_URL` | Production domain / Домен продакшена | `localhost:8000` |
| `FILES_DIR` | Upload directory / Папка загрузок | `uploads` |

### Expiration Options / Варианты срока действия

| English | Русский |
|---------|---------|
| 1 hour | 1 час |
| 1 day | 1 день |
| 7 days | 7 дней |
| 30 days | 30 дней |
| Custom duration | Своя длительность |
| No expiration | Бессрочно |

---

## 🛠️ Tech Stack / Технологический стек

### Backend / Бэкенд
- **FastAPI** - Modern async web framework / Современный асинхронный веб-фреймворк
- **SQLAlchemy** - Async ORM for database operations / Асинхронный ORM для работы с БД
- **PostgreSQL** - Primary database / Основная база данных
- **Pydantic** - Data validation and settings / Валидация данных и настройки
- **Aiofiles** - Async file handling / Асинхронная работа с файлами

### Frontend / Фронтенд
- **Vanilla JS** - Lightweight, no framework overhead / Лёгкий, без фреймворков
- **CSS3** - Custom animations and gradients / Кастомные анимации и градиенты
- **SVG Icons** - Crisp, scalable graphics / Чёткая масштабируемая графика
- **Inter Font** - Clean, modern typography / Чистая современная типографика

### DevOps
- **Docker & Docker Compose** - Containerization / Контейнеризация
- **Alembic** - Database migrations / Миграции БД
- **uv** - Fast Python package management / Быстрый менеджер пакетов

---

## 📁 Project Structure / Структура проекта

```
SecretMessage/
├── alembic/                 # Database migrations / Миграции БД
├── src/
│   ├── database/
│   │   ├── db.py           # Database connection / Подключение к БД
│   │   └── models.py       # SQLAlchemy models / Модели SQLAlchemy
│   ├── endpoints.py         # API route handlers / Обработчики API
│   ├── schemas.py           # Pydantic models / Модели Pydantic
│   ├── service.py           # Business logic / Бизнес-логика
│   └── config.py            # Configuration / Конфигурация
├── templates/
│   └── index.html          # Main frontend template / Главный шаблон
├── uploads/                 # File storage / Хранилище файлов
├── tests/                   # Test suite / Тесты
├── docker-compose.yml       # Docker services / Сервисы Docker
├── Dockerfile              # Container build / Сборка контейнера
└── main.py                 # Application entry / Точка входа
```

---

## 🔒 Security Features / Функции безопасности

| English | Русский |
|---------|---------|
| Cryptographic code generation | Криптографическая генерация кодов |
| UUID integration for uniqueness | UUID для уникальности |
| Automatic cleanup of expired messages | Автоматическая очистка истёкших сообщений |
| File isolation with prefixed names | Изоляция файлов с префиксами |
| Configurable CORS policies | Настраиваемые CORS политики |
| Timezone-aware datetime handling | Учёт часовых поясов |

---

## 🧪 Testing / Тестирование

### Running Tests / Запуск тестов

**With Docker (recommended) / В Docker (рекомендуется):**
```bash
# Run tests in isolated container / Запустить тесты в изолированном контейнере
docker-compose up test

# Start app with tests / Запустить приложение с тестами
docker-compose up -d
```

**Local / Локально:**
```bash
# Install dev dependencies / Установить dev зависимости
uv sync --extra dev

# Run all tests / Запустить все тесты
pytest

# Run with coverage / Запустить с покрытием
pytest --cov=src

# Run specific test file / Запустить конкретный файл
pytest tests/test.py

# Run with verbose output / Запустить с подробным выводом
pytest -v

# Run tests by keyword / Запустить тесты по ключевому слову
pytest -k "create"
```

### Test Coverage / Покрытие тестами

```bash
# Generate coverage report / Сгенерировать отчёт о покрытии
pytest --cov=src --cov-report=html

# View coverage in browser / Открыть отчёт в браузере
open htmlcov/index.html  # Linux: xdg-open htmlcov/index.html
```

### What's Tested / Что тестируется

| Test Category / Категория | Description / Описание |
|---------------------------|------------------------|
| **Models** | Database models creation and relationships / Создание моделей БД и связи |
| **API Endpoints** | All `/v1/*` endpoints / Все эндпоинты `/v1/*` |
| **File Operations** | Upload, download, expiry / Загрузка, скачивание, истечение |
| **Frontend** | Page rendering / Отображение страниц |
| **Integration** | Full workflow / Полный рабочий процесс |
| **Edge Cases** | Long messages, special chars, concurrent uploads / Длинные сообщения, спецсимволы, параллельные загрузки |

---

## 🎨 Customization / Настройка

### Branding / Брендинг
Edit the SVG logo in `templates/index.html`:  
Отредактируйте SVG логотип в `templates/index.html`:

```html
<svg class="logo" viewBox="0 0 100 100">
  <!-- Your custom logo / Ваш логотип -->
</svg>
```

### Color Scheme / Цветовая схема
Modify CSS variables in the `<style>` section:  
Измените CSS переменные в секции `<style>`:

```css
:root {
    --primary: #3b82f6;      /* Main brand color / Основной цвет */
    --secondary: #8b5cf6;    /* Accent color / Акцентный цвет */
    --bg-dark: #0a0a0f;      /* Background / Фон */
}
```

---

## 🤝 Contributing / Вклад

1. Fork the repository / Форкните репозиторий
2. Create a feature branch / Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Commit your changes / Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Push to the branch / Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Open a Pull Request / Откройте Pull Request

---

## ❓ FAQ / Часто задаваемые вопросы

<details>
<summary><b>How long are messages stored? / Как долго хранятся сообщения?</b></summary>

Messages are stored until they expire (based on your settings) or until the database is cleared. By default, messages can live from 1 hour to 30 days, or indefinitely if no expiration is set.

Сообщения хранятся до истечения срока (на основе ваших настроек) или до очистки базы данных. По умолчанию сообщения могут жить от 1 часа до 30 дней, или бессрочно, если срок не установлен.
</details>

<details>
<summary><b>Are files encrypted? / Файлы шифруются?</b></summary>

Currently, files are stored on disk without encryption. For production use, consider enabling disk encryption or using a secure storage service.

В настоящее время файлы хранятся на диске без шифрования. Для продакшена рекомендуется включить шифрование диска или использовать защищённое хранилище.
</details>

<details>
<summary><b>Can I self-host this? / Могу ли я разместить это у себя?</b></summary>

Yes! The application is designed for self-hosting. Just follow the Docker or manual installation instructions above.

Да! Приложение разработано для самостоятельного размещения. Просто следуйте инструкциям по установке через Docker или вручную выше.
</details>

---

## 📄 License / Лицензия

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Проект лицензирован под лицензией MIT - подробности в файле [LICENSE](LICENSE).

---

## 🙏 Acknowledgments / Благодарности

- **FastAPI** - For the amazing web framework / За потрясающий веб-фреймворк
- **Telegram** - For WebApp integration support / За поддержку WebApp
- **Inter Font** - Beautiful typography by Rasmus Andersson / Красивая типографика от Rasmus Andersson

---

## 📞 Support / Поддержка

For issues and feature requests, please use the [GitHub Issues](https://github.com/yupi-devv/SecretMessage/issues) page.

По вопросам и предложениям, пожалуйста, используйте страницу [GitHub Issues](https://github.com/yupi-devv/SecretMessage/issues).

---

<div align="center">

**Made with ❤️ for secure communication**  
**Сделано с ❤️ для безопасной коммуникации**

[Report Bug / Сообщить об ошибке](https://github.com/yupi-devv/SecretMessage/issues) · [Request Feature / Запросить функцию](https://github.com/yupi-devv/SecretMessage/issues)

</div>
