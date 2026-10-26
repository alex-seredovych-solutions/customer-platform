"""Operational shipment and order-status projection."""
class OrderMetrics:
    def __init__(self,db,clock):
        self.db,self.clock=db,clock

    def on_warehouse_released(self,event):
        fid=self.db.new_id('FACT')
        self.db.run('INSERT INTO shipment_facts VALUES (?,?,?,?,?,?)',
             (fid,event.payload['order_id'],event.payload['package_id'],event.id,'SHIPPED',self.clock.now()))

    def shipped_packages(self,order_id):
        return self.db.one("SELECT COUNT(*) AS n FROM shipment_facts WHERE order_id=? AND status='SHIPPED'",
                           (order_id,))['n']

    def distinct_shipped_packages(self,order_id):
        return self.db.one("SELECT COUNT(DISTINCT package_id) AS n FROM shipment_facts WHERE order_id=? AND status='SHIPPED'",
                           (order_id,))['n']


def accepted_package_count(carrier_events):
    return len({event['package_id'] for event in carrier_events if event.get('kind') == 'carrier.accepted'})
