import babel.numbers
import csv
import sys


q2017 = ['2016-2017-Q4', '2017-2018-Q1', '2017-2018-Q2', '2017-2018-Q3']

organizations_over_25k = {}
organizations_under_25k = {}

with open(sys.argv[1], 'r') as contracts_file:
    c_reader = csv.DictReader(contracts_file, dialect='excel')
    row_num = 0
    for c_record in c_reader:
        try:
            if c_record['reporting_period'] in q2017:
                org_id = c_record['owner_org']
                solicit_code = c_record['solicitation_procedure_code']
                current_org = {}

                # retrieve contract values and convert to decimal values

                ov = babel.numbers.parse_decimal(c_record['original_value'].replace('$', ''), locale='en_CA')
                cv = babel.numbers.parse_decimal(c_record['contract_value'].replace('$', ''), locale='en_CA')
                av = babel.numbers.parse_decimal(c_record['amendment_value'].replace('$', ''), locale='en_CA')

                # retrieve the existing organization record or create it if it does not exist

                if ov >= 25000 and org_id in organizations_over_25k and solicit_code in organizations_over_25k[org_id]:
                    current_org = organizations_over_25k[org_id][solicit_code]
                elif ov < 25000 and org_id in organizations_under_25k:
                    current_org = organizations_under_25k[org_id]
                else:
                    current_org = {'department': c_record['owner_org_title'],
                                   'year': 2017,
                                   'contact_count': 0,
                                   'service_original': 0,
                                   'service_amendment': 0,
                                   'service_count': 0,
                                   'goods_original': 0,
                                   'goods_amendment': 0,
                                   'goods_count': 0,
                                   'construction_original': 0,
                                   'construction_amendment': 0,
                                   'construction_count': 0,
                                   }

                is_original = (av == 0)
                if is_original:
                    current_org['contact_count'] += 1
                    if c_record['commodity_type_code'] == 'S':
                        current_org['service_original'] += cv
                        current_org['service_count'] += 1
                    elif c_record['commodity_type_code'] == 'G':
                        current_org['goods_original'] += cv
                        current_org['goods_count'] += 1
                    elif c_record['commodity_type_code'] == 'C':
                        current_org['construction_original'] += cv
                        current_org['construction_count'] += 1
                else:
                    current_org['contact_count'] += 1
                    if c_record['commodity_type_code'] == 'S':
                        current_org['service_amendment'] += av
                    elif c_record['commodity_type_code'] == 'G':
                        current_org['goods_amendment'] += av
                    elif c_record['commodity_type_code'] == 'C':
                        current_org['construction_amendment'] += av

                if ov >= 25000:
                    if org_id not in organizations_over_25k:
                        organizations_over_25k[org_id] = {}
                    organizations_over_25k[org_id][solicit_code] = current_org
                else:
                    organizations_under_25k[org_id] = current_org
                row_num += 1

        except Exception as x:
            sys.stderr.write(repr(x))

print(row_num)
for org in organizations_over_25k:
    for sc in organizations_over_25k[org]:
        print("(Over 25K) Dept. {0}, SC: {4}, Service Count: {3}, Service original: {1}, "
              "Service amendment: {2}".format(org,
                                              organizations_over_25k[org][sc]['service_original'],
                                              organizations_over_25k[org][sc]['service_amendment'],
                                              organizations_over_25k[org][sc]['service_count'],
                                              sc))

for org in organizations_under_25k:
    print("(Under 25K)Dept. {0}, Service Count: {3}, Service original: {1}, "
          "Service amendment: {2}".format(org,
                                          organizations_under_25k[org]['service_original'],
                                          organizations_under_25k[org]['service_amendment'],
                                          organizations_under_25k[org]['service_count']))

