import psycopg2


# Функция, создающая структуру БД (таблицы)
def create_db(connection):
    with connection.cursor() as cur:
        cur.execute("""
        DROP TABLE numbers;
        DROP TABLE clients;
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            surname VARCHAR(50) NOT NULL,
            email VARCHAR(50) NOT NULL UNIQUE
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS numbers(
            id SERIAL PRIMARY KEY,
            number VARCHAR(20) NOT NULL,
            client_id INTEGER NOT NULL REFERENCES clients(id)
        );
        """)
        connection.commit()


# Функция, позволяющая добавить нового клиента
def add_client(connection, first_name, last_name, email, phones=None):
    with connection.cursor() as cur:
        cur.execute("""
        INSERT INTO clients(name, surname, email) VALUES(%s, %s, %s) RETURNING id, name, surname, email;
        """, (first_name, last_name, email))
        connection.commit()
        if phones is not None:
            client_id = get_client_id(conn, email)
            add_phone(conn, client_id, phones)


# Функция, позволяющая добавить телефон для существующего клиента
def add_phone(connection, client_id, phone):
    with connection.cursor() as cur:
        cur.execute("""
        INSERT INTO numbers(number, client_id) VALUES(%s, %s) RETURNING id, number, client_id;
        """, (phone, client_id))
        connection.commit()


# Функция, позволяющая изменить данные о клиенте
def change_client(connection, client_id, first_name=None, last_name=None, email=None, phones=None):
    with connection.cursor() as cur:
        if first_name is not None:
            cur.execute("""
            UPDATE clients SET name=%s WHERE id=%s;
            """, (first_name, client_id))
            connection.commit()
        if last_name is not None:
            cur.execute("""
            UPDATE clients SET surname=%s WHERE id=%s;
            """, (last_name, client_id))
            connection.commit()
        if email is not None:
            cur.execute("""
            UPDATE clients SET email=%s WHERE id=%s;
            """, (email, client_id))
            connection.commit()
        if phones is not None:
            cur.execute("""
            UPDATE numbers SET number=%s WHERE client_id=%s;
            """, (phones, client_id))
            connection.commit()


# Функция, позволяющая удалить телефон для существующего клиента
def delete_phone(connection, client_id, phone):
    with connection.cursor() as cur:
        cur.execute("""
        DELETE FROM numbers WHERE client_id=%s AND number LIKE %s;
        """, (client_id, phone))
        connection.commit()


# Функция, позволяющая удалить существующего клиента
def delete_client(connection, client_id):
    with connection.cursor() as cur:
        cur.execute("""
        DELETE FROM numbers WHERE client_id=%s;
        """, (client_id,))
        cur.execute("""
        DELETE FROM clients WHERE id=%s;
        """, (client_id,))
        connection.commit()


# Функция, позволяющая найти клиента по его данным (имени, фамилии, email-у или телефону)
def find_client(connection, first_name=None, last_name=None, email=None, phone=None):
    with connection.cursor() as cur:
        if first_name is not None:
            cur.execute("""
            SELECT id FROM clients WHERE name=%s;
            """, (first_name,))
            return cur.fetchall()
        if last_name is not None:
            cur.execute("""
            SELECT id FROM clients WHERE surname=%s;
            """, (last_name,))
            return cur.fetchall()
        if email is not None:
            cur.execute("""
            SELECT id FROM clients WHERE email=%s;
            """, (email,))
            return cur.fetchall()
        if phone is not None:
            cur.execute("""
            SELECT client_id FROM numbers WHERE number=%s;
            """, (phone,))
            return cur.fetchall()


def get_client_id(connection, email):
    with connection.cursor() as cur:
        cur.execute("""
        SELECT id FROM clients WHERE email=%s;
        """, (email,))
        return cur.fetchone()[0]


with psycopg2.connect(database="sql_hw5", user="postgres", password="password") as conn:
    create_db(conn)
    add_client(conn, "Иван", "Иванов", "ivanov@mail.ru", "+7 999 888 77 66")
    add_client(conn, "Петр", "Петров", "petrov@mail.ru", "+7 999 555 44 33")
    add_client(conn, "Александр", "Александров", "aleksandrov@mail.ru")
    change_client(conn, 2, "Игорь", "Игорев", "igorev@mail.ru", "+7 777 777 77 77")
    delete_phone(conn, 1, "+7 999 888 77 66")
    delete_client(conn, 2)
    print(find_client(conn, "Александр"))

conn.close()
