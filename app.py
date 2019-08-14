from sqlalchemy.sql import select

from db import dal


def get_orders_by_customer(customer_name, shipped=None, details=False):
    columns = [dal.orders.c.order_id, dal.users.c.username, dal.users.c.phone]
    joins = dal.users.join(dal.orders)

    if details:
        columns.extend([
            dal.cookies.c.cookie_name,
            dal.line_items.c.quantity,
            dal.line_items.c.extended_cost,
        ])
        joins = joins.join(dal.line_items).join(dal.cookies)

    customer_orders = select(columns) \
        .select_from(joins) \
        .where(dal.users.c.username == customer_name)

    if shipped is not None:
        customer_orders = customer_orders.where(
            dal.orders.c.shipped == shipped)

    return dal.connection.execute(customer_orders).fetchall()