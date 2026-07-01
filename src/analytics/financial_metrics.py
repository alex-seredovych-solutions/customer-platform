"""Report payment authorizations separately from settled capture entries."""
class FinancialMetrics:
    def __init__(self,db):
        self.db=db

    def order_financials(self,order_id):
        order=self.db.one('SELECT * FROM orders WHERE order_id=?',(order_id,))
        captures=self.db.one('SELECT COALESCE(SUM(amount_cents),0) AS amount FROM captures WHERE order_id=?',(order_id,))['amount']
        refunds=self.db.one("SELECT COALESCE(SUM(amount_cents),0) AS amount FROM refunds WHERE order_id=? AND state='SETTLED'",(order_id,))['amount']
        return {'authorized_cents':order['amount_cents'],'captured_cents':captures,
                'settled_refunds_cents':refunds,'net_collected_cents':captures-refunds}
