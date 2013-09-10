from oscar.apps.order import utils as u

class OrderCreator(u.OrderCreator):
    def create_line_models(self, order, basket_line, extra_line_fields=None):
        order_line = super(OrderCreator, self).create_line_models(order, basket_line, extra_line_fields)
        if basket_line.real_quantity is not None:
            order_line.quantity = basket_line.real_quantity
            order_line.save()
        return order_line