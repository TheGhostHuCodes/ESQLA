from datetime import datetime

import pytest
from sqlalchemy import (Boolean, CheckConstraint, Column, create_engine,
                        DateTime, delete, ForeignKey, insert, Integer,
                        MetaData, Numeric, select, String, Table, update)
from sqlalchemy.exc import IntegrityError

metadata = MetaData()

cookies = Table(
    'cookies',
    metadata,
    Column('cookie_id', Integer(), primary_key=True),
    Column('cookie_name', String(50), index=True),
    Column('cookie_recipe_url', String(255)),
    Column('cookie_sku', String(55)),
    Column('quantity', Integer()),
    Column('unit_cost', Numeric(12, 2)),
    CheckConstraint('quantity > 0', name='quantity_positive'),
)

users = Table(
    'users',
    metadata,
    Column('user_id', Integer(), primary_key=True),
    Column('username', String(15), nullable=False, unique=True),
    Column('email_address', String(255), nullable=False),
    Column('phone', String(20), nullable=False),
    Column('password', String(25), nullable=False),
    Column('created_on', DateTime(), default=datetime.now),
    Column(
        'updated_on', DateTime(), default=datetime.now, onupdate=datetime.now),
)

orders = Table(
    'orders',
    metadata,
    Column('order_id', Integer(), primary_key=True),
    Column('user_id', ForeignKey('users.user_id', ondelete='CASCADE')),
    Column('shipped', Boolean(), default=False),
)

line_items = Table(
    'line_items',
    metadata,
    Column('line_items_id', Integer(), primary_key=True),
    Column('order_id', ForeignKey('orders.order_id', ondelete='CASCADE')),
    Column('cookie_id', ForeignKey('cookies.cookie_id', ondelete='CASCADE')),
    Column('quantity', Integer()),
    Column('extended_cost', Numeric(12, 2)),
)

engine = create_engine(
    'postgresql+psycopg2://postgres:postgres@localhost:5432')
metadata.create_all(engine)
connection = engine.connect()


def reset_primary_key_sequence(table, _id, reset_to=1):
    connection.execute(
        "ALTER SEQUENCE {table}_{_id}_seq RESTART WITH {start};".format(
            table=table, _id=_id, start=reset_to))


def ship_it(order_id):
    """Accept an order ID, removes the cookies from the inventory, and
    marks the order as shipped.

    Args:
        order_id (int): Order ID.
    """
    s = select([line_items.c.cookie_id, line_items.c.quantity]) \
        .where(line_items.c.order_id == order_id)
    transaction = connection.begin()
    cookies_to_ship = connection.execute(s).fetchall()
    try:
        for cookie in cookies_to_ship:
            u = update(cookies) \
                .where(cookies.c.cookie_id == cookie.cookie_id) \
                .values(quantity = cookies.c.quantity - cookie.quantity)
            connection.execute(u)
        u = update(orders) \
            .where(orders.c.order_id == order_id) \
            .values(shipped=True)
        connection.execute(u)
        print("Shipped order ID: {id}".format(id=order_id))
        transaction.commit()
    except IntegrityError as e:
        transaction.rollback()
        print(e)


# pylint: disable=E1120
@pytest.yield_fixture(autouse=True)
def clean_users_table():
    connection.execute(orders.delete())
    connection.execute(users.delete())
    connection.execute(cookies.delete())
    connection.execute(line_items.delete())
    reset_primary_key_sequence('users', 'user_id', 1)
    reset_primary_key_sequence('line_items', 'line_items_id', 1)
    reset_primary_key_sequence('orders', 'order_id', 1)
    reset_primary_key_sequence('cookies', 'cookie_id', 1)
    yield
    connection.execute(orders.delete())
    connection.execute(users.delete())
    connection.execute(cookies.delete())
    connection.execute(line_items.delete())


def test_access_attribute_not_queried_throws_AttributeError():
    with pytest.raises(AttributeError):
        ins = insert(users).values(
            username="cookiemon",
            email_address="mon@cookie.com",
            phone="111-111-1111",
            password="password",
        )
        result = connection.execute(ins)

        s = select([users.c.username])
        results = connection.execute(s)
        for result in results:
            print(result.username)
            print(result.password)


def test_inserting_two_unique_users_throws_IntegrityError():
    with pytest.raises(IntegrityError):
        ins = insert(users).values(
            username="cookiemon",
            email_address="mon@cookie.com",
            phone="111-111-1111",
            password="password",
        )
        connection.execute(ins)
        # Insert again to throw IntegrityError.
        connection.execute(ins)


def test_try_inserting_two_unique_users_prints_error():
    ins = insert(users).values(
        username="cookiemon",
        email_address="mon@cookie.com",
        phone="111-111-1111",
        password="password",
    )
    connection.execute(ins)
    try:
        connection.execute(ins)
    except IntegrityError as e:
        print(e.orig.pgerror, e.params)


def test_stuff():
    # Add user.
    ins = insert(users).values(
        username="cookiemon",
        email_address="mon@cookie.com",
        phone="111-111-1111",
        password="password")
    connection.execute(ins)

    s = select([users.c.user_id, users.c.username])
    result = connection.execute(s)
    print(80 * '#')
    for row in result:
        print(row)
    print(80 * '#')

    # Add cookies.
    ins = cookies.insert()
    inventory_list = [
        {
            'cookie_name': 'chocolate chip',
            'cookie_recipe_url': 'http://some.aweso.me/cookie/recipe.html',
            'cookie_sku': 'CC01',
            'quantity': '12',
            'unit_cost': '0.50'
        },
        {
            'cookie_name': 'dark chocolate chip',
            'cookie_recipe_url':
            'http://some.aweso.me/cookie/recipe_dark.html',
            'cookie_sku': 'CC02',
            'quantity': '1',
            'unit_cost': '0.75'
        },
    ]
    connection.execute(ins, inventory_list)

    # Add orders.
    ins = insert(orders).values(user_id=1, order_id=1)
    result = connection.execute(ins)
    ins = insert(line_items)
    order_items = [
        {
            'order_id': 1,
            'cookie_id': 1,
            'quantity': 9,
            'extended_cost': 4.50
        },
    ]
    result = connection.execute(ins, order_items)

    ins = insert(orders).values(user_id=1, order_id=2)
    result = connection.execute(ins)
    ins = insert(line_items)
    order_items = [
        {
            'order_id': 2,
            'cookie_id': 1,
            'quantity': 4,
            'extended_cost': 1.50
        },
        {
            'order_id': 2,
            'cookie_id': 2,
            'quantity': 1,
            'extended_cost': 4.50
        },
    ]
    result = connection.execute(ins, order_items)

    s = select([cookies.c.cookie_name, cookies.c.quantity])
    for cookie in connection.execute(s).fetchall():
        print(cookie)

    ship_it(1)
    for cookie in connection.execute(s).fetchall():
        print(cookie)

    ship_it(2)
    for cookie in connection.execute(s).fetchall():
        if cookie[0] == 'chocolate chip':
            assert cookie[1] == 3
        if cookie[0] == 'dark chocolate chip':
            assert cookie[1] == 1