"""One-shot helper to list tables in the configured database."""

from sqlalchemy import create_engine, text

from app.core.config import settings


def main() -> None:
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
        )
        tables = [row[0] for row in result]

    print(f"Tables in Railway Postgres ({len(tables)} total):")
    for t in tables:
        print(f"  - {t}")


if __name__ == "__main__":
    main()
