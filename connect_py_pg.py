import psycopg as pg

connn= pg.connect(
    host='localhost',
    dbname= 'myreadapp',
    user= 'postgres',
    password= 'postgres',
    port=5432
)
