from app.main import DB


def save_changes(data):
    DB.session.add(data)
    DB.session.commit()
