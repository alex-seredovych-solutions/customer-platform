"""Customer notifications from authoritative order, payment and shipment milestones.

Delivery transport and message content are distinct concerns. Templates and
trigger subscriptions are selected by deployment configuration.
"""
from .templates import render

class OrderNotifications:
    def __init__(self,db,bus,clock,settings):
        self.db,self.bus,self.clock,self.settings=db,bus,clock,settings
        self._delivered_keys=set()

    def _send(self,order_id,purpose,package_id=None,source_event_id=None,source_version=None):
        if not order_id:
            raise ValueError('Order ID required for a customer notification')
        identity=(order_id,package_id,purpose,source_version)
        if self.settings.deduplicate_notification_events and identity in self._delivered_keys:
            return None
        notice_id=self.db.new_id('MSG')
        text=render(purpose)
        self.db.run('INSERT INTO notifications VALUES (?,?,?,?,?,?,?)',
                    (notice_id,order_id,package_id,purpose,text,'SENT',self.clock.now()))
        if self.settings.deduplicate_notification_events:
            self._delivered_keys.add(identity)
        self.bus.publish('notification.delivered',order_id=order_id,notice_id=notice_id,
                         package_id=package_id,purpose=purpose,
                         source_event_id=source_event_id,source_version=source_version)
        return notice_id

    def on_order_created(self,event):
        return self._send(event.payload['order_id'],'ORDER_CONFIRMED',
                          source_event_id=event.id,source_version=event.payload.get('version'))

    def on_order_canceled(self,event):
        return self._send(event.payload['order_id'],'ORDER_CANCELLED',
                          source_event_id=event.id,source_version=event.payload.get('version'))

    def on_refund_requested(self,event):
        purpose='REFUND_PROCESSING' if self.settings.refund_settlement_notifications else 'REFUND_COMPLETE'
        return self._send(event.payload['order_id'],purpose,
                          source_event_id=event.id,source_version=event.payload.get('refund_id'))

    def on_refund_settled(self,event):
        if self.settings.refund_settlement_notifications:
            return self._send(event.payload['order_id'],'REFUND_COMPLETE',
                              source_event_id=event.id,source_version=event.payload.get('refund_id'))
        return None

    def on_refund_failed(self,event):
        return self._send(event.payload['order_id'],'REFUND_FAILED',
                          source_event_id=event.id,source_version=event.payload.get('refund_id'))

    def on_warehouse_released(self,event):
        if not self.settings.carrier_only_ship_status:
            return self._send(event.payload['order_id'],'SHIPPED',event.payload['package_id'],
                              source_event_id=event.id,source_version=event.payload.get('order_version'))
        return None

    def on_carrier_accepted(self,event):
        if self.settings.carrier_only_ship_status:
            return self._send(event.payload['order_id'],'SHIPPED',event.payload['package_id'],
                              source_event_id=event.id,source_version=event.payload.get('manifest_id'))
        return None

    def on_line_exception(self,event):
        if 'order_id' in event.payload:
            return self._send(event.payload['order_id'],'ORDER_EXCEPTION',
                              package_id=event.payload.get('package_id'),source_event_id=event.id)
        return None


def notification_for_processor_state(processor_status):
    return {'PENDING':'REFUND_PROCESSING','SETTLED':'REFUND_COMPLETE',
            'FAILED':'REFUND_FAILED'}.get(processor_status)
