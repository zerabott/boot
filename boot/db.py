import os
import psycopg2
import datetime
from psycopg2 import Error

# Get the database URL from the environment variable
# This variable is automatically set by Render
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set.")
        
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL:", error)
        return None

def init_db():
    """Initialize database with enhanced schema for PostgreSQL."""
    conn = get_db_connection()
    if conn is None:
        return

    try:
        with conn.cursor() as cursor:
            # Users table with join date tracking
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                questions_asked INTEGER DEFAULT 0,
                comments_posted INTEGER DEFAULT 0,
                blocked INTEGER DEFAULT 0
            )''')
            
            # Posts table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                user_id BIGINT NOT NULL,
                approved BOOLEAN DEFAULT NULL,
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
            )''')
            
            # Comments table with enhanced structure
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                comment_id SERIAL PRIMARY KEY,
                post_id INTEGER NOT NULL,
                user_id BIGINT NOT NULL,
                content TEXT NOT NULL,
                parent_comment_id INTEGER,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
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
                FOREIGN KEY(post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )''')
            
            # Submissions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                submission_id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                message_id BIGINT NOT NULL,
                submission_type TEXT,
                content TEXT,
                category TEXT,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                is_processed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )''')

            # User likes table for tracking likes on posts and comments
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_votes (
                user_id BIGINT NOT NULL,
                post_id INTEGER,
                comment_id INTEGER,
                vote_type TEXT NOT NULL,
                PRIMARY KEY (user_id, post_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
                FOREIGN KEY(comment_id) REFERENCES comments(comment_id) ON DELETE CASCADE
            )''')

            # Admin messaging table for private admin messages
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_messages (
                message_id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                text_content TEXT,
                file_id TEXT,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                is_resolved BOOLEAN DEFAULT FALSE,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )''')

            # Abuse reports table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                report_id SERIAL PRIMARY KEY,
                reporter_user_id BIGINT NOT NULL,
                post_id INTEGER,
                comment_id INTEGER,
                report_reason TEXT,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(reporter_user_id) REFERENCES users(user_id),
                FOREIGN KEY(post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
                FOREIGN KEY(comment_id) REFERENCES comments(comment_id) ON DELETE CASCADE
            )''')

            # Achievement Tracking Table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                achievement_id SERIAL PRIMARY KEY,
                achievement_name TEXT NOT NULL,
                description TEXT,
                achievement_type TEXT NOT NULL,
                criteria_value INTEGER,
                icon TEXT,
                is_hidden BOOLEAN DEFAULT FALSE
            )''')

            # User Achievements Table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                user_achievement_id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                achievement_id INTEGER NOT NULL,
                date_unlocked TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(achievement_id) REFERENCES achievements(achievement_id)
            )''')

            # Post Number Tracking
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_number_counter (
                id SERIAL PRIMARY KEY,
                current_number INTEGER DEFAULT 0
            )''')

            conn.commit()
    except (Exception, Error) as error:
        print("Error while initializing database:", error)
    finally:
        if conn:
            conn.close()


def add_user(user_id, username, first_name, last_name):
    conn = get_db_connection()
    if conn is None:
        return
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO users (user_id, username, first_name, last_name) VALUES (%s, %s, %s, %s)",
                    (user_id, username, first_name, last_name)
                )
                conn.commit()
    except (Exception, Error) as error:
        print("Error adding user:", error)
    finally:
        if conn:
            conn.close()


def get_user(user_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            return cursor.fetchone()
    except (Exception, Error) as error:
        print("Error getting user:", error)
        return None
    finally:
        if conn:
            conn.close()


def save_submission_in_db(user_id, message_id, submission_type, content, category):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO submissions (user_id, message_id, submission_type, content, category) VALUES (%s, %s, %s, %s, %s) RETURNING submission_id",
                (user_id, message_id, submission_type, content, category)
            )
            submission_id = cursor.fetchone()[0]
            conn.commit()
            return submission_id
    except (Exception, Error) as error:
        print("Error saving submission:", error)
        return None
    finally:
        if conn:
            conn.close()

