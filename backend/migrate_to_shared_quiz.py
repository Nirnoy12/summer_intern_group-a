import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from migrate_helpers import create_shared_quizzes_table, add_shared_quiz_id_column, migrate_existing_quizzes

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in .env")
    exit(1)

engine = create_engine(DATABASE_URL, echo=True)

with engine.connect() as conn:
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    create_shared_quizzes_table(conn, existing_tables)
    add_shared_quiz_id_column(conn, inspector)
    migrate_existing_quizzes(conn)

print("\n✅ All done! You can now restart the backend server.")
