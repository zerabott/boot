import os
import psycopg2
from psycopg2 import Error
from urllib.parse import urlparse

# Get the PostgreSQL database URL from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    Returns the connection object or None if the connection fails.
    """
    try:
        url = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            host=url.hostname,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            port=url.port,
            sslmode='require'
        )
        return conn
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def init_db():
    """Initialize database with enhanced schema for PostgreSQL."""
    conn = get_db_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    try:
        # Users table with join date tracking
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            join_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            questions_asked INTEGER DEFAULT 0,
            comments_posted INTEGER DEFAULT 0,
            blocked INTEGER DEFAULT 0
        )
        """)

        # Posts table with media fields
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            post_id SERIAL PRIMARY KEY,
            content TEXT,
            category TEXT NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            user_id BIGINT NOT NULL,
            approved INTEGER DEFAULT NULL,
            channel_message_id BIGINT,
            flagged INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            post_number INTEGER DEFAULT NULL,
            media_type TEXT,
            media_file_id TEXT,
            media_file_unique_id TEXT,
            media_caption TEXT,
            media_file_size INTEGER,
            media_mime_type TEXT,
            media_duration INTEGER,
            media_width INTEGER,
            media_height INTEGER,
            media_thumbnail_file_id TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)

        # Comments table with enhanced structure
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            comment_id SERIAL PRIMARY KEY,
            post_id INTEGER NOT NULL,
            user_id BIGINT NOT NULL,
            content TEXT NOT NULL,
            parent_comment_id INTEGER,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(post_id) REFERENCES posts(post_id),
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)
        
        # Reports table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            report_id SERIAL PRIMARY KEY,
            target_type TEXT NOT NULL,
            target_id INTEGER NOT NULL,
            reporter_id BIGINT NOT NULL,
            reason TEXT,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Reactions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reactions (
            reaction_id SERIAL PRIMARY KEY,
            target_type TEXT NOT NULL,
            target_id INTEGER NOT NULL,
            user_id BIGINT NOT NULL,
            reaction_type TEXT NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (target_type, target_id, user_id)
        )
        """)
        
        # Admin table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            admin_id BIGINT PRIMARY KEY,
            username TEXT,
            level INTEGER DEFAULT 1
        )
        """)
        
        # Admin Actions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_actions (
                id SERIAL PRIMARY KEY,
                admin_user_id BIGINT NOT NULL,
                action_type TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id INTEGER NOT NULL,
                details TEXT,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
    except Exception as e:
        print(f"Error during database initialization: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def get_user(user_id: int):
    """
    Fetches a user from the database.
    Returns a dictionary of user data or None if not found.
    """
    conn = get_db_connection()
    if conn is None:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, user_data))
        return None
    except Error as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def add_user(user_id: int, username: str, first_name: str, last_name: str):
    """Adds a new user to the database."""
    conn = get_db_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (user_id, username, first_name, last_name) VALUES (%s, %s, %s, %s) ON CONFLICT (user_id) DO NOTHING",
                       (user_id, username, first_name, last_name))
        conn.commit()
    except Error as e:
        print(f"Error adding user: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def is_blocked_user(user_id: int) -> bool:
    """Checks if a user is blocked."""
    conn = get_db_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT blocked FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if result and result[0] == 1:
            return True
        return False
    except Error as e:
        print(f"Error checking if user is blocked: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_post_author_id(post_id: int) -> int:
    """
    Gets the user ID of the post's author.
    """
    conn = get_db_connection()
    if conn is None:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM posts WHERE post_id = %s", (post_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    except Error as e:
        print(f"Error getting post author: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_comment_author_id(comment_id: int) -> int:
    """
    Gets the user ID of the comment's author.
    """
    conn = get_db_connection()
    if conn is None:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM comments WHERE comment_id = %s", (comment_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    except Error as e:
        print(f"Error getting comment author: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
