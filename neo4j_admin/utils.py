def get_all_db_labels(session):
    return list(session.run("call db.labels();"))
