#!/usr/bin/env python3
"""Keep IESO average-demand forecasts and reported demand with explicit EST intervals."""
import argparse,csv,io,re,xml.etree.ElementTree as ET
from datetime import datetime,timedelta,timezone
from common import ROOT,download,now,iso,date,record,save,status
EST=timezone(timedelta(hours=-5))
BASE='https://reports-public.ieso.ca/public/Adequacy3/'
DEMAND='https://reports-public.ieso.ca/public/Demand/'
NS={'i':'http://www.ieso.ca/schema'}

def hour_start(day,hour):
    hour=int(hour)
    if not 1<=hour<=24:raise ValueError('Invalid delivery hour')
    return datetime.fromisoformat(day).replace(tzinfo=EST)+timedelta(hours=hour-1)

def parse_forecast(raw,captured,archived=False):
    root=ET.fromstring(raw)
    if root.attrib.get('docID')!='Adequacy3':raise ValueError('Unexpected IESO report')
    issued=datetime.fromisoformat(root.findtext('i:DocHeader/i:CreatedAt',namespaces=NS)).replace(tzinfo=EST)
    day=root.findtext('i:DocBody/i:DeliveryDate',namespaces=NS)
    origin=issued if archived else captured
    if issued>captured+timedelta(minutes=5):raise ValueError('IESO issue time is in the future')
    values=root.findall('.//i:OntarioDemand/i:AverageDemand/i:Demand',NS)
    if len(values)!=24:raise ValueError('Expected 24 hourly average demand forecasts')
    points=[];seen=set()
    for item in values:
        h=int(item.findtext('i:DeliveryHour',namespaces=NS));target=hour_start(day,h)
        value=float(item.findtext('i:EnergyMW',namespaces=NS))
        if h in seen or not 0<value<60000:raise ValueError('Invalid demand forecast')
        seen.add(h)
        if target>origin:points.append({'target':iso(target),'value':value,'delivery_date':day,'delivery_hour':h})
    return iso(issued),sorted(points,key=lambda x:x['target'])

def parse_demand(raw,captured,lookback=45):
    lines=raw.decode('utf-8-sig').splitlines()
    try:start=next(i for i,line in enumerate(lines) if line.startswith('Date,Hour,'))
    except StopIteration:raise ValueError('Missing demand CSV header') from None
    rows=csv.DictReader(lines[start:]);points=[];seen=set()
    for row in rows:
        target=hour_start(row['Date'],row['Hour'])
        if not captured-timedelta(days=lookback)<=target<captured-timedelta(hours=1):continue
        value=float(row['Ontario Demand'])
        if not 0<value<60000 or iso(target) in seen:raise ValueError('Invalid or duplicate reported demand')
        seen.add(iso(target));points.append({'target':iso(target),'value':value,'delivery_date':row['Date'],'delivery_hour':int(row['Hour'])})
    if not points:raise ValueError('No recent reported demand')
    return points

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--bootstrap',action='store_true',help='Import three explicitly labelled historical issue versions once');args=parser.parse_args()
    stamp=now();today=stamp.astimezone(EST).date();records=[]
    for days in range(7):
        day=today+timedelta(days=days);url=BASE+'PUB_Adequacy3_'+day.strftime('%Y%m%d')+'.xml'
        raw=download(url);captured=now();issued,points=parse_forecast(raw,captured)
        if points:records.append(record('forecast','ontario','Ontario average demand',url,raw,points,captured_at=iso(captured),issued_at=issued,provenance='prospective',measurement='average-demand',units='MW'))
    if args.bootstrap:
        index=download(BASE).decode();available=set(re.findall(r'href="(PUB_Adequacy3_\d{8}_v\d+\.xml)"',index))
        for days in [3,2,1]:
            day=today-timedelta(days=days);prefix='PUB_Adequacy3_'+day.strftime('%Y%m%d')+'_v'
            choices=sorted([n for n in available if n.startswith(prefix)],key=lambda n:int(n.rsplit('_v',1)[1].split('.')[0]))
            if not choices:continue
            url=BASE+choices[0];raw=download(url);captured=now();issued,points=parse_forecast(raw,captured,True)
            if points:records.append(record('forecast','ontario','Ontario average demand',url,raw,points,captured_at=iso(captured),issued_at=issued,provenance='published_archive',measurement='average-demand',units='MW'))
    # Cross-year collection must retain both sides of New Year.
    years={today.year,(today-timedelta(days=45)).year}
    for year in sorted(years):
        url=DEMAND+f'PUB_Demand_{year}.csv';raw=download(url);captured=now();points=parse_demand(raw,captured)
        records.append(record('observation','ontario','Ontario average demand',url,raw,points,captured_at=iso(captured),provenance='observed',measurement='average-demand',units='MW'))
    for receipt in records:save(receipt)
    status([{'name':'IESO','status':'collected'}]);print(f'Saved {len(records)} IESO receipts.')
if __name__=='__main__':main()