def get_submission_by_message_id(message_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM submissions WHERE message_id = %s", (message_id,))
            return cursor.fetchone()
    except (Exception, Error) as error:
        print("Error getting submission:", error)
        return None
    finally:
        if conn:
            conn.close()

def save_pending_post(user_id, content, category, media_data=None):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            media_fields = ''
            media_values = ''
            media_params = ()
            if media_data:
                media_fields = ', media_type, media_file_id, media_file_unique_id, media_caption, media_file_size, media_mime_type, media_duration, media_width, media_height, media_thumbnail_file_id'
                media_values = ', %s, %s, %s, %s, %s, %s, %s, %s, %s'
                media_params = (
                    media_data.get('media_type'),
                    media_data.get('file_id'),
                    media_data.get('file_unique_id'),
                    media_data.get('caption'),
                    media_data.get('file_size'),
                    media_data.get('mime_type'),
                    media_data.get('duration'),
                    media_data.get('width'),
                    media_data.get('height'),
                    media_data.get('thumbnail_file_id')
                )
                
            cursor.execute(
                f"INSERT INTO posts (user_id, content, category, approved{media_fields}) VALUES (%s, %s, %s, %s{media_values}) RETURNING post_id",
                (user_id, content, category, False) + media_params
            )
            post_id = cursor.fetchone()[0]
            conn.commit()
            return post_id
    except (Exception, Error) as error:
        print("Error saving pending post:", error)
        return None
    finally:
        if conn:
            conn.close()
            
def get_pending_posts():
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT p.post_id, p.content, p.category, p.timestamp, p.media_type, p.media_file_id, p.media_caption,
                       u.username, u.first_name, u.last_name
                FROM posts p
                INNER JOIN users u ON p.user_id = u.user_id
                WHERE p.approved IS NULL
                ORDER BY p.timestamp ASC
            ''')
            return cursor.fetchall()
    except (Exception, Error) as error:
        print("Error getting pending posts:", error)
        return []
    finally:
        if conn:
            conn.close()


def get_post(post_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT p.post_id, p.content, p.approved, p.channel_message_id, p.user_id,
                       p.media_type, p.media_file_id, p.media_caption
                FROM posts p
                WHERE p.post_id = %s
            ''', (post_id,))
            return cursor.fetchone()
    except (Exception, Error) as error:
        print("Error getting post:", error)
        return None
    finally:
        if conn:
            conn.close()

def approve_post(post_id, channel_message_id):
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE posts SET approved = TRUE, channel_message_id = %s WHERE post_id = %s",
                (channel_message_id, post_id)
            )
            conn.commit()
            return True
    except (Exception, Error) as error:
        print("Error approving post:", error)
        return False
    finally:
        if conn:
            conn.close()


def reject_post(post_id):
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE posts SET approved = FALSE WHERE post_id = %s", (post_id,))
            conn.commit()
            return True
    except (Exception, Error) as error:
        print("Error rejecting post:", error)
        return False
    finally:
        if conn:
            conn.close()


def update_user_stats(user_id, stat_type):
    conn = get_db_connection()
    if conn is None:
        return
    
    try:
        with conn.cursor() as cursor:
            if stat_type == 'questions_asked':
                cursor.execute(
                    "UPDATE users SET questions_asked = questions_asked + 1 WHERE user_id = %s",
                    (user_id,)
                )
            elif stat_type == 'comments_posted':
                cursor.execute(
                    "UPDATE users SET comments_posted = comments_posted + 1 WHERE user_id = %s",
                    (user_id,)
                )
            conn.commit()
    except (Exception, Error) as error:
        print("Error updating user stats:", error)
    finally:
        if conn:
            conn.close()


def get_user_stats(user_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT questions_asked, comments_posted, blocked FROM users WHERE user_id = %s",
                (user_id,)
            )
            return cursor.fetchone()
    except (Exception, Error) as error:
        print("Error getting user stats:", error)
        return None
    finally:
        if conn:
            conn.close()


