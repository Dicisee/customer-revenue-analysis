import csv,zipfile,sqlite3,os,collections,decimal,json,argparse,io
from pathlib import Path
parser=argparse.ArgumentParser(description='Reproduce customer revenue analysis from the original case study ZIP')
parser.add_argument('--input', default='Case Study.zip', help='Path to the original ZIP containing casestudy.csv')
args=parser.parse_args()
P=Path(__file__).resolve().parent
input_zip=Path(args.input).expanduser().resolve()
if not input_zip.is_file():
 raise SystemExit(f'Input not found: {input_zip}. Pass --input "Case Study.zip"')
(P/'sql').mkdir(exist_ok=True)
(P/'data').mkdir(exist_ok=True)
db=sqlite3.connect(':memory:'); db.execute('create table orders(customer_email text, net_revenue_cents integer, year integer)'); stats=collections.Counter(); years=collections.Counter(); duplicates=collections.Counter(); raw_rows=0
with zipfile.ZipFile(input_zip) as z, z.open('casestudy.csv') as f:
 import io
 reader=csv.DictReader(io.TextIOWrapper(f,encoding='utf-8-sig',newline=''))
 batch=[]
 for row in reader:
  raw_rows+=1; email=(row['customer_email'] or '').strip().lower(); year=int(row['year']); amount=decimal.Decimal(row['net_revenue']); cents=int((amount*100).quantize(decimal.Decimal('1')))
  if not email: stats['missing_email']+=1;continue
  if email != row['customer_email']:stats['normalized_email_rows']+=1
  batch.append((email,cents,year)); years[year]+=1
  if len(batch)==20000:db.executemany('insert into orders values(?,?,?)',batch);batch=[]
 if batch:db.executemany('insert into orders values(?,?,?)',batch)
db.execute('create index idx_orders_year_email on orders(year,customer_email)')
db.execute('create table customer_year as select year, customer_email, sum(net_revenue_cents) revenue_cents from orders group by year,customer_email');db.execute('create unique index idx_cy on customer_year(year,customer_email)')
ys=[r[0] for r in db.execute('select distinct year from customer_year order by year')]; print('raw',raw_rows,'years',ys,'stats',stats,'rows',years)
metrics=['Total Revenue Current Year','New Customer Revenue','Existing Customer Growth','Revenue Lost from Attrition','Existing Customer Revenue Current Year','Existing Customer Revenue Prior Year','Total Customers Current Year','Total Customers Previous Year','New Customers','Lost Customers']
# Standard SQL compatible SQLite; use CTE and correlated previous-year joins; years from current rows, earliest year comparison undefined.
queries={
'01_total_revenue.sql':'''SELECT year, ROUND(SUM(revenue_cents) / 100.0, 2) AS total_revenue_current_year FROM customer_year GROUP BY year ORDER BY year;''',
'02_new_customer_revenue.sql':'''SELECT c.year, ROUND(SUM(CASE WHEN p.customer_email IS NULL THEN c.revenue_cents ELSE 0 END) / 100.0, 2) AS new_customer_revenue FROM customer_year c LEFT JOIN customer_year p ON p.customer_email = c.customer_email AND p.year = c.year - 1 WHERE c.year > (SELECT MIN(year) FROM customer_year) GROUP BY c.year ORDER BY c.year;''',
'03_existing_customer_growth.sql':'''SELECT c.year, ROUND(SUM(c.revenue_cents - p.revenue_cents) / 100.0, 2) AS existing_customer_growth FROM customer_year c JOIN customer_year p ON p.customer_email = c.customer_email AND p.year = c.year - 1 GROUP BY c.year ORDER BY c.year;''',
'04_revenue_lost_from_attrition.sql':'''SELECT y.year, ROUND(SUM(CASE WHEN c.customer_email IS NULL THEN p.revenue_cents ELSE 0 END) / 100.0, 2) AS revenue_lost_from_attrition FROM (SELECT DISTINCT year FROM customer_year) y JOIN customer_year p ON p.year = y.year - 1 LEFT JOIN customer_year c ON c.year = y.year AND c.customer_email = p.customer_email GROUP BY y.year ORDER BY y.year;''',
'05_existing_customer_revenue_current_year.sql':'''SELECT c.year, ROUND(SUM(c.revenue_cents) / 100.0, 2) AS existing_customer_revenue_current_year FROM customer_year c JOIN customer_year p ON p.customer_email = c.customer_email AND p.year = c.year - 1 GROUP BY c.year ORDER BY c.year;''',
'06_existing_customer_revenue_prior_year.sql':'''SELECT c.year, ROUND(SUM(p.revenue_cents) / 100.0, 2) AS existing_customer_revenue_prior_year FROM customer_year c JOIN customer_year p ON p.customer_email = c.customer_email AND p.year = c.year - 1 GROUP BY c.year ORDER BY c.year;''',
'07_total_customers_current_year.sql':'''SELECT year, COUNT(*) AS total_customers_current_year FROM customer_year GROUP BY year ORDER BY year;''',
'08_total_customers_previous_year.sql':'''SELECT y.year, COUNT(*) AS total_customers_previous_year FROM (SELECT DISTINCT year FROM customer_year) y JOIN customer_year p ON p.year = y.year - 1 GROUP BY y.year ORDER BY y.year;''',
'09_new_customers.sql':'''SELECT c.year, COUNT(*) AS new_customers FROM customer_year c LEFT JOIN customer_year p ON p.customer_email = c.customer_email AND p.year = c.year - 1 WHERE p.customer_email IS NULL AND c.year > (SELECT MIN(year) FROM customer_year) GROUP BY c.year ORDER BY c.year;''',
'10_lost_customers.sql':'''SELECT y.year, COUNT(*) AS lost_customers FROM (SELECT DISTINCT year FROM customer_year) y JOIN customer_year p ON p.year = y.year - 1 LEFT JOIN customer_year c ON c.year = y.year AND c.customer_email = p.customer_email WHERE c.customer_email IS NULL GROUP BY y.year ORDER BY y.year;'''
}
for name,sql in queries.items():
 (P/'sql'/name).write_text('-- Run after executing setup.sql. First year has no prior-year baseline where relevant.\n'+sql+'\n')
 print(name,list(db.execute(sql))[:5])
