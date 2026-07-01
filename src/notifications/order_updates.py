"""Order, parcel and financial notifications sent from event subscribers."""
from .templates import render

class OrderNotifications:
    def __init__(self,db,bus,clock,settings):
        self.db,self.bus,self.clock,self.settings=db,bus,clock,settings

    def _send(self,order_id,purpose,package_id=None):
        notice_id=self.db.new_id('MSG')
        self.db.run('INSERT INTO notifications VALUES (?,?,?,?,?,?,?)',
                    (notice_id,order_id,package_id,purpose,render(purpose),'SENT',self.clock.now()))
        self.bus.publish('notification.delivered',order_id=order_id,notice_id=notice_id,purpose=purpose)
        return notice_id

    def on_order_created(self,event):
        self._send(event.payload['order_id'],'ORDER_CONFIRMED')

    def on_order_canceled(self,event):
        self._send(event.payload['order_id'],'ORDER_CANCELLED')

    def on_refund_requested(self,event):
        if not self.settings.refund_settlement_notifications:
            self._send(event.payload['order_id'],'REFUND_COMPLETE')
        else:
            self._send(event.payload['order_id'],'REFUND_PROCESSING')

    def on_refund_settled(self,event):
        if self.settings.refund_settlement_notifications:
            self._send(event.payload['order_id'],'REFUND_COMPLETE')

    def on_warehouse_released(self,event):
        if not self.settings.carrier_only_ship_status:
            self._send(event.payload['order_id'],'SHIPPED',event.payload['package_id'])

    def on_carrier_accepted(self,event):
        if self.settings.carrier_only_ship_status:
            self._send(event.payload['order_id'],'SHIPPED',event.payload['package_id'])