def get_channel_stats():
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM posts WHERE approved = TRUE")
            total_posts = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM comments")
            total_comments = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT user_id) FROM users")
            total_users = cursor.fetchone()[0]
            
            return total_posts, total_comments, total_users
    except (Exception, Error) as error:
        print("Error getting channel stats:", error)
        return None
    finally:
        if conn:
            conn.close()


def add_comment(post_id, user_id, content, parent_comment_id=None, media_data=None):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            media_fields = ''
            media_values = ''
            media_params = ()
            if media_data:
                media_fields = ', media_type, media_file_id, media_file_unique_id, media_caption, media_file_size, media_mime_type, media_duration, media_width, media_height, media_thumbnail_file_id'
                media_values = ', %s, %s, %s, %s, %s, %s, %s, %s, %s'
                media_params = (
                    media_data.get('media_type'),
                    media_data.get('file_id'),
                    media_data.get('file_unique_id'),
                    media_data.get('caption'),
                    media_data.get('file_size'),
                    media_data.get('mime_type'),
                    media_data.get('duration'),
                    media_data.get('width'),
                    media_data.get('height'),
                    media_data.get('thumbnail_file_id')
                )
            
            cursor.execute(
                f"INSERT INTO comments (post_id, user_id, content, parent_comment_id{media_fields}) VALUES (%s, %s, %s, %s{media_values}) RETURNING comment_id",
                (post_id, user_id, content, parent_comment_id) + media_params
            )
            comment_id = cursor.fetchone()[0]
            conn.commit()
            return comment_id
    except (Exception, Error) as error:
        print("Error adding comment:", error)
        return None
    finally:
        if conn:
            conn.close()


def get_comment_count(post_id):
    """Gets the number of comments for a specific post."""
    conn = get_db_connection()
    if conn is None:
        return 0
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM comments WHERE post_id = %s", (post_id,))
            return cursor.fetchone()[0]
    except (Exception, Error) as error:
        print("Error getting comment count:", error)
        return 0
    finally:
        if conn:
            conn.close()

def get_post_and_comments(post_id):
    conn = get_db_connection()
    if conn is None:
        return None, []
    
    try:
        with conn.cursor() as cursor:
            # Get post details
            cursor.execute('''
                SELECT p.post_id, p.content, p.category, p.timestamp, p.likes, p.post_number,
                       p.media_type, p.media_file_id, p.media_caption
                FROM posts p
                WHERE p.post_id = %s
            ''', (post_id,))
            post = cursor.fetchone()
            
            # Get comments for the post, ordered by parent-child hierarchy and timestamp
            cursor.execute('''
                SELECT c.comment_id, c.user_id, c.content, c.timestamp, u.username,
                       c.media_type, c.media_file_id, c.media_caption
                FROM comments c
                INNER JOIN users u ON c.user_id = u.user_id
                WHERE c.post_id = %s
                ORDER BY c.timestamp ASC
            ''', (post_id,))
            comments = cursor.fetchall()
            
            return post, comments
    except (Exception, Error) as error:
        print("Error getting post and comments:", error)
        return None, []
    finally:
        if conn:
            conn.close()

