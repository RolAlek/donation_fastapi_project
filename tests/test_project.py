import os
from http import HTTPStatus

import pytest

from tests.conftest import PROJECT_URL, PROJECT_DETAIL


EXPECTED_KEYS = {
    "name",
    "description",
    "full_amount",
    "id",
    "invested_amount",
    "fully_invested",
    "created_date",
}


@pytest.mark.parametrize(
    "invalid_name",
    [None, "", "a" * 101],
    ids=["null", "empty", "too long"],
)
def test_create_project_with_invalid_name(superuser_client, invalid_name):
    response = superuser_client.post(
        PROJECT_URL,
        json={
            "name": invalid_name,
            "description": "Project test description",
            "full_amount": 1000,
        },
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        "Создание проекта с пустым именем или больше 100 символов не"
        " допустимо."
    )


@pytest.mark.parametrize(
    "non_desc",
    [None, ""],
    ids=["null", "empty"],
)
def test_create_project_with_non_description(non_desc, superuser_client):
    response = superuser_client.post(
        PROJECT_URL,
        json={
            "name": "Project test name",
            "description": non_desc,
            "full_amount": 1000,
        },
    )
    assert (
        response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    ), "Создание проекта с пустым описанием не допустимо."


@pytest.mark.parametrize(
    "json_data",
    [
        {"invested_amount": 1000},
        {"fully_invested": True},
        {"id": 100},
    ],
)
def test_create_project_with_default_filling_fields(
    json_data, superuser_client
):
    response = superuser_client.post(
        PROJECT_URL,
        json=json_data,
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        "При попытке передавать автозаполняемые поля при создании проекта"
        " должна возращать ошибка 422."
    )


@pytest.mark.parametrize(
    "invalid_amount",
    [None, "", 0, -1, "string"],
    ids=["None", "empty_string", "null", "negative", "string"],
)
def test_create_project_with_invalid_amount(invalid_amount, superuser_client):
    response = superuser_client.post(
        PROJECT_URL,
        json={
            "name": "Project test name",
            "description": "Project test description",
            "full_amount": invalid_amount,
        },
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        "Создание проекта с пустым, меньше 1 или строковым значением суммы не"
        " допустимо."
    )


def test_create_project(superuser_client, correct_create_testing_data):
    response = superuser_client.post(
        PROJECT_URL,
        json=correct_create_testing_data,
    )
    assert (
        response.status_code == HTTPStatus.CREATED
    ), "Создание проекта с корректными данными не должно вызывать ошибок."
    data = response.json()
    missing_keys = EXPECTED_KEYS - data.keys()
    assert not missing_keys, (
        f"При коректном запросе на создание проекта к {PROJECT_URL} в ответе"
        f" не хватает следующих ключей: `{"`, `".join(missing_keys)}`"
    )
    data.pop("created_date")
    data.pop("close_date", None)
    assert data == {
        "id": 1,
        "name": "Test name",
        "description": "Test description",
        "full_amount": 1000,
        "fully_invested": False,
        "invested_amount": 0,
    }, (
        f"При POST-запросе к {PROJECT_URL} ответ отличается от ожидаемого. Убедитесь,"
        "что пустые поля не показывются в ответе"
    )


@pytest.mark.usefixtures("charity_project_first", "charity_project_second")
def test_get_all_projects(superuser_client):
    response = superuser_client.get(PROJECT_URL)
    assert (
        response.status_code == HTTPStatus.OK
    ), f"GET-запрос к {PROJECT_URL} должен вернуть код 200."
    data = response.json()
    [project.pop("close_date", None) for project in data]
    assert data == [
        {
            "id": 1,
            "name": "Test Charity Project number 1",
            "description": "This is a test charity project number 1",
            "full_amount": 1000,
            "created_date": "2023-01-01T00:00:00",
            "fully_invested": False,
            "invested_amount": 0,
        },
        {
            "id": 2,
            "name": "Test Charity Project number 2",
            "description": "This is a test charity project number 2",
            "full_amount": 2000,
            "created_date": "2023-02-01T00:00:00",
            "fully_invested": False,
            "invested_amount": 0,
        },
    ], (
        f"GET-запрос к {PROJECT_URL} должен вернуть список существующих"
        " проектов."
    )


@pytest.mark.parametrize(
    "json_data",
    [
        {
            "name": "Test name change",
            "description": "Test description change",
            "full_amount": 2000,
        }
    ],
)
def test_update_project_with_non_exist_id(superuser_client, json_data):
    response = superuser_client.patch(PROJECT_DETAIL, json=json_data)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        "Запрос с попыткой обновления проекта с несуществующим id должен"
        " возвращать ошибку со статусом 404"
    )


