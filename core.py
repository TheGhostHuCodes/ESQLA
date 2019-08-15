from datetime import datetime
from pprint import pprint

from sqlalchemy import (
    and_,
    Boolean,
    cast,
    Column,
    create_engine,
    DateTime,
    delete,
    desc,
    ForeignKey,
    func,
    insert,
    Integer,
    MetaData,
    not_,
    Numeric,
    or_,
    select,
    String,
    Table,
    text,
    update,
)

# Database schema.
metadata = MetaData()

cookies = Table(
    "cookies",
    metadata,
    Column("cookie_id", Integer(), primary_key=True),
    Column("cookie_name", String(50), index=True),
    Column("cookie_recipe_url", String(255)),
    Column("cookie_sku", String(55)),
    Column("quantity", Integer()),
    Column("unit_cost", Numeric(12, 2)),
)

users = Table(
    "users",
    metadata,
    Column("user_id", Integer(), primary_key=True),
    Column("username", String(15), nullable=False, unique=True),
    Column("email_address", String(255), nullable=False),
    Column("phone", String(20), nullable=False),
    Column("password", String(25), nullable=False),
    Column("created_on", DateTime(), default=datetime.now),
    Column("updated_on", DateTime(), default=datetime.now, onupdate=datetime.now),
)

orders = Table(
    "orders",
    metadata,
    Column("order_id", Integer(), primary_key=True),
    Column("user_id", ForeignKey("users.user_id")),
    Column("shipped", Boolean(), default=False),
)

line_items = Table(
    "line_items",
    metadata,
    Column("line_item_id", Integer(), primary_key=True),
    Column("order_id", ForeignKey("orders.order_id")),
    Column("cookie_id", ForeignKey("cookies.cookie_id")),
    Column("quantity", Integer()),
    Column("extended_cost", Numeric(12, 2)),
)

engine = create_engine("postgresql+psycopg2://esqla:secret@localhost:5432/esqla_db")
#                                             ^^^^^ ^^^^^^ ^^^^^^^^^^^^^^ ^^^^^^^^
#                                             user  pass   host:port      database
metadata.create_all(engine)

# Insert cookies.
# pylint: disable=no-value-for-parameter
ins = cookies.insert().values(
    cookie_name="chocolate chip",
    cookie_recipe_url="http://some.aweso.me/cookie/recipe.html",
    cookie_sku="CC01",
    quantity="12",
    unit_cost="0.50",
)
print(str(ins))
print(ins.compile().params)

result = engine.execute(ins)
print(result.inserted_primary_key)

ins = insert(cookies).values(
    cookie_name="chocolate chip",
    cookie_recipe_url="http://some.aweso.me/cookie/recipe.html",
    cookie_sku="CC01",
    quantity="12",
    unit_cost="0.50",
)

# pylint: disable=no-value-for-parameter
ins = cookies.insert()
result = engine.execute(
    ins,
    cookie_name="dark chocolate chip",
    cookie_recipe_url="http://some.aweso.me/cookie/recipe_dark.html",
    cookie_sku="CC02",
    quantity="1",
    unit_cost="0.75",
)
print(result.inserted_primary_key)

inventory_list = [
    {
        "cookie_name": "peanut butter",
        "cookie_recipe_url": "http://some.aweso.me/cookie/peanut.html",
        "cookie_sku": "PB01",
        "quantity": "24",
        "unit_cost": "0.25",
    },
    {
        "cookie_name": "oatmeal raisin",
        "cookie_recipe_url": "http://some.okay.me/cookie/raisin.html",
        "cookie_sku": "EWW01",
        "quantity": "100",
        "unit_cost": "1.00",
    },
]
result = engine.execute(ins, inventory_list)

# Querying Data.
s = select([cookies])
print(str(s))
rp = engine.execute(s)
results = rp.fetchall()
pprint(results)

first_row = results[0]
print("first_row[1]: {}".format(first_row[1]))
print("first_row.cookie_name: {}".format(first_row.cookie_name))
print("first_row[cookies.c.cookie_name]: {}".format(first_row[cookies.c.cookie_name]))

s = cookies.select()
rp = engine.execute(s)
for record in rp:
    print(record.cookie_name)

s = select([cookies.c.cookie_name, cookies.c.quantity])
rp = engine.execute(s)
print(rp.keys())
print(rp.first())

s = select([cookies.c.cookie_name, cookies.c.quantity]).order_by(cookies.c.quantity)
rp = engine.execute(s)
for cookie in rp:
    print(
        "{quantity} - {name}".format(quantity=cookie.quantity, name=cookie.cookie_name)
    )

s = select([cookies.c.cookie_name, cookies.c.quantity]).order_by(
    desc(cookies.c.quantity)
)
rp = engine.execute(s)
for cookie in rp:
    print(
        "{quantity} - {name}".format(quantity=cookie.quantity, name=cookie.cookie_name)
    )

s = (
    select([cookies.c.cookie_name, cookies.c.quantity])
    .order_by(cookies.c.quantity)
    .limit(2)
)
rp = engine.execute(s)
pprint([result.cookie_name for result in rp])

s = select([func.sum(cookies.c.quantity)])
rp = engine.execute(s)
print(rp.scalar())

s = select([func.count(cookies.c.cookie_name)])
rp = engine.execute(s)
record = rp.first()
print(record.keys())
print(record.count_1)