def like_post(user_id, post_id, is_like):
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        with conn.cursor() as cursor:
            vote_type = 'like' if is_like else 'dislike'
            
            # Check if user has already voted on this post
            cursor.execute(
                "SELECT vote_type FROM user_votes WHERE user_id = %s AND post_id = %s",
                (user_id, post_id)
            )
            existing_vote = cursor.fetchone()
            
            if existing_vote:
                if existing_vote[0] == vote_type:
                    # User is trying to do the same action, so undo the vote
                    if vote_type == 'like':
                        cursor.execute("UPDATE posts SET likes = likes - 1 WHERE post_id = %s", (post_id,))
                    else:
                        cursor.execute("UPDATE posts SET likes = likes + 1 WHERE post_id = %s", (post_id,))
                    cursor.execute("DELETE FROM user_votes WHERE user_id = %s AND post_id = %s", (user_id, post_id))
                else:
                    # User is switching their vote
                    if vote_type == 'like':
                        cursor.execute("UPDATE posts SET likes = likes + 2 WHERE post_id = %s", (post_id,))
                    else:
                        cursor.execute("UPDATE posts SET likes = likes - 2 WHERE post_id = %s", (post_id,))
                    cursor.execute("UPDATE user_votes SET vote_type = %s WHERE user_id = %s AND post_id = %s", (vote_type, user_id, post_id))
            else:
                # New vote
                if vote_type == 'like':
                    cursor.execute("UPDATE posts SET likes = likes + 1 WHERE post_id = %s", (post_id,))
                else:
                    cursor.execute("UPDATE posts SET likes = likes - 1 WHERE post_id = %s", (post_id,))
                cursor.execute(
                    "INSERT INTO user_votes (user_id, post_id, vote_type) VALUES (%s, %s, %s)",
                    (user_id, post_id, vote_type)
                )

            conn.commit()
            return True
    except (Exception, Error) as error:
        print("Error liking/disliking post:", error)
        return False
    finally:
        if conn:
            conn.close()


def save_report(reporter_user_id, content_id, content_type, reason):
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        with conn.cursor() as cursor:
            if content_type == 'post':
                cursor.execute(
                    "INSERT INTO reports (reporter_user_id, post_id, report_reason) VALUES (%s, %s, %s)",
                    (reporter_user_id, content_id, reason)
                )
            elif content_type == 'comment':
                cursor.execute(
                    "INSERT INTO reports (reporter_user_id, comment_id, report_reason) VALUES (%s, %s, %s)",
                    (reporter_user_id, content_id, reason)
                )
            conn.commit()
            return True
    except (Exception, Error) as error:
        print("Error saving report:", error)
        return False
    finally:
        if conn:
            conn.close()


def get_reports(limit=10):
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT r.report_id, u.username, u.user_id, r.post_id, r.comment_id, r.report_reason, r.timestamp
                FROM reports r
                INNER JOIN users u ON r.reporter_user_id = u.user_id
                ORDER BY r.timestamp DESC
                LIMIT %s
            ''', (limit,))
            return cursor.fetchall()
    except (Exception, Error) as error:
        print("Error getting reports:", error)
        return []
    finally:
        if conn:
            conn.close()


def get_post_reports(post_id):
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT reporter_user_id, report_reason FROM reports WHERE post_id = %s", (post_id,))
            return cursor.fetchall()
    except (Exception, Error) as error:
        print("Error getting post reports:", error)
        return []
    finally:
        if conn:
            conn.close()


def get_comment_reports(comment_id):
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT reporter_user_id, report_reason FROM reports WHERE comment_id = %s", (comment_id,))
            return cursor.fetchall()
    except (Exception, Error) as error:
        print("Error getting comment reports:", error)
        return []
    finally:
        if conn:
            conn.close()


def clear_reports_for_content(content_id, content_type):
    conn = get_db_connection()
    if conn is None:
        return
    
    try:
        with conn.cursor() as cursor:
            if content_type == 'post':
                cursor.execute("DELETE FROM reports WHERE post_id = %s", (content_id,))
            elif content_type == 'comment':
                cursor.execute("DELETE FROM reports WHERE comment_id = %s", (content_id,))
            conn.commit()
    except (Exception, Error) as error:
        print("Error clearing reports:", error)
    finally:
        if conn:
            conn.close()


def add_post_number(post_id):
    conn = get_db_connection()
    if conn is None:
        return
    
    try:
        with conn.cursor() as cursor:
            # Check if a counter exists
            cursor.execute("SELECT current_number FROM post_number_counter FOR UPDATE")
            counter_row = cursor.fetchone()
            
            if not counter_row:
                # If no counter exists, create one and set it to 1
                cursor.execute("INSERT INTO post_number_counter (current_number) VALUES (1)")
                new_post_number = 1
            else:
                current_number = counter_row[0]
                new_post_number = current_number + 1
                cursor.execute("UPDATE post_number_counter SET current_number = %s", (new_post_number,))
            
            # Update the post with the new number
            cursor.execute("UPDATE posts SET post_number = %s WHERE post_id = %s", (new_post_number, post_id))
            
            conn.commit()
            return new_post_number
    except (Exception, Error) as error:
        print("Error adding post number:", error)
        return None
    finally:
        if conn:
            conn.close()


def add_user_achievement(user_id, achievement_name):
    conn = get_db_connection()
    if conn is None:
        return
    
    try:
        with conn.cursor() as cursor:
            # Check if the user already has the achievement
            cursor.execute('''
                SELECT ua.user_achievement_id
                FROM user_achievements ua
                JOIN achievements a ON ua.achievement_id = a.achievement_id
                WHERE ua.user_id = %s AND a.achievement_name = %s
            ''', (user_id, achievement_name))
            if cursor.fetchone():
                return
            
            # Get the achievement ID
            cursor.execute("SELECT achievement_id FROM achievements WHERE achievement_name = %s", (achievement_name,))
            achievement_id = cursor.fetchone()
            
            if achievement_id:
                cursor.execute(
                    "INSERT INTO user_achievements (user_id, achievement_id) VALUES (%s, %s)",
                    (user_id, achievement_id[0])
                )
                conn.commit()
    except (Exception, Error) as error:
        print("Error adding user achievement:", error)
    finally:
        if conn:
            conn.close()


def get_user_achievements(user_id):
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT a.achievement_name, a.description, a.icon
                FROM user_achievements ua
                JOIN achievements a ON ua.achievement_id = a.achievement_id
                WHERE ua.user_id = %s
            ''', (user_id,))
            return cursor.fetchall()
    except (Exception, Error) as error:
        print("Error getting user achievements:", error)
        return []
    finally:
        if conn:
            conn.close()


