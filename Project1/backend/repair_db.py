import os
from app import app, db

DB_PATH = 'forum.db'

if __name__ == '__main__':
    if os.path.exists(DB_PATH):
        print(f"Removing existing database: {DB_PATH}")
        os.remove(DB_PATH)

    with app.app_context():
        db.create_all()
        print('Database schema created.')

        # Optional: initialize sample data
        try:
            from init_data import init_data
            init_data()
            print('Sample data initialized.')
        except Exception as e:
            print('Failed to initialize data:', e)
