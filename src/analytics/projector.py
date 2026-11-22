"""Operational dashboard views and reconciliation checks."""
class Projector:
    def __init__(self,db):
        self.db=db

    def events_by_type(self):
        return self.db.all('SELECT event_type,COUNT(*) AS n FROM event_log GROUP BY event_type ORDER BY event_type')

    def package_counts(self):
        return self.db.all('SELECT status,COUNT(*) AS n FROM packages GROUP BY status')

    def carrier_disputes(self):
        """Find released packages that were rejected or never accepted by a carrier."""
        released=self.db.all("SELECT * FROM packages WHERE status='RELEASED'")
        mismatches=[]
        for package in released:
            manifest=self.db.one("SELECT * FROM carrier_manifests WHERE package_id=? "
                                 "ORDER BY processed_at DESC LIMIT 1",(package['package_id'],))
            if manifest and manifest['status']=='REJECTED':
                mismatches.append({'order_id':package['order_id'],
                                   'package_id':package['package_id'],
                                   'reason':manifest['reason']})
        return mismatches

    def unverified_release(self):
        return self.db.all("""SELECT p.package_id,p.order_id,p.status,t.pack_verified
            FROM packages p JOIN warehouse_tasks t ON t.package_id=p.package_id
            WHERE p.status IN ('RELEASED','SHIPPED') AND t.pack_verified=0""")