def get_all_achievements():
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT achievement_name, description, icon, is_hidden FROM achievements")
            return cursor.fetchall()
    except (Exception, Error) as error:
        print("Error getting all achievements:", error)
        return []
    finally:
        if conn:
            conn.close()

def get_post_media_details(post_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT media_type, media_file_id, media_caption FROM posts WHERE post_id = %s",
                (post_id,)
            )
            return cursor.fetchone()
    except (Exception, Error) as error:
        print("Error getting post media details:", error)
        return None
    finally:
        if conn:
            conn.close()


def get_all_channel_posts(limit=10, offset=0):
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT post_id, content, category, timestamp, likes, post_number, channel_message_id,
                       media_type, media_file_id, media_caption
                FROM posts
                WHERE approved = TRUE
                ORDER BY post_number DESC
                LIMIT %s OFFSET %s
            ''', (limit, offset))
            return cursor.fetchall()
    except (Exception, Error) as error:
        print("Error getting channel posts:", error)
        return []
    finally:
        if conn:
            conn.close()

def count_channel_posts():
    conn = get_db_connection()
    if conn is None:
        return 0
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM posts WHERE approved = TRUE")
            return cursor.fetchone()[0]
    except (Exception, Error) as error:
        print("Error counting channel posts:", error)
        return 0
    finally:
        if conn:
            conn.close()


def get_post_by_post_number(post_number):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM posts WHERE post_number = %s", (post_number,))
            return cursor.fetchone()
    except (Exception, Error) as error:
        print("Error getting post by number:", error)
        return None
    finally:
        if conn:
            conn.close()


def get_user_comments(user_id, limit=10):
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT c.comment_id, c.content, c.timestamp, c.media_type, c.media_file_id, c.media_caption, p.post_number
                FROM comments c
                INNER JOIN posts p ON c.post_id = p.post_id
                WHERE c.user_id = %s
                ORDER BY c.timestamp DESC
                LIMIT %s
            ''', (user_id, limit))
            return cursor.fetchall()
    except (Exception, Error) as error:
        print("Error getting user comments:", error)
        return []
    finally:
        if conn:
            conn.close()


