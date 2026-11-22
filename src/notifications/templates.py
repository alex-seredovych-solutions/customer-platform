"""Event-specific customer templates; no payment or address secrets."""
TEMPLATES={
    'ORDER_CONFIRMED':'Your order was placed successfully.',
    'ORDER_CANCELLED':'Your cancellation is confirmed. Payment adjustments may still be processing.',
    'REFUND_COMPLETE':'Your refund has been completed.',
    'REFUND_PROCESSING':'Your refund is processing. We will confirm when it settles.',
    'REFUND_FAILED':'Your refund could not be completed. Our team will follow up.',
    'ORDER_EXCEPTION':'An order item requires attention. We will share available options.',
    'SHIPPED':'Your package has shipped.',
}

def render(purpose,locale='en-US'):
    if purpose not in TEMPLATES:
        raise KeyError(f'Unknown notification purpose: {purpose}')
    # Localization and channel rules are not yet integrated with the customer
    # directory; the default English template is used for every recipient.
    return TEMPLATES[purpose]
