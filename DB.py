# # import sqlite3
# # import json  # Needed for the raw_json column
# #
# #
# # class RedditDatabase:
# #     def __init__(self, db_name='reddit_app.db'):
# #         self.db_name = db_name
# #         self.create_tables()
# #
# #     def get_connection(self):
# #         conn = sqlite3.connect(self.db_name)
# #         conn.row_factory = sqlite3.Row
# #         return conn
# #
# #     # --- 1. SETUP (Updated with your new Schema) ---
# #     def create_tables(self):
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
# #
# #         # Table 1: Users (Added created_at)
# #         cursor.execute('''
# #                        CREATE TABLE IF NOT EXISTS app_users
# #                        (
# #                            uid
# #                            INTEGER
# #                            PRIMARY
# #                            KEY
# #                            AUTOINCREMENT,
# #                            username
# #                            TEXT
# #                            UNIQUE
# #                            NOT
# #                            NULL,
# #                            password_hash
# #                            TEXT
# #                            NOT
# #                            NULL,
# #                            created_at
# #                            DATETIME
# #                            DEFAULT
# #                            CURRENT_TIMESTAMP
# #                        )
# #                        ''')
# #
# #         # Table 2: Search History (Unchanged)
# #         cursor.execute('''
# #                        CREATE TABLE IF NOT EXISTS search_history
# #                        (
# #                            search_id
# #                            INTEGER
# #                            PRIMARY
# #                            KEY
# #                            AUTOINCREMENT,
# #                            uid
# #                            INTEGER,
# #                            query_text
# #                            TEXT
# #                            NOT
# #                            NULL,
# #                            search_type
# #                            TEXT
# #                            NOT
# #                            NULL,
# #                            created_at
# #                            DATETIME
# #                            DEFAULT
# #                            CURRENT_TIMESTAMP,
# #                            FOREIGN
# #                            KEY
# #                        (
# #                            uid
# #                        ) REFERENCES app_users
# #                        (
# #                            uid
# #                        ) ON DELETE CASCADE
# #                            )
# #                        ''')
# #
# #         # Table 3: Analysis Results (HEAVILY UPGRADED)
# #         cursor.execute('''
# #                        CREATE TABLE IF NOT EXISTS analysis_results
# #                        (
# #                            id
# #                            INTEGER
# #                            PRIMARY
# #                            KEY
# #                            AUTOINCREMENT,
# #                            search_id
# #                            INTEGER,
# #                            post_link
# #                            TEXT,
# #                            content
# #                            TEXT,
# #                            sentiment
# #                            TEXT, -- 'positive', 'negative'
# #                            primary_emotion
# #                            TEXT, -- 'joy', 'anger'
# #                            confidence
# #                            REAL,
# #                            raw_json
# #                            TEXT, -- Full dictionary string
# #                            FOREIGN
# #                            KEY
# #                        (
# #                            search_id
# #                        ) REFERENCES search_history
# #                        (
# #                            search_id
# #                        ) ON DELETE CASCADE
# #                            )
# #                        ''')
# #
# #         # 4. Indexes (For Speed)
# #         cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_history ON search_history(uid, created_at DESC)')
# #         cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_results ON analysis_results(search_id)')
# #
# #         conn.commit()
# #         conn.close()
# #
# #     # --- 2. INSERT METHODS ---
# #
# #     def add_user(self, username, password_hash):
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
# #         try:
# #             cursor.execute("INSERT INTO app_users (username, password_hash) VALUES (?, ?)",
# #                            (username, password_hash))
# #             conn.commit()
# #             return cursor.lastrowid
# #         except sqlite3.IntegrityError:
# #             cursor.execute("SELECT uid FROM app_users WHERE username = ?", (username,))
# #             return cursor.fetchone()['uid']
# #         finally:
# #             conn.close()
# #
# #     def verify_login(self, username, password):
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
# #         cursor.execute("SELECT uid, password_hash FROM app_users WHERE username = ?", (username,))
# #         user_data = cursor.fetchone()
# #         conn.close()
# #
# #         if user_data and user_data['password_hash'] == password:
# #             return user_data['uid']
# #         return None
# #
# #     def add_search_event(self, uid, query_text, search_type):
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
# #         cursor.execute("INSERT INTO search_history (uid, query_text, search_type) VALUES (?, ?, ?)",
# #                        (uid, query_text, search_type))
# #         search_id = cursor.lastrowid
# #         conn.commit()
# #         conn.close()
# #         return search_id
# #
# #     # --- UPDATED: HANDLES NEW COLUMNS ---
# #     def add_analysis_results(self, search_id, results_list):
# #         """
# #         Expects results_list to contain dictionaries or tuples with:
# #         (link, content, sentiment, primary_emotion, confidence, raw_json_dict)
# #         """
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
# #
# #         data_to_insert = []
# #         for row in results_list:
# #             # Check if row is a tuple or object and unpack accordingly
# #             link = row['link']
# #             content = row['text']
# #             sentiment = row['sentiment']  # e.g. "Positive"
# #             emotion = row['primary_emotion']  # e.g. "Joy"
# #             conf = row['confidence']  # e.g. 0.95
# #
# #             # Convert the raw dictionary to a JSON string for storage
# #             raw_data = json.dumps(row['raw_dict'])
# #
# #             data_to_insert.append((search_id, link, content, sentiment, emotion, conf, raw_data))
# #
# #         cursor.executemany('''
# #                            INSERT INTO analysis_results
# #                            (search_id, post_link, content, sentiment, primary_emotion, confidence, raw_json)
# #                            VALUES (?, ?, ?, ?, ?, ?, ?)
# #                            ''', data_to_insert)
# #
# #         conn.commit()
# #         conn.close()
# #         print(f"✅ Saved {len(data_to_insert)} enhanced results to DB.")
# #
# #     # --- 3. GETTER METHODS (Standard) ---
# #     def get_user_by_username(self, username):
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
# #         cursor.execute("SELECT * FROM app_users WHERE username = ?", (username,))
# #         return cursor.fetchone()
# #
# #     def get_searches_by_user_id(self, uid):
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
# #         cursor.execute("SELECT * FROM search_history WHERE uid = ? ORDER BY created_at DESC", (uid,))
# #         return cursor.fetchall()
#
#
# import sqlite3
# import json
#
#
# class RedditDatabase:
#     def __init__(self, db_name='reddit_pulse.db'):
#         self.db_name = db_name
#         self.create_tables()
#
#     def get_connection(self):
#         conn = sqlite3.connect(self.db_name)
#         conn.row_factory = sqlite3.Row
#         return conn
#
#     def create_tables(self):
#         conn = self.get_connection()
#         cursor = conn.cursor()
#
#         # 1. Users Table (Now with Email - NOT UNIQUE)
#         cursor.execute('''
#                        CREATE TABLE IF NOT EXISTS app_users
#                        (
#                            uid
#                            INTEGER
#                            PRIMARY
#                            KEY
#                            AUTOINCREMENT,
#                            username
#                            TEXT
#                            UNIQUE
#                            NOT
#                            NULL,
#                            email
#                            TEXT
#                            NOT
#                            NULL,
#                            password
#                            TEXT
#                            NOT
#                            NULL,
#                            created_at
#                            DATETIME
#                            DEFAULT
#                            CURRENT_TIMESTAMP
#                        )
#                        ''')
#
#         # 2. Search History (Handles Subreddit, Topic, User, AND Statements)
#         # Table 2: Search History (Added api_response column)
#         cursor.execute('''
#                        CREATE TABLE IF NOT EXISTS search_history
#                        (
#                            search_id
#                            INTEGER
#                            PRIMARY
#                            KEY
#                            AUTOINCREMENT,
#                            uid
#                            INTEGER,
#                            query_text
#                            TEXT
#                            NOT
#                            NULL,
#                            search_type
#                            TEXT
#                            NOT
#                            NULL,
#                            api_response
#                            TEXT, -- <--- NEW COLUMN
#                            created_at
#                            DATETIME
#                            DEFAULT
#                            CURRENT_TIMESTAMP,
#                            FOREIGN
#                            KEY
#                        (
#                            uid
#                        ) REFERENCES app_users
#                        (
#                            uid
#                        ) ON DELETE CASCADE
#                            )
#                        ''')
#
#         # 3. Analysis Results (Stores details for searches AND single statements)
#         cursor.execute('''
#                        CREATE TABLE IF NOT EXISTS analysis_results
#                        (
#                            id
#                            INTEGER
#                            PRIMARY
#                            KEY
#                            AUTOINCREMENT,
#                            search_id
#                            INTEGER,
#                            post_link
#                            TEXT,
#                            content
#                            TEXT,
#                            sentiment
#                            TEXT,
#                            primary_emotion
#                            TEXT,
#                            confidence
#                            REAL,
#                            raw_json
#                            TEXT,
#                            FOREIGN
#                            KEY
#                        (
#                            search_id
#                        ) REFERENCES search_history
#                        (
#                            search_id
#                        ) ON DELETE CASCADE
#                            )
#                        ''')
#
#         # 4. NEW TABLE: Vibe Check History
#         # 4. UPDATED: Global Vibe Cache (No User ID, Subreddit is Unique)
#         cursor.execute('''
#                        CREATE TABLE IF NOT EXISTS subreddit_vibes
#                        (
#                            subreddit
#                            TEXT
#                            PRIMARY
#                            KEY,
#                            overall_sentiment
#                            TEXT,
#                            overall_emotion
#                            TEXT,
#                            last_updated
#                            DATETIME
#                            DEFAULT
#                            CURRENT_TIMESTAMP
#                        )
#                        ''')
#
#         conn.commit()
#         conn.close()
#
#     # --- USER METHODS ---
#     def add_user(self, username, email, password_hash):
#         conn = self.get_connection()
#         cursor = conn.cursor()
#         try:
#             # Now saving email as well
#             cursor.execute("INSERT INTO app_users (username, email, password) VALUES (?, ?, ?)",
#                            (username, email, password_hash))
#             conn.commit()
#             return cursor.lastrowid
#         except sqlite3.IntegrityError:
#             return None
#         finally:
#             conn.close()
#
#     def verify_login(self, username, password):
#         conn = self.get_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT uid, password FROM app_users WHERE username = ?", (username,))
#         user_data = cursor.fetchone()
#         conn.close()
#         if user_data and user_data['password'] == password:
#             return user_data['uid']
#         return None
#
#     # --- SEARCH & STATEMENT METHODS ---
#     def add_search_event(self, uid, query_text, search_type, raw_data=None):
#         conn = self.get_connection()
#         cursor = conn.cursor()
#
#         # Convert the raw dictionary to a string for storage
#         # If raw_data is None (like for 'Analyze Own'), we save "{}".
#         json_str = json.dumps(raw_data) if raw_data else "{}"
#
#         cursor.execute("INSERT INTO search_history (uid, query_text, search_type, api_response) VALUES (?, ?, ?, ?)",
#                        (uid, query_text, search_type, json_str))
#
#         search_id = cursor.lastrowid
#         conn.commit()
#         conn.close()
#         return search_id
#
#     def add_analysis_results(self, search_id, results_list):
#         conn = self.get_connection()
#         cursor = conn.cursor()
#         data_to_insert = []
#         for row in results_list:
#             # Handle both dictionary (from analyzer) and tuple inputs
#             link = row.get('link', 'N/A')  # Statements have no link
#             content = row.get('text', row.get('content', ''))
#             sentiment = row['sentiment']
#             emotion = row['primary_emotion']
#             conf = row['confidence']
#             raw_data = json.dumps(row.get('raw_dict', row.get('raw_json', {})))
#
#             data_to_insert.append((search_id, link, content, sentiment, emotion, conf, raw_data))
#
#         cursor.executemany('''
#                            INSERT INTO analysis_results
#                            (search_id, post_link, content, sentiment, primary_emotion, confidence, raw_json)
#                            VALUES (?, ?, ?, ?, ?, ?, ?)
#                            ''', data_to_insert)
#         conn.commit()
#         conn.close()
#
#     # --- NEW: VIBE METHODS ---
#     def add_vibe_result(self, uid, subreddit, sentiment, emotion, score):
#         conn = self.get_connection()
#         cursor = conn.cursor()
#         cursor.execute('''
#                        INSERT INTO vibe_history (uid, subreddit, overall_sentiment, overall_emotion, match_score)
#                        VALUES (?, ?, ?, ?, ?)
#                        ''', (uid, subreddit, sentiment, emotion, score))
#         conn.commit()
#         conn.close()
#
#     # --- GETTERS ---
#     def get_searches_by_user_id(self, uid):
#         conn = self.get_connection()
#         cursor = conn.cursor()
#         # Combine standard searches and statement analysis
#         cursor.execute("SELECT * FROM search_history WHERE uid = ? ORDER BY created_at DESC", (uid,))
#         return cursor.fetchall()
#
#     def get_vibes_by_user_id(self, uid):
#         conn = self.get_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM vibe_history WHERE uid = ? ORDER BY created_at DESC", (uid,))
#         return cursor.fetchall()
#
#     def get_subreddit_vibe(self, subreddit):
#         """Checks if we already have data for this subreddit."""
#         conn = self.get_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM subreddit_vibes WHERE subreddit = ? COLLATE NOCASE", (subreddit,))
#         data = cursor.fetchone()
#         conn.close()
#         return data
#
#     def update_subreddit_vibe(self, subreddit, sentiment, emotion):
#         """Saves or Updates the cache."""
#         conn = self.get_connection()
#         cursor = conn.cursor()
#         # INSERT OR REPLACE will update the row if 'subreddit' already exists
#         cursor.execute('''
#             INSERT OR REPLACE INTO subreddit_vibes (subreddit, overall_sentiment, overall_emotion, last_updated)
#             VALUES (?, ?, ?, CURRENT_TIMESTAMP)
#         ''', (subreddit, sentiment, emotion))
#         conn.commit()
#         conn.close()

