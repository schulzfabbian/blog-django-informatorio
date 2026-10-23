# PyMySQL es opcional: solo se usa si está instalado (por ejemplo, para MySQL).
try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    pass