with open(sys.argv[2], 'r', encoding='utf-8-sig') as contractsa_file:
    c_reader = csv.DictReader(contractsa_file, dialect='excel')
    row_num = 0
    for c_record in c_reader:
        try:
            if c_record['year'] == '2017':
                org_id = c_record['owner_org']
                if org_id in organizations_under_25k:
                    current_org = organizations_under_25k[org_id]
                else:
                    current_org = {'department': c_record['owner_org_title'],
                                   'year': 2017,
                                   'contact_count': 0,
                                   'service_original': 0,
                                   'service_amendment': 0,
                                   'service_count': 0,
                                   'goods_original': 0,
                                   'goods_amendment': 0,
                                   'goods_count': 0,
                                   'construction_original': 0,
                                   'construction_amendment': 0,
                                   'construction_count': 0,
                                   }
                gvo = babel.numbers.parse_decimal(c_record['contracts_goods_original_value'], locale='en_CA')
                gva = babel.numbers.parse_decimal(c_record['contracts_goods_amendment_value'], locale='en_CA')
                gno = babel.numbers.parse_number(c_record['contract_goods_number_of'], locale='en_CA')
                svo = babel.numbers.parse_decimal(c_record['contracts_service_original_value'], locale='en_CA')
                sva = babel.numbers.parse_decimal(c_record['contracts_service_amendment_value'], locale='en_CA')
                sno = babel.numbers.parse_number(c_record['contract_service_number_of'], locale='en_CA')
                cvo = babel.numbers.parse_decimal(c_record['contracts_construction_original_value'], locale='en_CA')
                cva = babel.numbers.parse_decimal(c_record['contracts_construction_amendment_value'], locale='en_CA')
                cno = babel.numbers.parse_number(c_record['contract_construction_number_of'], locale='en_CA')

                current_org['contact_count'] += (gno + sno + cno)
                current_org['service_original'] += svo
                current_org['service_amendment'] += sva
                current_org['service_count'] += sno
                current_org['goods_original'] += gvo
                current_org['goods_amendment'] += gva
                current_org['goods_count'] += gno
                current_org['construction_original'] += cvo
                current_org['construction_amendment'] += cva
                current_org['construction_count'] += cno
                organizations_under_25k[org_id] = current_org
                row_num += 1

        except Exception as x:

            sys.stderr.write(repr(x))

# Under 25K Contracts

with open('contracts_dv_under_25k.csv', 'w', encoding='utf-8') as outfile:
    field_names = ['year', 'commodity_type_en', 'commodity_type_fr', 'contracts_count', 'original_value',
                   'amendment_value', 'department_en', 'department_fr']
    csv_writer = csv.DictWriter(outfile, fieldnames=field_names, dialect='excel')
    csv_writer.writeheader()

    for org in organizations_under_25k:
        bi_org_title = str(organizations_under_25k[org]['department']).split('|')
        department_en = bi_org_title[0].strip()
        department_fr = bi_org_title[1].strip() if len(bi_org_title) == 2 else department_en
        row_values = {'year': 2017,
                      'commodity_type_en': 'Service',
                      'commodity_type_fr': 'Services',
                      'contracts_count': organizations_under_25k[org]['service_count'],
                      'original_value': organizations_under_25k[org]['service_original'],
                      'amendment_value': organizations_under_25k[org]['service_amendment'],
                      'department_en': department_en,
                      'department_fr': department_fr}
        csv_writer.writerow(row_values)
        row_values = {'year': 2017,
                      'commodity_type_en': 'Good',
                      'commodity_type_fr': 'Biens',
                      'contracts_count': organizations_under_25k[org]['goods_count'],
                      'original_value': organizations_under_25k[org]['goods_original'],
                      'amendment_value': organizations_under_25k[org]['goods_amendment'],
                      'department_en': department_en,
                      'department_fr': department_fr}
        csv_writer.writerow(row_values)
        row_values = {'year': 2017,
                      'commodity_type_en': 'Construction',
                      'commodity_type_fr': 'Construction',
                      'contracts_count': organizations_under_25k[org]['construction_count'],
                      'original_value': organizations_under_25k[org]['construction_original'],
                      'amendment_value': organizations_under_25k[org]['construction_amendment'],
                      'department_en': department_en,
                      'department_fr': department_fr}
        csv_writer.writerow(row_values)

