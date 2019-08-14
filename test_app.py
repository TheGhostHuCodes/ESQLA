import pytest
from sqlalchemy.sql import insert

from app import dal, get_orders_by_customer

# pylint: disable=E1120
dal.db_init('postgresql+psycopg2://postgres:postgres@localhost:5432')


def reset_primary_key_sequence(table, _id, reset_to=1):
    dal.connection.execute(
        "ALTER SEQUENCE {table}_{_id}_seq RESTART WITH {start};".format(
            table=table, _id=_id, start=reset_to))


def prep_db():
    ins = dal.cookies.insert()
    dal.connection.execute(
        ins,
        cookie_name='dark chocolate chip',
        cookie_recipe_url='http://some.aweso.me/cookie/recipe_dark.html',
        cookie_sku='CC02',
        quantity='1',
        unit_cost='0.75')
    inventory_list = [
        {
            'cookie_name': 'peanut butter',
            'cookie_recipe_url': 'http://some.aweso.me/cookie/peanut.html',
            'cookie_sku': 'PB01',
            'quantity': '24',
            'unit_cost': '0.25'
        },
        {
            'cookie_name': 'oatmeal raisin',
            'cookie_recipe_url': 'http://some.okay.me/cookie/raisin.html',
            'cookie_sku': 'EWW01',
            'quantity': '100',
            'unit_cost': '1.00'
        },
    ]
    dal.connection.execute(ins, inventory_list)

    customer_list = [
        {
            'username': "cookiemon",
            'email_address': "mon@cookie.com",
            'phone': "111-111-1111",
            'password': "password"
        },
        {
            'username': "cakeeater",
            'email_address': "cakeeater@cake.com",
            'phone': "222-222-2222",
            'password': "password"
        },
        {
            'username': "pieguy",
            'email_address': "guy@pie.com",
            'phone': "333-333-3333",
            'password': "password"
        },
    ]

    ins = dal.users.insert()
    dal.connection.execute(ins, customer_list)
    ins = insert(dal.orders).values(user_id=1, order_id='wlk001')
    dal.connection.execute(ins)
    ins = insert(dal.line_items)
    order_items = [
        {
            'order_id': 'wlk001',
            'cookie_id': 1,
            'quantity': 2,
            'extended_cost': 1.00
        },
        {
            'order_id': 'wlk001',
            'cookie_id': 3,
            'quantity': 12,
            'extended_cost': 3.00
        },
    ]
    dal.connection.execute(ins, order_items)
    ins = insert(dal.orders).values(user_id=2, order_id='ol001')
    dal.connection.execute(ins)
    ins = insert(dal.line_items)

    order_items = [
        {
            'order_id': 'ol001',
            'cookie_id': 1,
            'quantity': 24,
            'extended_cost': 12.00
        },
        {
            'order_id': 'ol001',
            'cookie_id': 4,
            'quantity': 6,
            'extended_cost': 6.00
        },
    ]
    dal.connection.execute(ins, order_items)


@pytest.yield_fixture(scope='module', autouse=True)
def clean_users_table():
    dal.connection.execute(dal.orders.delete())
    dal.connection.execute(dal.users.delete())
    dal.connection.execute(dal.cookies.delete())
    dal.connection.execute(dal.line_items.delete())
    reset_primary_key_sequence('users', 'user_id', 1)
    reset_primary_key_sequence('line_items', 'line_items_id', 1)
    reset_primary_key_sequence('orders', 'order_id', 1)
    reset_primary_key_sequence('cookies', 'cookie_id', 1)
    prep_db()
    yield
    dal.connection.execute(dal.orders.delete())
    dal.connection.execute(dal.users.delete())
    dal.connection.execute(dal.cookies.delete())
    dal.connection.execute(dal.line_items.delete())


def test_get_orders_by_customer_blank_returns_empty_list():
    results = get_orders_by_customer('')
    assert results == []


def test_get_orders_by_customer_blank_shipped_returns_empty_list():
    results = get_orders_by_customer('', shipped=True)
    assert results == []


def test_get_orders_by_customer_blank_not_shipped_returns_empty_list():
    results = get_orders_by_customer('', shipped=False)
    assert results == []


def test_get_orders_by_customer_blank_details_returns_empty_list():
    results = get_orders_by_customer('', details=True)
    assert results == []


def test_get_orders_by_customer_blank_shipped_details_returns_empty_list():
    results = get_orders_by_customer('', shipped=True, details=True)
    assert results == []


def test_get_orders_by_customer_blank_not_shipped_details_returns_empty_list():
    results = get_orders_by_customer('', shipped=False, details=True)
    assert results == []
