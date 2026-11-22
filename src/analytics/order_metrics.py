"""Shipment metrics from warehouse transitions or authoritative carrier custody.

The projection supports warehouse transition and carrier-custody event streams
with different rollout configurations.
"""
class OrderMetrics:
    def __init__(self,db,clock,settings=None):
        self.db,self.clock,self.settings=db,clock,settings

    def _record(self,event,source_status):
        order_id=event.payload['order_id']
        package_id=event.payload['package_id']
        if not package_id:
            return False
        if self.settings and self.settings.deduplicate_reporting_events:
            if self.db.one('SELECT * FROM shipment_facts WHERE source_event_id=?', (event.id,)):
                return False
            if self.db.one("SELECT * FROM shipment_facts WHERE package_id=? AND status='SHIPPED'",
                           (package_id,)):
                return False
        fact_id=self.db.new_id('FACT')
        self.db.run('INSERT INTO shipment_facts VALUES (?,?,?,?,?,?)',
                    (fact_id,order_id,package_id,event.id,source_status,self.clock.now()))
        return True

    def on_warehouse_released(self,event):
        if not self.settings or not self.settings.carrier_only_ship_status:
            return self._record(event,'SHIPPED')
        return False

    def on_carrier_accepted(self,event):
        if self.settings and self.settings.carrier_only_ship_status:
            return self._record(event,'SHIPPED')
        return False

    def shipped_packages(self,order_id):
        return self.db.one("SELECT COUNT(*) AS n FROM shipment_facts WHERE order_id=? AND status='SHIPPED'",
                           (order_id,))['n']

    def distinct_shipped_packages(self,order_id):
        return self.db.one("SELECT COUNT(DISTINCT package_id) AS n FROM shipment_facts "
                           "WHERE order_id=? AND status='SHIPPED'",(order_id,))['n']

    def status_summary(self,order_id):
        packages=self.db.all('SELECT * FROM packages WHERE order_id=?',(order_id,))
        fact_count=self.shipped_packages(order_id)
        accepted=sum(bool(row['carrier_accepted_at']) for row in packages)
        return {'order_id':order_id,'packages_total':len(packages),
                'carrier_accepted_packages':accepted,'reported_shipments':fact_count,
                'overreported':fact_count>accepted}


def accepted_package_count(carrier_events):
    return len({event['package_id'] for event in carrier_events if event.get('kind')=='carrier.accepted'})
