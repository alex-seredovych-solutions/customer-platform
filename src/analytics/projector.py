"""Daily warehouse projections and current snapshot aggregation."""
class Projector:
    def __init__(self,db):
        self.db=db

    def events_by_type(self):
        return self.db.all('SELECT event_type,COUNT(*) AS n FROM event_log GROUP BY event_type ORDER BY event_type')

    def package_counts(self):
        return self.db.all('SELECT status,COUNT(*) AS n FROM packages GROUP BY status')
