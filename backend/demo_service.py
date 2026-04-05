from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# --- Database Configuration ---
# Point 1: Increase the maximum connection pool size in the application configuration.
# This section demonstrates how to configure the database engine and its connection pool.
# Environment variables are preferred for sensitive data and easy configuration changes.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydatabase")

# Configure the SQLAlchemy engine with connection pooling parameters.
# pool_size: The number of connections to keep open in the pool.
# max_overflow: The number of connections that can be opened beyond the pool_size.
# pool_timeout: The number of seconds to wait before giving up on getting a connection from the pool.
# pool_recycle: The number of seconds after which a connection is automatically recycled.
#               Useful for preventing stale connections and handling database restarts.
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # Default is 5. Increased for demonstration.
    max_overflow=20,     # Default is 10. Increased for demonstration.
    pool_timeout=30,     # Default is 30 seconds.
    pool_recycle=3600,   # Recycle connections every hour (3600 seconds).
    # echo=True          # Uncomment to log all SQL statements for debugging
)

# Create a configured "Session" class.
# autocommit=False: Ensures transactions are explicitly committed.
# autoflush=False: Prevents flushing changes to the DB before commit, giving more control.
# bind=engine: Binds the session to our configured database engine.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Application Logic ---
def handler():
    """
    Handles a request, demonstrating database interaction with connection pooling
    and best practices for connection management.
    """
    db = None # Initialize db to None to ensure it's defined for the finally block
    try:
        # Point 3: Identify and fix any connection leaks in the application code.
        # Obtain a database session. This "borrows" a connection from the pool.
        db = SessionLocal()

        # Point 2: Optimize database queries to reduce their execution time and connection holding duration.
        # Example: Fetching a single item by ID.
        # - Ensure appropriate indexes exist on 'id' and other frequently queried columns.
        # - Select only the columns you need, e.g., `SELECT name, email FROM users`.
        # - Avoid N+1 query problems by using eager loading (e.g., `joinedload` in SQLAlchemy).
        # - For complex queries, use database-specific tools (like `EXPLAIN ANALYZE` in PostgreSQL)
        #   to understand query plan and identify bottlenecks.
        print("Executing a sample query...")
        result = db.execute(text("SELECT 'Hello from DB' as message, 1 as id")).fetchone()
        # A more realistic example:
        # result = db.execute(text("SELECT * FROM users WHERE id = :user_id"), {"user_id": 1}).fetchone()

        if result:
            print(f"Query result: {result.message} (ID: {result.id})")
        else:
            print("No result from query.")

        # If you were performing writes (INSERT, UPDATE, DELETE), you would commit here:
        # db.commit()
        # print("Transaction committed.")

    except Exception as e:
        # Point 3 (continued): Rollback transaction on error to prevent partial data.
        if db:
            db.rollback()
        print(f"An error occurred during database operation: {e}")

        # Point 4: Monitor database performance and application load.
        # Log errors and performance metrics to a monitoring system (e.g., Prometheus, Grafana, CloudWatch).
        # This helps in identifying issues, understanding application load, and determining the
        # appropriate connection pool size.
        # Example: logger.error("Database operation failed", exc_info=True)
        # Consider adding metrics for connection acquisition time, query execution time, etc.

    finally:
        # Point 3 (continued): Crucially, ensure the database session is closed.
        # This returns the connection to the pool, making it available for other requests.
        # Failing to close sessions leads to connection leaks and pool exhaustion.
        if db:
            db.close()
            print("Database session closed and connection returned to pool.")