"""
Reddit Pulse - Database Management Module
==========================================
This module handles all database operations for the Reddit Pulse application,
including user management, search history, analysis results, and subreddit vibe caching.

Database Schema:
    - users: User account information
    - search_events: Log of all user searches
    - analysis_results: Individual emotion analysis records
    - subreddit_vibes: Cached community sentiment data

Author: Reddit Pulse Team
License: MIT
"""

import sqlite3
import hashlib
import json

class RedditDatabase:
    """
    Database manager for Reddit Pulse application.

    Handles all CRUD operations, authentication, and data persistence
    using SQLite as the backend database.
    """

    def __init__(self, db_name="reddit_pulse_2.db"):
        """
        Initialize database connection and create tables if they don't exist.

        Args:
            db_name (str): Name of the SQLite database file. Defaults to 'reddit_pulse.db'
        """
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        """
        Create and return a database connection.

        Returns:
            sqlite3.Connection: Active database connection with row factory enabled
        """
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Enables dictionary-like access to rows
        return conn

    def create_tables(self):
        """
        Create all required database tables if they don't already exist.

        Tables Created:
            - users: Stores user credentials and metadata
            - search_events: Logs all search operations
            - analysis_results: Stores emotion analysis data
            - subreddit_vibes: Caches subreddit community sentiment
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table - stores authentication and profile data
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           user_id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           username
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           email
                           TEXT,
                           password_hash
                           TEXT
                           NOT
                           NULL,
                           created_at
                           DATETIME
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # Search events table - logs all user searches
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS search_events
                       (
                           search_id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           user_id
                           INTEGER
                           NOT
                           NULL,
                           query_text
                           TEXT
                           NOT
                           NULL,
                           search_type
                           TEXT
                           NOT
                           NULL,
                           raw_json
                           TEXT,
                           created_at
                           DATETIME
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           user_id
                       )
                           )
                       ''')

        # Analysis results table - stores individual emotion predictions
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS analysis_results
                       (
                           result_id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           search_id
                           INTEGER
                           NOT
                           NULL,
                           link
                           TEXT,
                           content
                           TEXT
                           NOT
                           NULL,
                           sentiment
                           TEXT
                           NOT
                           NULL,
                           primary_emotion
                           TEXT
                           NOT
                           NULL,
                           confidence
                           REAL
                           NOT
                           NULL,
                           raw_emotions_json
                           TEXT,
                           created_at
                           DATETIME
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           search_id
                       ) REFERENCES search_events
                       (
                           search_id
                       )
                           )
                       ''')

        # Subreddit vibes cache - stores community sentiment for fast lookups
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS subreddit_vibes
                       (
                           vibe_id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           subreddit_name
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           overall_sentiment
                           TEXT
                           NOT
                           NULL,
                           overall_emotion
                           TEXT
                           NOT
                           NULL,
                           last_updated
                           DATETIME
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        conn.commit()
        conn.close()

    # ========================================================================
    # USER MANAGEMENT
    # ========================================================================

    def hash_password(self, password):
        """
        Hash a password using SHA-256.

        Args:
            password (str): Plain text password

        Returns:
            str: Hexadecimal hash of the password

        Security Note:
            SHA-256 is used for simplicity. For production, consider bcrypt or argon2.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username, email, password):
        """
        Register a new user in the database.

        Args:
            username (str): Unique username
            email (str): Unique email address
            password (str): Plain text password (will be hashed)

        Returns:
            int or None: The new user_id if successful, None if username/email already exists
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            # Username or email already exists
            conn.close()
            return None

    def verify_login(self, username, password):
        """
        Verify user credentials during login.

        Args:
            username (str): Username to authenticate
            password (str): Plain text password to verify

        Returns:
            int or None: user_id if credentials are valid, None otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        password_hash = self.hash_password(password)
        cursor.execute(
            "SELECT user_id FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )

        row = cursor.fetchone()
        conn.close()

        return row['user_id'] if row else None

    # ========================================================================
    # SEARCH EVENT MANAGEMENT
    # ========================================================================

    def add_search_event(self, user_id, query_text, search_type, raw_json_data):
        """
        Log a new search event to the database.

        Args:
            user_id (int): ID of the user performing the search
            query_text (str): The search query (subreddit name, topic, or username)
            search_type (str): Type of search ('subreddit', 'topic', 'user', or 'statement')
            raw_json_data (dict or None): Raw Reddit API response data

        Returns:
            int: The search_id of the newly created record
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Convert raw JSON to string for storage
        raw_json_str = json.dumps(raw_json_data) if raw_json_data else None

        cursor.execute(
            "INSERT INTO search_events (user_id, query_text, search_type, raw_json) VALUES (?, ?, ?, ?)",
            (user_id, query_text, search_type, raw_json_str)
        )

        conn.commit()
        search_id = cursor.lastrowid
        conn.close()

        return search_id

    def get_searches_by_user_id(self, user_id):
        """
        Retrieve all search history for a specific user.

        Args:
            user_id (int): ID of the user

        Returns:
            list[dict]: List of search records, ordered by most recent first
                Each dict contains: search_id, query_text, search_type, created_at
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT search_id, query_text, search_type, created_at FROM search_events WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # ========================================================================
    # ANALYSIS RESULTS MANAGEMENT
    # ========================================================================

    def add_analysis_results(self, search_id, results_list):
        """
        Save emotion analysis results to the database.

        Args:
            search_id (int): The parent search event ID
            results_list (list[dict]): List of analysis results, each containing:
                - link (str): URL to the analyzed content
                - content (str): The analyzed text
                - sentiment (str): Overall sentiment category
                - primary_emotion (str): Dominant emotion detected
                - confidence (float): Confidence score (0-1)
                - raw_json (dict): Full emotion probability distribution

        Returns:
            None
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        for result in results_list:
            # Convert raw emotion dict to JSON string
            raw_json_str = json.dumps(result.get('raw_json', {}))

            cursor.execute(
                '''INSERT INTO analysis_results
                   (search_id, link, content, sentiment, primary_emotion, confidence, raw_emotions_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (
                    search_id,
                    result.get('link', ''),
                    result.get('text', result.get('content', '')),  # Handle both key names
                    result['sentiment'],
                    result['primary_emotion'],
                    result['confidence'],
                    raw_json_str
                )
            )

        conn.commit()
        conn.close()

    # ========================================================================
    # SUBREDDIT VIBE CACHING
    # ========================================================================

    def update_subreddit_vibe(self, subreddit_name, overall_sentiment, overall_emotion):
        """
        Update or insert subreddit vibe data in the cache.

        This method uses UPSERT logic to either update existing records or insert new ones.
        The cache helps avoid re-scraping subreddits for vibe checks.

        Args:
            subreddit_name (str): Name of the subreddit (without 'r/')
            overall_sentiment (str): Dominant sentiment ('positive', 'negative', 'neutral', 'ambiguous')
            overall_emotion (str): Most common emotion detected

        Returns:
            None
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Use REPLACE to update if exists, insert if not
        cursor.execute(
            '''REPLACE
            INTO subreddit_vibes (subreddit_name, overall_sentiment, overall_emotion, last_updated)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)''',
            (subreddit_name.lower(), overall_sentiment, overall_emotion)
        )

        conn.commit()
        conn.close()

    def get_subreddit_vibe(self, subreddit_name):
        """
        Retrieve cached vibe data for a subreddit.

        Args:
            subreddit_name (str): Name of the subreddit (without 'r/')

        Returns:
            dict or None: Cached vibe data if found, containing:
                - overall_sentiment (str)
                - overall_emotion (str)
                - last_updated (datetime)
                Returns None if subreddit not in cache
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT overall_sentiment, overall_emotion, last_updated FROM subreddit_vibes WHERE subreddit_name = ?",
            (subreddit_name.lower(),)
        )

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None
