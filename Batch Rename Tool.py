# Need to test NAT section


import os
from datetime import datetime
import requests
import urllib3
from xml.etree import ElementTree

urllib3.disable_warnings()

addresses = {}
address_groups = {}
services = {}
service_groups = {}
sec_policies = {}
nat_policies = {}
logs = []
sp_memo = ''
tree = ''

c_types = {1: ["addresses",
               "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/address"],
           2: ["addr_grps",
               "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/address-group"],
           3: ["services",
               "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/service"],
           4: ["service_grps",
               "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/service-group"],
           5: ["sec_pols",
               "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/rulebase/security"],
           6: ["nat_pols",
               "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/rulebase/nat"]}

api_key = input("Enter your API key here:\n")
firewall_ip = input("Enter firewall Management IP:\n")


change_type = int(input("Enter the number of what you would like to rename.\n1. Addresses  2. Address Groups  "
                        "3. Services  4. Service Groups 5. Security Policies  6. NAT Policies\n"))

xpath = f'{c_types[change_type][1]}'

if change_type == 5:
    sp_memo = int(input("Select mode.\n1: Basic\n2: Verbose\n\tBasic gives policy name only. "
                        "Verbose mode gives full details of each policy.\n"))
chosen_c_type = f'{c_types[change_type][0]}'
xpath_suffix = ''
xml_input = 0


while xml_input not in ["1", "2"]:
    xml_input = input("Select input source:\n\t1: File path   2: Connect to firewall API\n")
    if xml_input == "1":
        tree = ElementTree.parse(input("Enter file path:\n"))
        break
    elif xml_input == "2":
        data = requests.get(f'https://{firewall_ip}/api/?type=config&action=get&key={api_key}&xpath={xpath}',
                            verify=False)

        tree = ElementTree.fromstring(data.content)
        break
    else:
        continue
# data = requests.get(input("Paste URL to XPath:\n"), verify=False)  # Probably not using this


if chosen_c_type == 'addresses':
    for child in tree.iter('entry'):
        addresses[child.attrib['name']] = [child.attrib['name'], child[0].text, ""]
        # print(child[0].text)
    # print(addresses, '\n')

    for addy in addresses:
        print(f'Current Name: {addy} IP: {addresses[addy][1]}')
        new_name = input("Enter new address name. Enter with no input to skip.\n")
        addresses[addy][2] = new_name

    # print(addresses, '\n\n')

    for address in addresses:
        if addresses[address][2]:
            # print(f'Object "{address}" >>> Changing name to "{addresses[address][2]}"')
            logs.append(f'Object "{address}" >>> Changing name to "{addresses[address][2]}"\n')
        else:
            # print(f'Object: "{address}" >>> Name unchanged.')
            logs.append(f'Object: "{address}" >>> Name unchanged.\n')

    for address in addresses:
        if addresses[address][2]:
            print(f'rename address "{address}" to "{addresses[address][2]}"')


elif chosen_c_type == 'addr_grps':
    for child in tree.iter('entry'):
        address_groups[child.attrib['name']] = [child.attrib['name'], ""]
        # print(child[0].text)
    # print(address_groups, '\n')

    for ag in address_groups:
        print(f'Current Name: {ag}')
        new_name = input("Enter new address group name. Enter with no input to skip.\n")
        address_groups[ag][1] = new_name

    # print(address_groups, '\n\n')

    for ag in address_groups:
        if address_groups[ag][1]:
            # print(f'Object "{ag}" >>> Changing name to "{address_groups[ag][1]}"')
            logs.append(f'Object "{ag}" >>> Changing name to "{address_groups[ag][1]}"\n')
        else:
            # print(f'Object: "{ag}" >>> Name unchanged.')
            logs.append(f'Object: "{ag}" >>> Name unchanged.\n')

    for ag in address_groups:
        if address_groups[ag][1]:
            print(f'rename address group "{ag}" to "{address_groups[ag][1]}"')


if chosen_c_type == 'services':
    for child in tree.iter('entry'):
        services[child.attrib['name']] = [child.attrib['name'], ""]
        # print(child[0].text)
    # print(services, '\n')

    for svc in services:
        print(f'Current Name: {svc} IP: {services[svc][1]}')
        new_name = input("Enter new address name. Enter with no input to skip.\n")
        services[svc][1] = new_name

    # print(services, '\n\n')

    for svc in services:
        if services[svc][1]:
            # print(f'Object "{svc}" >>> Changing name to "{services[svc][1]}"')
            logs.append(f'Object "{svc}" >>> Changing name to "{services[svc][1]}"\n')
        else:
            # print(f'Object: "{svc}" >>> Name unchanged.')
            logs.append(f'Object: "{svc}" >>> Name unchanged.\n')

    for svc in services:
        if services[svc][1]:
            print(f'rename service "{svc}" to "{services[svc][1]}"')


