import logging
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
Base = declarative_base()

# SQLAlchemy Engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# SessionLocal for database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency that provides a database session per request."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def ensure_database_exists():
    """
    Connect to MySQL server without specifying the target database
    and create the database if it doesn't exist yet.
    """
    try:
        encoded_password = quote_plus(settings.MYSQL_PASSWORD)
        root_url = (
            f"mysql+pymysql://{settings.MYSQL_USER}:{encoded_password}@"
            f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/?charset=utf8mb4"
        )
        temp_engine = create_engine(root_url, isolation_level="AUTOCOMMIT")
        with temp_engine.connect() as conn:
            conn.execute(
                text(f"CREATE DATABASE IF NOT EXISTS `{settings.MYSQL_DATABASE}` "
                     f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            )
        temp_engine.dispose()
        logger.info(f"Database '{settings.MYSQL_DATABASE}' is ready.")
    except Exception as e:
        logger.warning(f"Could not auto-create database '{settings.MYSQL_DATABASE}': {e}")

def init_db():
    """Create database and all tables if they do not exist."""
    ensure_database_exists()
    # Import all models to register them on Base metadata
    import app.models.user  # noqa: F401
    import app.models.blacklist  # noqa: F401
    import app.models.interview_report  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("All database tables verified/created successfully.")
