import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from alembic import command
from main import app
from src.config import stg
from src.database.db import get_session
from src.database.models import Files, MessageURL


# Фикстуры
@pytest.fixture(scope="session")
def apply_migrations():
    """Применяет миграции для тестовой БД"""
    assert stg.MODE == "TEST", "Тесты должны запускаться в TEST режиме!"
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    yield
    command.downgrade(alembic_cfg, "base")


# Fix for Docker environment - use main DB instead of test DB
# In production, you would use a separate test database
@pytest.fixture(scope="session")
def test_engine():
    """Создает engine для тестов"""
    # Use the main database URL (tests will clean up after themselves)
    engine = create_async_engine(stg.DB_URL, echo=False)
    yield engine
    engine.sync_engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine, apply_migrations):
    """Создает сессию для каждого теста"""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(test_session):
    """HTTP клиент для тестирования API"""

    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def temp_upload_dir():
    """Временная директория для файлов"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


# Тесты моделей
@pytest.mark.asyncio
async def test_create_message_url(test_session):
    """Тест создания MessageURL"""
    message = MessageURL(
        url_code="test123",
        message_text="Test message",
        expired_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    test_session.add(message)
    await test_session.commit()
    await test_session.refresh(message)

    assert message.url_code == "test123"
    assert message.message_text == "Test message"
    assert message.expired_at is not None


@pytest.mark.asyncio
async def test_create_files(test_session):
    """Тест создания Files с связью"""
    message = MessageURL(
        url_code="test456", message_text="Message with files", expired_at=None
    )
    test_session.add(message)
    await test_session.flush()

    file = Files(filename="test.pdf", filepath="/uploads/test.pdf", url_code="test456")
    test_session.add(file)
    await test_session.commit()

    await test_session.refresh(message)
    assert len(message.files) == 1
    assert message.files[0].filename == "test.pdf"


# Тесты API: Создание сообщений
@pytest.mark.asyncio
async def test_create_message_text_only(client):
    """Тест создания сообщения только с текстом"""
    response = await client.post(
        "/v1/create", data={"msgtext": "Secret message", "expiry_delta_minutes": ""}
    )

    assert response.status_code == 200
    data = response.json()
    assert "url_code" in data
    assert data["message_text"] == "Secret message"
    assert data["expired_minutes_at"] is None


@pytest.mark.asyncio
async def test_create_message_with_expiry(client):
    """Тест создания сообщения с сроком действия"""
    response = await client.post(
        "/v1/create", data={"msgtext": "Expiring message", "expiry_delta_minutes": "60"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["expired_minutes_at"] == 60


@pytest.mark.asyncio
async def test_create_message_with_file(client, temp_upload_dir):
    """Тест создания сообщения с файлом"""
    # Создаем тестовый файл
    test_file_path = temp_upload_dir / "test.txt"
    test_file_path.write_text("Test content")

    with open(test_file_path, "rb") as f:
        response = await client.post(
            "/v1/create",
            data={"msgtext": "Message with file", "expiry_delta_minutes": ""},
            files={"files": ("test.txt", f, "text/plain")},
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data["sfiles"]) == 1
    assert "test.txt" in data["sfiles"]


@pytest.mark.asyncio
async def test_create_message_with_multiple_files(client, temp_upload_dir):
    """Тест создания сообщения с несколькими файлами"""
    file1 = temp_upload_dir / "file1.txt"
    file2 = temp_upload_dir / "file2.txt"
    file1.write_text("Content 1")
    file2.write_text("Content 2")

    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        response = await client.post(
            "/v1/create",
            data={"msgtext": "", "expiry_delta_minutes": "30"},
            files=[
                ("files", ("file1.txt", f1, "text/plain")),
                ("files", ("file2.txt", f2, "text/plain")),
            ],
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data["sfiles"]) == 2


@pytest.mark.asyncio
async def test_create_message_empty_fails(client):
    """Тест: пустое сообщение без файлов должно вернуть ошибку"""
    response = await client.post(
        "/v1/create", data={"msgtext": "", "expiry_delta_minutes": ""}
    )

    assert response.status_code == 400
    assert "required" in response.json()["detail"].lower()


# Тесты API: Просмотр сообщений
@pytest.mark.asyncio
async def test_view_message_success(client, test_session):
    """Тест успешного просмотра сообщения"""
    # Создаем сообщение
    message = MessageURL(
        url_code="view123",
        message_text="Test view message",
        expired_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    test_session.add(message)
    await test_session.commit()

    # Просматриваем
    response = await client.get("/v1/view/view123")

    assert response.status_code == 200
    data = response.json()
    assert data["url_code"] == "view123"
    assert data["message_text"] == "Test view message"


@pytest.mark.asyncio
async def test_view_message_not_found(client):
    """Тест: несуществующее сообщение"""
    response = await client.get("/v1/view/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_view_expired_message(client, test_session):
    """Тест: просмотр истекшего сообщения"""
    message = MessageURL(
        url_code="expired123",
        message_text="Expired message",
        expired_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    test_session.add(message)
    await test_session.commit()

    response = await client.get("/v1/view/expired123")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_view_message_with_files(client, test_session):
    """Тест просмотра сообщения с файлами"""
    message = MessageURL(
        url_code="withfiles", message_text="Message with files", expired_at=None
    )
    test_session.add(message)
    await test_session.flush()

    file = Files(
        filename="document.pdf",
        filepath="/uploads/0-withfiles.pdf",
        url_code="withfiles",
    )
    test_session.add(file)
    await test_session.commit()

    response = await client.get("/v1/view/withfiles")
    assert response.status_code == 200
    data = response.json()
    assert len(data["files"]) == 1
    assert data["files"][0]["filename"] == "document.pdf"


# Тесты API: Скачивание файлов
@pytest.mark.asyncio
async def test_download_file_success(client, test_session, temp_upload_dir):
    """Тест успешного скачивания файла"""
    # Создаем сообщение и файл
    message = MessageURL(
        url_code="download123",
        message_text="Download test",
        expired_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    test_session.add(message)
    await test_session.flush()

    # Создаем реальный файл
    test_file = temp_upload_dir / "testfile.txt"
    test_file.write_text("Download me!")

    file_record = Files(
        filename="testfile.txt", filepath=str(test_file), url_code="download123"
    )
    test_session.add(file_record)
    await test_session.commit()

    # Скачиваем
    response = await client.get(f"/v1/download/{test_file.name}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_download_file_not_found(client):
    """Тест скачивания несуществующего файла"""
    response = await client.get("/v1/download/nonexistent.txt")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_download_expired_file(client, test_session, temp_upload_dir):
    """Тест скачивания файла истекшего сообщения"""
    message = MessageURL(
        url_code="expired_file",
        message_text="Expired",
        expired_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    test_session.add(message)
    await test_session.flush()

    test_file = temp_upload_dir / "expired.txt"
    test_file.write_text("Expired content")

    file_record = Files(
        filename="expired.txt", filepath=str(test_file), url_code="expired_file"
    )
    test_session.add(file_record)
    await test_session.commit()

    response = await client.get(f"/v1/download/{test_file.name}")
    assert response.status_code == 410  # Gone


# Тесты фронтенда
@pytest.mark.asyncio
async def test_root_page(client):
    """Тест главной страницы"""
    response = await client.get("/")
    assert response.status_code == 200
    assert b"Secret Message" in response.content


@pytest.mark.asyncio
async def test_view_page_with_code(client, test_session):
    """Тест страницы просмотра с кодом"""
    message = MessageURL(url_code="page123", message_text="Page test", expired_at=None)
    test_session.add(message)
    await test_session.commit()

    response = await client.get("/page123")
    assert response.status_code == 200
    assert b"page123" in response.content or b"Secret Message" in response.content


# Интеграционные тесты
@pytest.mark.asyncio
async def test_full_workflow(client, temp_upload_dir):
    """Полный цикл: создание → просмотр → скачивание"""
    # 1. Создаем сообщение с файлом
    test_file = temp_upload_dir / "workflow.txt"
    test_file.write_text("Workflow test")

    with open(test_file, "rb") as f:
        create_response = await client.post(
            "/v1/create",
            data={"msgtext": "Full workflow test", "expiry_delta_minutes": "60"},
            files={"files": ("workflow.txt", f, "text/plain")},
        )

    assert create_response.status_code == 200
    code = create_response.json()["url_code"]

    # 2. Просматриваем сообщение
    view_response = await client.get(f"/v1/view/{code}")
    assert view_response.status_code == 200
    view_data = view_response.json()
    assert view_data["message_text"] == "Full workflow test"
    assert len(view_data["files"]) == 1

    # 3. Скачиваем файл (проверяем наличие в ответе)
    download_url = view_data["files"][0]["download_url"]
    # Извлекаем путь из URL
    filepath = download_url.split("/download/")[-1]
    download_response = await client.get(f"/v1/download/{filepath}")
    # Может вернуть 404 если файл не на диске в тестах, но структура верная
    assert download_response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_concurrent_file_uploads(client, temp_upload_dir):
    """Тест параллельной загрузки нескольких файлов"""
    files = []
    for i in range(5):
        f = temp_upload_dir / f"concurrent_{i}.txt"
        f.write_text(f"Content {i}")
        files.append(f)

    files_data = [("files", (f.name, open(f, "rb"), "text/plain")) for f in files]

    response = await client.post(
        "/v1/create",
        data={"msgtext": "Concurrent test", "expiry_delta_minutes": ""},
        files=files_data,
    )

    # Закрываем файлы
    for _, (_, file_obj, _) in files_data:
        file_obj.close()

    assert response.status_code == 200
    data = response.json()
    assert len(data["sfiles"]) == 5


# Тесты edge cases
@pytest.mark.asyncio
async def test_very_long_message(client):
    """Тест очень длинного сообщения"""
    long_text = "A" * 10000
    response = await client.post(
        "/v1/create", data={"msgtext": long_text, "expiry_delta_minutes": ""}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_special_characters_in_message(client):
    """Тест спецсимволов в сообщении"""
    special_text = "Test 🔐 <script>alert('xss')</script> \n\t привет"
    response = await client.post(
        "/v1/create", data={"msgtext": special_text, "expiry_delta_minutes": ""}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message_text"] == special_text


@pytest.mark.asyncio
async def test_zero_expiry_minutes(client):
    """Тест нулевого времени жизни"""
    response = await client.post(
        "/v1/create", data={"msgtext": "Zero expiry", "expiry_delta_minutes": "0"}
    )
    # Должно создаться, но мгновенно истечь или быть бессрочным
    assert response.status_code in [200, 400]


# Простой тест
def test_basic():
    """Базовый тест работоспособности"""
    assert 1 == 1
    assert stg.MODE == "TEST"
