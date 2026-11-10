import logging
from datetime import datetime


def add(client, **kw):
    kw.setdefault("title", "Task")
    r = client.post("/api/todos", json=kw)
    assert r.status_code == 201, r.text
    return r.json()


def test_create_defaults_and_utc(client):
    t = add(client, title="  Buy milk  ")
    assert t["title"] == "Buy milk"
    assert t["priority"] == "medium"
    assert t["category"] == "other"
    assert t["completed"] is False and t["archived"] is False
    assert t["due_date"] is None
    assert t["created_at"].endswith("Z")
    datetime.fromisoformat(t["created_at"].replace("Z", "+00:00"))


def test_create_validation(client):
    for body in [
        {"title": "   "},
        {"title": "x" * 201},
        {},
        {"title": "a", "priority": "urgent"},
        {"title": "a", "category": "fun"},
        {"title": "a", "due_date": "11/09/2026"},
        {"title": "a", "due_date": "2026-02-30"},
        {"title": "a", "due_date": "20261109"},
    ]:
        assert client.post("/api/todos", json=body).status_code == 422, body


def test_list_excludes_archived_by_default(client):
    a = add(client, title="a")
    b = add(client, title="b")
    client.patch(f"/api/todos/{a['id']}", json={"archived": True})
    assert [t["id"] for t in client.get("/api/todos").json()] == [b["id"]]
    both = client.get("/api/todos", params={"include_archived": "true"}).json()
    assert [t["id"] for t in both] == [a["id"], b["id"]]
    assert both[0]["archived"] is True


def test_list_empty(client):
    assert client.get("/api/todos").json() == []


def test_search_case_insensitive(client):
    add(client, title="Buy Milk")
    add(client, title="Walk dog")
    r = client.get("/api/todos", params={"q": "MILK"}).json()
    assert [t["title"] for t in r] == ["Buy Milk"]
    assert client.get("/api/todos", params={"q": "zzz"}).json() == []


def test_complete_and_undo_keeps_other_fields(client):
    t = add(client, title="a", due_date="2026-11-01", category="work", priority="high")
    r = client.patch(f"/api/todos/{t['id']}", json={"completed": True}).json()
    assert r["completed"] is True and r["archived"] is False
    assert {k: r[k] for k in ("title", "due_date", "category", "priority")} == {
        "title": "a",
        "due_date": "2026-11-01",
        "category": "work",
        "priority": "high",
    }
    r = client.patch(f"/api/todos/{t['id']}", json={"completed": False}).json()
    assert r["completed"] is False


def test_archive_restore_round_trip(client):
    t = add(client)
    client.patch(f"/api/todos/{t['id']}", json={"completed": True})
    client.patch(f"/api/todos/{t['id']}", json={"archived": True})
    r = client.patch(f"/api/todos/{t['id']}", json={"archived": False}).json()
    assert r["archived"] is False and r["completed"] is True
    assert len(client.get("/api/todos").json()) == 1


def test_patch_errors(client):
    t = add(client)
    assert client.patch("/api/todos/999", json={"completed": True}).status_code == 404
    assert client.patch(f"/api/todos/{t['id']}", json={"title": "new"}).status_code == 422
    assert client.patch(f"/api/todos/{t['id']}", json={}).status_code == 422
    assert client.patch(f"/api/todos/{t['id']}", json={"completed": "yes"}).status_code == 422


def test_no_delete(client):
    t = add(client)
    assert client.delete(f"/api/todos/{t['id']}").status_code == 405
    assert client.delete("/api/todos/1").status_code == 405


def test_overdue(client):
    past = add(client, title="past", due_date="2026-11-08")
    older = add(client, title="older", due_date="2026-11-01")
    add(client, title="today", due_date="2026-11-09")
    add(client, title="future", due_date="2026-11-20")
    add(client, title="nodate")
    done = add(client, title="done", due_date="2026-11-01")
    arch = add(client, title="arch", due_date="2026-11-01")
    client.patch(f"/api/todos/{done['id']}", json={"completed": True})
    client.patch(f"/api/todos/{arch['id']}", json={"archived": True})
    r = client.get("/api/todos/overdue").json()
    assert [t["id"] for t in r] == [older["id"], past["id"]]  # due_date asc
    r = client.get("/api/todos/overdue", params={"q": "PAST"}).json()
    assert [t["id"] for t in r] == [past["id"]]


def test_overdue_empty(client):
    assert client.get("/api/todos/overdue").json() == []


def test_titles_never_logged(client, caplog):
    caplog.set_level(logging.DEBUG)
    secret = "SECRET-TITLE-123"
    t = add(client, title=secret, due_date="2026-11-01")
    client.get("/api/todos", params={"q": secret})
    client.get("/api/todos/overdue", params={"q": secret})
    client.patch(f"/api/todos/{t['id']}", json={"completed": True})
    client.patch(f"/api/todos/{t['id']}", json={"archived": True})
    # The httpx logger is the test client's own request log, not the server's.
    server_logs = "\n".join(
        r.getMessage() for r in caplog.records if not r.name.startswith("httpx")
    )
    assert "todo id=" in server_logs  # sanity: server did log something
    assert secret not in server_logs