def get_post_author_id(post_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM posts WHERE post_id = %s", (post_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except (Exception, Error) as error:
        print("Error getting post author ID:", error)
        return None
    finally:
        if conn:
            conn.close()

def get_comment_author_id(comment_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM comments WHERE comment_id = %s", (comment_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except (Exception, Error) as error:
        print("Error getting comment author ID:", error)
        return None
    finally:
        if conn:
            conn.close()


def delete_post_completely(post_id):
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM posts WHERE post_id = %s", (post_id,))
            conn.commit()
            return True
    except (Exception, Error) as error:
        print("Error deleting post completely:", error)
        return False
    finally:
        if conn:
            conn.close()


def delete_comment_completely(comment_id):
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM comments WHERE comment_id = %s", (comment_id,))
            conn.commit()
            return True
    except (Exception, Error) as error:
        print("Error deleting comment completely:", error)
        return False
    finally:
        if conn:
            conn.close()


def get_post_details_for_deletion(post_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT channel_message_id, post_number FROM posts WHERE post_id = %s", (post_id,))
            return cursor.fetchone()
    except (Exception, Error) as error:
        print("Error getting post details for deletion:", error)
        return None
    finally:
        if conn:
            conn.close()

def get_comment_details_for_deletion(comment_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT post_id, channel_message_id FROM comments WHERE comment_id = %s", (comment_id,))
            return cursor.fetchone()
    except (Exception, Error) as error:
        print("Error getting comment details for deletion:", error)
        return None
    finally:
        if conn:
            conn.close()


def get_recent_posts(limit=10):
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT post_id, content, timestamp, post_number, channel_message_id, likes,
                       media_type, media_file_id, media_caption
                FROM posts
                WHERE approved = TRUE
                ORDER BY timestamp DESC
                LIMIT %s
            ''', (limit,))
            return cursor.fetchall()
    except (Exception, Error) as error:
        print("Error getting recent posts:", error)
        return []
    finally:
        if conn:
            conn.close()

def get_trending_posts(limit=10):
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT post_id, content, timestamp, post_number, channel_message_id, likes,
                       media_type, media_file_id, media_caption
                FROM posts
                WHERE approved = TRUE
                ORDER BY likes DESC, timestamp DESC
                LIMIT %s
            ''', (limit,))
            return cursor.fetchall()
    except (Exception, Error) as error:
        print("Error getting trending posts:", error)
        return []
    finally:
        if conn:
            conn.close()


def get_leaderboard(limit=10):
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT u.first_name, u.last_name, u.username, u.questions_asked, u.comments_posted
                FROM users u
                ORDER BY u.questions_asked DESC
                LIMIT %s
            ''', (limit,))
            return cursor.fetchall()
    except (Exception, Error) as error:
        print("Error getting leaderboard:", error)
        return []
    finally:
        if conn:
            conn.close()


def get_user_posts(user_id, limit=10):
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT p.post_id, p.content, p.category, p.timestamp, p.approved,
                       COUNT(c.comment_id) as comment_count, p.post_number,
                       p.media_type, p.media_file_id, p.media_file_unique_id, p.media_caption,
                       p.media_file_size, p.media_mime_type, p.media_duration, 
                       p.media_width, p.media_height, p.media_thumbnail_file_id
                FROM posts p
                LEFT JOIN comments c ON p.post_id = c.post_id
                WHERE p.user_id = %s
                GROUP BY p.post_id, p.content, p.category, p.timestamp, p.approved, p.post_number,
                         p.media_type, p.media_file_id, p.media_file_unique_id, p.media_caption,
                         p.media_file_size, p.media_mime_type, p.media_duration, 
                         p.media_width, p.media_height, p.media_thumbnail_file_id
                ORDER BY p.timestamp DESC
                LIMIT %s
            ''', (user_id, limit))
            return cursor.fetchall()
    except (Exception, Error) as error:
        print("Error getting user posts:", error)
        return []
    finally:
        if conn:
            conn.close()
            
def get_post_author_id(post_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM posts WHERE post_id = %s", (post_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except (Exception, Error) as error:
        print("Error getting post author ID:", error)
        return None
    finally:
        if conn:
            conn.close()
