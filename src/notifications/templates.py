"""Customer-facing template catalog."""
TEMPLATES={
    'ORDER_CONFIRMED':'Your order has been accepted.',
    'SHIPPED':'Your package has shipped.',
    'REFUND_COMPLETE':'Your refund has been completed.',
    'REFUND_PROCESSING':'Your refund is processing.',
    'ORDER_CANCELLED':'Your cancellation is confirmed.'
}

def render(template_key,**values):
    return TEMPLATES[template_key].format(**values)
