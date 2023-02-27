import sqlite3


db_path = "otto.db"


def get_value(category, id):
    con = sqlite3.connect(db_path)
    key = make_key(category, id)
    result = con.execute(
        "SELECT value FROM thing WHERE key=?",
        (key,)
    )
    row = result.fetchone()
    return row and row.value or None


def set_value(category, id, value):
    con = sqlite3.connect(db_path)
    key = make_key(category, id)
    if get_value(category, id) is not None:
        con.execute(
            "UPDATE thing SET value = ? WHERE key = ?",
            (value, key)
        )
    else:
        con.execute(
            "INSERT INTO thing (key, value) VALUES (?, ?)",
            (key, value)
        )


def make_key(category, id):
    return f"{category}_<!>_{id}"
