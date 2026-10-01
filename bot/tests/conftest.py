import sys
import types


class FakeDatabase:
    pass


fake_db_main = types.ModuleType("functions.db_main")
fake_db_main.Database = FakeDatabase
sys.modules.setdefault("functions.db_main", fake_db_main)