elif chosen_c_type == 'service_grps':
    for child in tree.iter('entry'):
        service_groups[child.attrib['name']] = [child.attrib['name'], ""]
        # print(child[0].text)
    # print(service_groups, '\n')

    for sg in service_groups:
        print(f'Current Name: {sg}')
        new_name = input("Enter new service group name. Enter with no input to skip.\n")
        service_groups[sg][1] = new_name

    # print(service_groups, '\n\n')

    for sg in service_groups:
        if service_groups[sg][1]:
            # print(f'Object "{sg}" >>> Changing name to "{service_groups[sg][1]}"')
            logs.append(f'Object "{sg}" >>> Changing name to "{service_groups[sg][1]}"\n')
        else:
            # print(f'Object: "{sg}" >>> Name unchanged.')
            logs.append(f'Object: "{sg}" >>> Name unchanged.\n')

    for sg in service_groups:
        if service_groups[sg][1]:
            print(f'rename service group "{sg}" to "{service_groups[sg][1]}"')


elif chosen_c_type == 'sec_pols':
    for child in tree.iter('entry'):  # This is where we get the root of each node for the individual rules.
        cur_rulename = child.attrib["name"]
        if sp_memo == 2:  # Basic or verbose mode check
            sec_policies[child.attrib['name']] = {"name": child.attrib['name'], "new_name": "", "from": [],
                                                  "to": [], "sources": [], "destinations": [], "apps": [],
                                                  "services": []}

            for members in (child.iter('from')):
                for each in members:
                    sec_policies[child.attrib['name']]["from"].append(each.text)
            # print(sec_policies[cur_rulename]["from"])

            for members in (child.iter('to')):
                for each in members:
                    sec_policies[child.attrib['name']]["to"].append(each.text)
            # print(sec_policies[cur_rulename]["to"])

            for members in (child.iter('source')):
                for each in members:
                    sec_policies[child.attrib['name']]["sources"].append(each.text)
            # print(sec_policies[cur_rulename]["sources"])

            for add in (child.iter('destination')):
                for each in add:
                    sec_policies[child.attrib['name']]["destinations"].append(each.text)
            # print(sec_policies[cur_rulename]["destinations"])

            for members in (child.iter('application')):
                for each in members:
                    sec_policies[child.attrib['name']]["apps"].append(each.text)
            # print(sec_policies[cur_rulename]["apps"])

            for members in (child.iter('service')):
                for each in members:
                    sec_policies[child.attrib['name']]["services"].append(each.text)
        else:
            sec_policies[child.attrib['name']] = {"name": child.attrib['name'], "new_name": ""}

        # print(child[0][0].text)
        # print(child[0].text)

    # print("Rule names:")
    # for pol in sec_policies:
    #     print(f'\t{pol}')
    # print("<<End of Rules>>\n\n")
    for sp in sec_policies:
        print(f'Current Rule Name: {sp}\nFrom Zone(s): {sec_policies[sp]["from"]}  >>  To Zone(s): '
              f'{sec_policies[sp]["to"]}\n"Source(s): {sec_policies[sp]["sources"]}  >>  Destination(s): '
              f'{sec_policies[sp]["destinations"]}\nApplications: {sec_policies[sp]["apps"]}    Services: '
              f'{sec_policies[sp]["services"]}')
        new_name = input("Enter new security rule name. Enter with no input to skip.\n")
        sec_policies[sp]["new_name"] = new_name

    # print(sec_policies, '\n\n')

    for sp in sec_policies:
        if sec_policies[sp]["new_name"]:
            # print(f'Rule name "{sp}" >>> Changing name to "{sec_policies[sp][1]}"')
            logs.append(f'Rule name "{sp}" >>> Changing name to "{sec_policies[sp][1]}"\n')
        else:
            # print(f'Rule name: "{sp}" >>> Name unchanged.')
            logs.append(f'Rule name: "{sp}" >>> Name unchanged.\n')
    print("\nSet commands. Paste into CLI.\n\nset cli scripting-mode on\nconfigure")
    for sp in sec_policies:
        if sec_policies[sp]["new_name"]:
            print(f'rename rulebase security rules "{sp}" to "{sec_policies[sp][1]}"')


if chosen_c_type == 'nat_pols':  # Test this
    for child in tree.iter('entry'):
        nat_policies[child.attrib['name']] = [child.attrib['name'], child[0].text, ""]
        # print(child[0].text)
    # print(nat_policies, '\n')

    for np in nat_policies:
        print(f'Current Name: {np}')
        new_name = input("Enter new NAT rule name. Enter with no input to skip.\n")
        nat_policies[np][1] = new_name

    # print(nat_policies, '\n\n')

    for np in nat_policies:
        if nat_policies[np][1]:
            # print(f'Object "{np}" >>> Changing name to "{nat_policies[np][1]}"')
            logs.append(f'Rule name "{np}" >>> Changing name to "{nat_policies[np][1]}"\n')
        else:
            # print(f'Object: "{np}" >>> Name unchanged.')
            logs.append(f'Rule name: "{np}" >>> Name unchanged.\n')

    for np in nat_policies:
        if nat_policies[np][1]:
            print(f'rename np "{np}" to "{nat_policies[np][1]}"')


home_path = os.path.expanduser("~\Desktop")
# print(home_path)

with open(f'{home_path}\\rename_changelog.txt', 'w+') as file:
    file.write(f'Name change script generator run on: {datetime.now()}\n')
    file.write(f'{chosen_c_type} names changed...\n\n')
    file.write("\n")
    for line in logs:
        file.write(line)
print(f'\n\nLog file written to: {home_path}\\rename_changelog.txt')
