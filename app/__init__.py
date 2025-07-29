from app.arango_db_helper import ArangoDBHelper  # если ArangoDBHelper в другом файле

# или просто from app.arango_db_helper import ArangoDBHelper — если всё в одном

_arango_helper_instance = None
_arango_test_helper_instance = None


def get_arango_db_helper(is_test_mode: bool = False) -> ArangoDBHelper:
    global _arango_helper_instance, _arango_test_helper_instance

    if is_test_mode:
        if _arango_test_helper_instance is None:
            print("[INIT] Creating test ArangoDBHelper instance")
            _arango_test_helper_instance = ArangoDBHelper(is_test_mode=True)
        return _arango_test_helper_instance
    else:
        if _arango_helper_instance is None:
            print("[INIT] Creating production ArangoDBHelper instance")
            _arango_helper_instance = ArangoDBHelper(is_test_mode=False)
        return _arango_helper_instance
