from typing import Dict, Any

_FAKE_DB: Dict[str, list[dict[str, Any]]] = {"users": [], "items": []}

class FakeDB:
    def __init__(self) -> None:
        self.users = _FAKE_DB["users"]
        self.items = _FAKE_DB["items"]

    def add_user(self, user: dict) -> dict:
        user["id"] = len(self.users) + 1
        self.users.append(user)
        return user

    def list_users(self) -> list[dict]:
        return self.users

    def add_item(self, item: dict) -> dict:
        item["id"] = len(self.items) + 1
        self.items.append(item)
        return item

    def list_items(self) -> list[dict]:
        return self.items

def get_db() -> FakeDB:
    return FakeDB()
