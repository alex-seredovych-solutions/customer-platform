"""Card authorization, settled capture and financial reconciliation by order."""
class FinancialMetrics:
    def __init__(self,db):
        self.db=db

    def order_financials(self,order_id):
        order=self.db.one('SELECT * FROM orders WHERE order_id=?',(order_id,))
        if not order:
            raise KeyError(order_id)
        captures=self.db.all('SELECT * FROM captures WHERE order_id=?',(order_id,))
        refunds=self.db.all('SELECT * FROM refunds WHERE order_id=?',(order_id,))
        captured=sum(row['amount_cents'] for row in captures if row['status']=='SETTLED')
        settled_refunds=sum(row['amount_cents'] for row in refunds if row['state']=='SETTLED')
        pending_refunds=sum(row['amount_cents'] for row in refunds if row['state']=='PENDING')
        return {'authorized_cents':order['amount_cents'],
                'captured_cents':captured,'settled_refunds_cents':settled_refunds,
                'pending_refunds_cents':pending_refunds,
                'net_collected_cents':captured-settled_refunds,
                'capture_count':len(captures),
                'unlinked_capture_count':sum(row['package_id'] is None for row in captures)}

    def allocation_discrepancies(self,order_id):
        invoice=self.db.one('SELECT * FROM orders WHERE order_id=?',(order_id,))
        allocations=self.db.all('SELECT * FROM order_line_allocations WHERE order_id=?',(order_id,))
        allocated=sum(row['card_due_cents'] for row in allocations)
        captures=self.order_financials(order_id)
        return {'invoice_total_cents':invoice['amount_cents'],
                'allocated_line_cents':allocated,
                'unallocated_cents':invoice['amount_cents']-allocated,
                'captures_without_package':captures['unlinked_capture_count']}
