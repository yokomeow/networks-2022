import pymysql
from pymysql.cursors import DictCursor

def connect():
    try:
        sql = pymysql.connect(
            host="localhost",
            user="root",
            password="muffin15",
            db="tt",
            port=3306,
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        return sql
    except Exception as e:
        print('Ошибка подключения к базе')
        print(e)

def create_table_users():

    sql = connect()
    cursor = sql.cursor()

    q = f"""
        create table if not exists users (
        user_id int primary key,
        a float(14,3) default 0{''.join([', ' + letter + ' float(14,3) default 0' for letter in 'bcdefghijklmnopqrstuvwxyz'])},
        a_t float(14,3) default 1{''.join([', ' + letter + '_t float(14,3) default 1' for letter in 'bcdefghijklmnopqrstuvwxyz'])},
        a_f float(14,3) default 0{''.join([', ' + letter + '_f float(14,3) default 0' for letter in 'bcdefghijklmnopqrstuvwxyz'])},
        attempts int
    )
    """

    cursor.execute(q)

    sql.close()

def create_table_words():

    sql = connect()
    cursor = sql.cursor()

    q = f"""
        create table if not exists words (
        id int primary key,
        word varchar(256),
        a int{''.join([', ' + letter + ' int' for letter in 'bcdefghijklmnopqrstuvwxyz'])}
    )
    """

    cursor.execute(q)

    sql.close()


if __name__=='__main__':
    create_table_users()
    create_table_words()
    print('Done!')