@pytest.mark.usefixtures("charity_project_with_invested_amount")
def test_update_project_with_full_amount_less_invested(superuser_client):
    response = superuser_client.patch(
        os.path.join(PROJECT_URL, "3"),
        json={"full_amount": 500},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, (
        "Запрос с попыткой поменять необходимую сумму проекта на меньшую чем"
        " уже внесено должен возвращать ошибку 422"
    )


@pytest.mark.usefixtures("closed_charity_project")
def test_update_closed_project(superuser_client):
    response = superuser_client.patch(
        os.path.join(PROJECT_URL, "4"),
        json={"name": "Test change name to closed project"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, (
        "Запрос с попыткой обновления закрытого проекта должен"
        " возвращать ошибку 422."
    )


@pytest.mark.usefixtures("charity_project_first")
@pytest.mark.parametrize(
    "json_data, expected_data",
    [
        (
            {"full_amount": 2000},
            {
                "id": 1,
                "name": "Test Charity Project number 1",
                "description": "This is a test charity project number 1",
                "full_amount": 2000,
                "created_date": "2023-01-01T00:00:00",
                "fully_invested": False,
                "invested_amount": 0,
            },
        ),
        (
            {"name": "Testing change project name"},
            {
                "id": 1,
                "name": "Testing change project name",
                "description": "This is a test charity project number 1",
                "full_amount": 1000,
                "created_date": "2023-01-01T00:00:00",
                "fully_invested": False,
                "invested_amount": 0,
            },
        ),
        (
            {"description": "Testing change project description"},
            {
                "id": 1,
                "name": "Test Charity Project number 1",
                "description": "Testing change project description",
                "full_amount": 1000,
                "created_date": "2023-01-01T00:00:00",
                "fully_invested": False,
                "invested_amount": 0,
            },
        ),
    ],
)
def test_update_project(
    superuser_client,
    charity_project_first,
    json_data,
    expected_data,
):
    response = superuser_client.patch(PROJECT_DETAIL, json=json_data)
    assert (
        response.status_code == 200
    ), (
        f"Коректный PATCH-запрос к {PROJECT_DETAIL} должен вернуть статус-код"
        " 200"
    )
    response_data = response.json()
    missing_keys = EXPECTED_KEYS - response_data.keys()
    assert not missing_keys, (
        f"В ответе на PATCH-запрос к {PROJECT_DETAIL} не хвататет следующих"
        f" ключей:`{"`, `".join(missing_keys)}`"
    )
    response_data.pop("close_date", None)
    assert response_data == expected_data, (
        f"Структура ответа на PATCH-запрос к {PROJECT_DETAIL} не"
        " соответствует ожидаемому."
    )


@pytest.mark.usefixtures("charity_project_first")
@pytest.mark.parametrize(
    "json_data",
    [
        {"name": ""},
        {"description": ""},
        {"full_amount": ""},
        {"full_amount": "123abc"},
        {"full_amount": 0.5},
        {"full_amount": 0},
        {"full_amount": -1},
    ],
)
def test_update_project_with_invalid_data(superuser_client, json_data):
    response = superuser_client.patch(PROJECT_DETAIL, json=json_data)
    assert response.status_code == 422, (
        f"Убедитесь что при попытке отправить PATCH-запрос к {PROJECT_DETAIL} с"
        "некоректыми данными: постые поля name, description, full_amount"
        "текстовые значения или отрицательные числа или числа с плавоющей"
        "точкой возаращется ответ со статус-кодом 422"
    )


@pytest.mark.usefixtures("charity_project_first")
@pytest.mark.parametrize(
    "json_data",
    [
        {"invested_amount": 500},
        {"fully_invested": True},
        {"close_date": "2023-01-01T00:00:00"},
        {"created_date": "2023-01-01T00:00:00"},
    ],
)
def test_update_project_with_default_filling_fields(
    superuser_client, json_data
):
    response = superuser_client.patch(PROJECT_DETAIL, json=json_data)
    assert response.status_code == 422, (
        f"Убедитесь что при попытке отправить PATCH-запрос к {PROJECT_DETAIL}"
        " с полями не предусмотренными спецификацией API для этого эндпоинта"
        " возвращает статус код 422"
    )


def test_delete_project_with_non_exist_id(
    superuser_client, charity_project_first
):
    url = os.path.join(PROJECT_URL, "100")
    response = superuser_client.delete(url)
    assert (
        response.status_code == 404
    ), f"DELETE-запрос к {url} должен возвращать статус-код 404"


@pytest.mark.usefixtures("charity_project_first", "charity_project_second")
def test_delete_project(superuser_client, charity_project_first):
    response = superuser_client.delete(PROJECT_DETAIL)
    assert (
        response.status_code == 204
    ), f"DELETE-запрос к {PROJECT_DETAIL} должен возвращать статус-код 204"
