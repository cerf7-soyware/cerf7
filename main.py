from cerf7 import create_app
from cerf7.db import *

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
