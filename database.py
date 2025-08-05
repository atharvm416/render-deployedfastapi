from databases import Database
from sqlalchemy import create_engine, MetaData

# Use the external Render database URL with the proper format
DATABASE_URL = "postgresql+asyncpg://banquethall_user:DAr8Ac0blhWLZocyjCtkohzzCyA5L9PK@dpg-d28qj2uuk2gs73fm6n40-a.oregon-postgres.render.com/banquethall"

database = Database(DATABASE_URL)
metadata = MetaData()
