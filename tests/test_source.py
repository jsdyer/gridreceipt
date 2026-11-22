import sys,unittest
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from collect import hour_start,parse_forecast,parse_demand
class GridTests(unittest.TestCase):
    def test_ieso_uses_fixed_est_even_during_daylight_saving(self):
        self.assertEqual(hour_start('2026-07-01',1).astimezone(timezone.utc).hour,5)
        self.assertEqual(hour_start('2026-07-01',24).astimezone(timezone.utc).isoformat(),'2026-07-02T04:00:00+00:00')
    def xml(self):
        points=''.join(f'<Demand><DeliveryHour>{h}</DeliveryHour><EnergyMW>{15000+h}</EnergyMW></Demand>' for h in range(1,25))
        return ('<Document docID="Adequacy3" xmlns="http://www.ieso.ca/schema"><DocHeader><CreatedAt>2026-11-20T08:00:00</CreatedAt></DocHeader><DocBody><DeliveryDate>2026-11-21</DeliveryDate><OntarioDemand><AverageDemand>'+points+'</AverageDemand><PeakDemand><Demand><EnergyMW>99999</EnergyMW></Demand></PeakDemand></OntarioDemand></DocBody></Document>').encode()
    def test_average_series_and_prospective_vs_historical_eligibility(self):
        issued,points=parse_forecast(self.xml(),datetime(2026,11,22,12,tzinfo=timezone.utc));self.assertEqual(points,[])
        issued,points=parse_forecast(self.xml(),datetime(2026,11,22,tzinfo=timezone.utc),True);self.assertEqual(len(points),24);self.assertEqual(points[0]['value'],15001)
    def test_market_demand_is_not_substituted_for_ontario(self):
        raw=b'\\\\Created at example\nDate,Hour,Market Demand,Ontario Demand\n2026-11-21,1,21000,16000\n'
        self.assertEqual(parse_demand(raw,datetime(2026,11,22,tzinfo=timezone.utc))[0]['value'],16000)
    def test_duplicate_reported_hour_is_rejected(self):
        raw=b'Date,Hour,Market Demand,Ontario Demand\n2026-11-21,1,21000,16000\n2026-11-21,1,21000,17000\n'
        with self.assertRaises(ValueError):parse_demand(raw,datetime(2026,11,22,tzinfo=timezone.utc))
