import uuid
from sqlalchemy import text

def create_shared_quizzes_table(conn, existing_tables):
    if "shared_quizzes" not in existing_tables:
        print("Creating 'shared_quizzes' table...")
        conn.execute(text("""
            CREATE TABLE shared_quizzes (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                yt_playlist_id VARCHAR NOT NULL,
                sequence_order INTEGER NOT NULL,
                title VARCHAR NOT NULL,
                status VARCHAR NOT NULL DEFAULT 'pending',
                video_yt_ids JSON DEFAULT '[]',
                questions_per_attempt INTEGER NOT NULL DEFAULT 10,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.execute(text("CREATE INDEX idx_shared_quizzes_yt_playlist_id ON shared_quizzes (yt_playlist_id)"))
        conn.commit()
        print("  ✅ Created shared_quizzes table")
    else:
        print("  ℹ shared_quizzes table already exists — skipping create")

def add_shared_quiz_id_column(conn, inspector):
    quiz_cols = [c["name"] for c in inspector.get_columns("quizzes")]
    if "shared_quiz_id" not in quiz_cols:
        print("Adding 'shared_quiz_id' column to 'quizzes'...")
        conn.execute(text("ALTER TABLE quizzes ADD COLUMN shared_quiz_id UUID REFERENCES shared_quizzes(id)"))
        conn.commit()
        print("  ✅ Added shared_quiz_id column")
    else:
        print("  ℹ shared_quiz_id already exists on quizzes — skipping")

def migrate_existing_quizzes(conn):
    print("Migrating existing Quiz rows to SharedQuiz...")
    result = conn.execute(text("""
        SELECT q.id, q.title, q.status, q.questions_per_attempt, q.video_yt_ids,
               q.sequence_order, p.yt_playlist_id
        FROM quizzes q
        JOIN playlists p ON q.playlist_id = p.id
        WHERE q.shared_quiz_id IS NULL
        ORDER BY q.created_at, q.sequence_order
    """))
    quizzes_to_migrate = result.fetchall()
    print(f"  Found {len(quizzes_to_migrate)} quiz rows to migrate")

    for row in quizzes_to_migrate:
        quiz_id, title, status, qpa, video_yt_ids, seq_order, yt_playlist_id = row
        existing = conn.execute(text("""
            SELECT id FROM shared_quizzes
            WHERE yt_playlist_id = :yt_pid AND sequence_order = :seq
        """), {"yt_pid": yt_playlist_id, "seq": seq_order}).fetchone()

        if existing:
            shared_quiz_id = existing[0]
            print(f"  Reusing existing SharedQuiz {shared_quiz_id} for Quiz {quiz_id}")
        else:
            shared_quiz_id = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO shared_quizzes (id, yt_playlist_id, sequence_order, title, status, video_yt_ids, questions_per_attempt)
                VALUES (:id, :yt_pid, :seq, :title, :status, :vids::json, :qpa)
            """), {
                "id": shared_quiz_id,
                "yt_pid": yt_playlist_id,
                "seq": seq_order,
                "title": title,
                "status": status,
                "vids": video_yt_ids if isinstance(video_yt_ids, str) else "[]",
                "qpa": qpa or 10,
            })
            print(f"  Created SharedQuiz {shared_quiz_id} for Quiz {quiz_id}")

            q_result = conn.execute(text("""
                UPDATE questions SET quiz_id = :sq_id WHERE quiz_id = :qz_id
            """), {"sq_id": shared_quiz_id, "qz_id": str(quiz_id)})
            print(f"    Moved {q_result.rowcount} questions to SharedQuiz")

        conn.execute(text("""
            UPDATE quizzes SET shared_quiz_id = :sq_id WHERE id = :qz_id
        """), {"sq_id": shared_quiz_id, "qz_id": str(quiz_id)})
    conn.commit()
    print("  ✅ Migration complete")