s = select([func.count(cookies.c.cookie_name).label("inventory_count")])
rp = engine.execute(s)
record = rp.first()
print(record.keys())
print(record.inventory_count)

s = select([cookies]) \
    .where(cookies.c.cookie_name == 'chocolate chip')
rp = engine.execute(s)
record = rp.first()
pprint(record.items())

s = select([cookies]) \
    .where(cookies.c.cookie_name.like('%chocolate%'))
rp = engine.execute(s)
for record in rp.fetchall():
    print(record.cookie_name)

s = select([cookies.c.cookie_name, 'SKU-' + cookies.c.cookie_sku])
for row in engine.execute(s):
    print(row)

s = select([
    cookies.c.cookie_name,
    cast((cookies.c.quantity * cookies.c.unit_cost), Numeric(12, 2)) \
        .label('inv_cost')
    ])
for row in engine.execute(s):
    print('{name} - {cost}'.format(name=row.cookie_name, cost=row.inv_cost))

s = select([cookies]) \
    .where(and_(cookies.c.quantity > 23, cookies.c.unit_cost < 0.40))
for row in engine.execute(s):
    print(row.cookie_name)

s = select([cookies]) \
    .where(or_(
        cookies.c.quantity.between(10, 50),
        cookies.c.cookie_name.contains('chip'),
    ))
for row in engine.execute(s):
    print(row.cookie_name)

# Updates.
u = update(cookies) \
    .where(cookies.c.cookie_name == 'chocolate chip') \
    .values(quantity=(cookies.c.quantity + 120))
result = engine.execute(u)
print(result.rowcount)

s = select([cookies]) \
    .where(cookies.c.cookie_name == 'chocolate chip')
result = engine.execute(s).first()
for key in result.keys():
    print("{key:>20}: {value}".format(key=key, value=result[key]))

# Deletes.
u = delete(cookies) \
    .where(cookies.c.cookie_name == 'dark chocolate chip')
result = engine.execute(u)
print(result.rowcount)

s = select([cookies]) \
    .where(cookies.c.cookie_name == 'dark chocolate chip')
result = engine.execute(s).fetchall()
print(len(result))

# Insert customers.
customer_list = [
    {
        'username': 'cookiemon',
        'email_address': 'mon@cookie.com',
        'phone': '111-111-1111',
        'password': 'password'
    },
    {
        'username': 'cakeeater',
        'email_address': 'cakeeater@cake.com',
        'phone': '222-222-2222',
        'password': 'password'
    },
    {
        'username': 'pieguy',
        'email_address': 'guy@pie.com',
        'phone': '333-333-3333',
        'password': 'password'
    },
]
ins = users.insert()
result = engine.execute(ins, customer_list)

# Insert orders.
ins = insert(orders).values(user_id=1, order_id=1)
result = engine.execute(ins)
ins = insert(line_items)
order_items = [
    {
        'order_id': 1,
        'cookie_id': 1,
        'quantity': 2,
        'extended_cost': 1.00
    },
    {
        'order_id': 1,
        'cookie_id': 3,
        'quantity': 12,
        'extended_cost': 3.00
    },
]
result = engine.execute(ins, order_items)
ins = insert(orders).values(user_id=2, order_id=2)
result = engine.execute(ins)
ins = insert(line_items)
order_items = [
    {
        'order_id': 2,
        'cookie_id': 1,
        'quantity': 24,
        'extended_cost': 12.00
    },
    {
        'order_id': 2,
        'cookie_id': 4,
        'quantity': 6,
        'extended_cost': 6.00
    },
]
result = engine.execute(ins, order_items)

# Table join.
columns = [
    orders.c.order_id,
    users.c.username,
    users.c.phone,
    cookies.c.cookie_name,
    line_items.c.quantity,
    line_items.c.extended_cost,
]
cookiemon_orders = select(columns) \
    .select_from(orders.join(users).join(line_items).join(cookies)) \
    .where(users.c.username == 'cookiemon')
result = engine.execute(cookiemon_orders).fetchall()
for row in result:
    print(row)

# Outer join.
columns = [users.c.username, func.count(orders.c.order_id)]
all_orders = select(columns) \
    .select_from(users.outerjoin(orders)) \
    .group_by(users.c.username)
result = engine.execute(all_orders).fetchall()
for row in result:
    print(row)


# Chaining.
def get_orders_by_customers(customer_name, shipped=None, details=False):
    columns = [
        orders.c.order_id,
        users.c.username,
        users.c.phone,
    ]
    joins = users.join(orders)
    if details:
        columns.extend([
            cookies.c.cookie_name,
            line_items.c.quantity,
            line_items.c.extended_cost,
        ])
        joins = joins.join(line_items).join(cookies)
    customer_orders = select(columns) \
        .select_from(joins) \
        .where(users.c.username == customer_name)
    if shipped is not None:
        customer_orders = customer_orders.where(orders.c.shipped == shipped)
    result = engine.execute(customer_orders).fetchall()
    return result


pprint(get_orders_by_customers('cakeeater'))
pprint(get_orders_by_customers('cakeeater', details=True))
pprint(get_orders_by_customers('cakeeater', shipped=True))
pprint(get_orders_by_customers('cakeeater', shipped=False))
pprint(get_orders_by_customers('cakeeater', shipped=False, details=True))

# Raw SQL.
result = engine.execute('SELECT * FROM orders').fetchall()
pprint(result)

statement = select([users]) \
    .where(text("username='cookiemon'"))
pprint(engine.execute(statement).fetchall())