setup='''-- SQLite setup. Load the supplied CSV into a staging table (staging_orders) with\n-- customer_email TEXT, net_revenue TEXT, year INTEGER, and optional index column.\n-- The provided Python preparation script loads/normalizes the original ZIP directly.\n-- If loading manually, execute the statements below after importing into staging_orders.\nCREATE TABLE customer_year AS\nSELECT CAST(year AS INTEGER) AS year, LOWER(TRIM(customer_email)) AS customer_email,\n       SUM(CAST(ROUND(CAST(net_revenue AS REAL)*100,0) AS INTEGER)) AS revenue_cents\nFROM staging_orders WHERE TRIM(COALESCE(customer_email,'')) <> ''\nGROUP BY CAST(year AS INTEGER), LOWER(TRIM(customer_email));\nCREATE UNIQUE INDEX idx_customer_year ON customer_year(year,customer_email);\n'''
(P/'sql'/'setup.sql').write_text(setup)
# Make results from independent set arithmetic and exact cents
byyear={}
for y,e,c in db.execute('select year,customer_email,revenue_cents from customer_year'):
 byyear.setdefault(y,{})[e]=c
result=[]
for i,y in enumerate(ys):
 curr=byyear[y]; prev=byyear.get(y-1)
 row={'Year':y,'Total Revenue Current Year':sum(curr.values())/100,'Total Customers Current Year':len(curr)}
 if prev is not None:
  cs=set(curr);ps=set(prev); existing=cs&ps;new=cs-ps;lost=ps-cs
  row.update({'New Customer Revenue':sum(curr[k] for k in new)/100,'Existing Customer Growth':sum(curr[k]-prev[k] for k in existing)/100,'Revenue Lost from Attrition':sum(prev[k] for k in lost)/100,'Existing Customer Revenue Current Year':sum(curr[k] for k in existing)/100,'Existing Customer Revenue Prior Year':sum(prev[k] for k in existing)/100,'Total Customers Previous Year':len(prev),'New Customers':len(new),'Lost Customers':len(lost)})
  assert round(row['Total Revenue Current Year']-row['New Customer Revenue']-row['Existing Customer Revenue Current Year'],2)==0
  assert round(row['Total Revenue Current Year']-sum(prev.values())/100-(row['New Customer Revenue']+row['Existing Customer Growth']-row['Revenue Lost from Attrition']),2)==0
  assert len(curr)==len(existing)+len(new) and len(prev)==len(existing)+len(lost)
 else:
  for k in metrics:
   if k not in row:row[k]=''
 result.append(row)
# verify each query independently against result
for filename,sql in queries.items():
 field=next(k for k in metrics if k.lower().replace(' ','_') in sql.lower() or k.lower().replace(' ','_') in filename.lower()) if False else None
 expected_field=metrics[int(filename[:2])-1]
 for y,v in db.execute(sql):
  expected=next(r[expected_field] for r in result if r['Year']==y)
  assert abs(v-expected)<0.00001,(filename,y,v,expected)
with open(P/'data'/'tableau_yearly_metrics.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['Year']+metrics);w.writeheader();w.writerows(result)
# SQL script one-shot for SQLite CLI
(P/'sql'/'all_10_queries.sql').write_text('\n\n'.join('-- '+name+'\n'+sql for name,sql in queries.items())+'\n')
(P/'data'/'validation.json').write_text(json.dumps({'input_rows':raw_rows,'normalized_email_rows':stats['normalized_email_rows'],'year_order_counts':dict(years),'unique_customer_year_pairs':sum(len(v) for v in byyear.values()),'years':ys,'tests':'All ten SQL outputs match independently computed Python metrics; revenue and customer reconciliations pass.'},indent=2))
print('RESULTS',json.dumps(result,indent=2))
