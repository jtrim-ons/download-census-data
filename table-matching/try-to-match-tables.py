import csv

class Table(object):
    def __init__(self, table_id, table_name):
        self.table_id = table_id
        self.table_name = table_name
        self.cell_names = set()
        self.cell_name_to_id = {}
        self.cell_id_to_name = {}
    
    def __repr__(self):
        return 'Table("{}", "{}")'.format(self.table_id, self.table_name)

tables = {2001: {}, 2011: {}}
with open('cells-export.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        year = int(row['year'])
        if year not in [2001, 2011]:
            continue
        table_id = row['table_id']
        table_name = row['table_name']
        cell_id = row['cell_id']
        cell_name = row['cell_name']
        if table_id not in tables[year]:
            tables[year][table_id] = Table(table_id, table_name)
        table = tables[year][table_id]
        #print(table)
        table.cell_names.add(cell_name)
        table.cell_name_to_id[cell_name] = cell_id
        table.cell_id_to_name[cell_id] = cell_name
        #print(year)

        #print(row)

def print_table(table2011, table2001):
    print('<table class="table">')
    print('  <thead>')
    print('    <tr>')
    print('      <th>Cell code 2011</th>')
    print('      <th>Cell code 2001</th>')
    print('      <th>Cell name</th>')
    print('    </tr>')
    print('  </thead>')
    print('  <tbody>')
    for cell_id in sorted(int(k) for k in table2011.cell_id_to_name.keys()):
        cell_name = table2011.cell_id_to_name[str(cell_id)]
        if cell_name in table2001.cell_names:
            print('    <tr class="in-both-years">')
            print('      <td>{}</td>'.format(table2011.cell_name_to_id[cell_name]))
            print('      <td>{}</td>'.format(table2001.cell_name_to_id[cell_name]))
            print('      <td>{}</td>'.format(cell_name))
            print('    </tr>')
        else:
            print('    <tr class="in-2011-only">')
            print('      <td>{}</td>'.format(table2011.cell_name_to_id[cell_name]))
            print('      <td>-</td>')
            print('      <td>{}</td>'.format(cell_name))
            print('    </tr>')
    for cell_id in sorted(int(k) for k in table2001.cell_id_to_name.keys()):
        cell_name = table2001.cell_id_to_name[str(cell_id)]
        if cell_name not in table2011.cell_names:
            print('    <tr class="in-2001-only">')
            print('      <td>-</td>')
            print('      <td>{}</td>'.format(table2001.cell_name_to_id[cell_name]))
            print('      <td>{}</td>'.format(cell_name))
            print('    </tr>')
    print('  </tbody>')
    print('</table>')

def print_tables(table2011, table2001):
    print_table(table2011, table2001)

print('<html>')
print('<head>')
print('<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">')
print('<style>')
print('  .in-both-years {background: #e6ffe6;}')
print('  .in-2011-only {background: #ffebe6;}')
print('  .in-2001-only {background: #e6edff;}')
print('</style>')
print('</head>')
print('<body>')
print('<div class="container">')
print('<h1>A first attempt at matching 2011 tables to 2001 tables</h1>')
print('<p>')
print('This page has a section for each Census 2011 Key Statistics and Quick')
print('Statistics table.  Each section begins with Nomis dataset ID for the')
print('table, and a suggested table from 2001 that contains similar cells.')
print('The HTML table has a green row for each 2011 cell that is also in the')
print('suggested 2001 table, a red row for each 2011 cell that is not in the 2001')
print('table, and a blue row for each cell that is in the 2001 table')
print('but not in the 2011 table.')
print('</p>')
for table2011 in tables[2011].values():
    table_scores = []
    for table2001 in tables[2001].values():
        cell_names_in_common = table2011.cell_names & table2001.cell_names
        # Score is number of 2011 cell names that are in the 2001 tables, with
        # ties broken by preferring small 2001 tables.
        score = len(cell_names_in_common) - len(table2001.cell_names) / 10000000
        table_scores.append((score, table2001))
    table_scores.sort(key=lambda s: s[0], reverse=True)
    best_table = table_scores[0][1]
    #print(table2011.table_name, '///', best_table.table_name)

    print(f'<h3>{table2011.table_name}</h3>')
    print(f'<p><b>Nomis Table ID:</b> {table2011.table_id}</p>')
    print(f'<p><b>Suggested 2001 table:</b> {best_table.table_name}</p>')
    print(f'<p><b>Suggested 2001 table ID:</b> {best_table.table_id}</p>')
    print_tables(table2011, best_table)

print('</div>')
print('<body>')
print('<html>')
