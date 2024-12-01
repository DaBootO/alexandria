import pytest

TEST_TABLE = {
    "cols": {"name": "str"},
    "tags": ["testTag"]
}
TEST_UUID = ""

@pytest.mark.asyncio
async def test_read_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Server is Running"}

@pytest.mark.asyncio
async def test_create_experiment(client, db_session):
    global TEST_UUID
    response = await client.post(
        "/createExperiment/",
        json=TEST_TABLE,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    assert "uuid" in response.json()
    TEST_UUID = response.json()['uuid']
    assert len(TEST_UUID) == 36

@pytest.mark.asyncio
async def test_delete_experiment(client, db_session):
    global TEST_UUID
    assert TEST_UUID, "TEST_UUID is not set. Ensure test_create_experiment runs first."
    response = await client.post(f"/deleteExperiment/{TEST_UUID}")
    print(response.headers)
    print(response.url)
    assert response.status_code == 200
    assert TEST_UUID == response.json()['deleted_uuid']
