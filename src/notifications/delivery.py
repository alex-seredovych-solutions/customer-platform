"""Notification transport receipts and delivery history."""
class DeliveryTracker:
    def __init__(self,db):
        self.db=db

    def mark_bounced(self,notice_id):
        self.db.run("UPDATE notifications SET status='BOUNCED' WHERE notice_id=?",(notice_id,))

    def by_order(self,order_id):
        return self.db.all('SELECT * FROM notifications WHERE order_id=? ORDER BY notice_id',(order_id,))
