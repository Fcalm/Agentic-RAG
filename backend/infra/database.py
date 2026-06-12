import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/langchain_app",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


def _clean_nul_chars(val):
    """递归清除 Python 数据结构中字符串里的 \x00 (NUL) 字符以及无法转为 UTF-8 的孤立代理项字符 (Surrogates)。"""
    if isinstance(val, str):
        val = val.replace("\x00", "")
        try:
            return val.encode("utf-8", "ignore").decode("utf-8")
        except Exception:
            return val
    elif isinstance(val, dict):
        return {k: _clean_nul_chars(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [_clean_nul_chars(v) for v in val]
    elif isinstance(val, tuple):
        return tuple(_clean_nul_chars(v) for v in val)
    return val


@event.listens_for(engine, "before_cursor_execute", retval=True)
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """
    SQLAlchemy 全局引擎监听器：拦截所有底层的 SQL 执行和传入绑定的参数。
    在所有底层驱动执行前自动过滤、擦除所有参数中的 \x00 字符，
    彻底、优雅地解决 PostgreSQL 不允许 VARCHAR/TEXT 写入 NUL (0x00) 字节的异常，
    使业务层不需要在各处手动书写 replace() 代码。
    """
    if parameters is not None:
        if isinstance(parameters, dict):
            for k, v in list(parameters.items()):
                parameters[k] = _clean_nul_chars(v)
        elif isinstance(parameters, list):
            for i, v in enumerate(parameters):
                parameters[i] = _clean_nul_chars(v)
        elif isinstance(parameters, tuple):
            parameters = tuple(_clean_nul_chars(v) for v in parameters)
    return statement, parameters


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base = declarative_base()


def init_db() -> None:
    # Delayed import to avoid circular dependency.
    import backend.db.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
