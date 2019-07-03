import requests
import urllib3
from xml.etree import ElementTree
from tkinter.filedialog import asksaveasfilename, askopenfilename, Tk
import os
root = Tk()
root.withdraw()
root.focus_force()

urllib3.disable_warnings()

# xpath_suffix = ''
xml_input = None


tree = ''
print("\nThis script will output CLI set commands to add security-group and logging profiles to Palo Alto firewall "
      "security policies.\n")
while True:
    choice_s = input("Do you want to add SECURITY-GROUP profiles to the policies? (y or n)\n")
    if choice_s not in ["y", "n"]:
        print("Please enter y or n.")
        continue
    else:
        break
while True:
    choice_l = input("Do you want to add LOG-FORWARDING profiles to the policies? (y or n)\n")
    if choice_l not in ["y", "n"]:
        print("Please enter y or n.")
        continue
    else:
        break

sec_set = None
log_set = None


while xml_input not in ["1", "2"]:
    xml_input = input("Select input source:\n\t1: Import .xml config file.   2: Connect to firewall API\n")
    if xml_input == "1":
        tree = ElementTree.parse(askopenfilename(parent=root, initialdir=os.path.expanduser("~/Desktop"),
                                                 title="Select Palo Alto .xml Config File."))
        # tree = ElementTree.parse(input("Enter file path:\n"))
        break
    elif xml_input == "2":
        firewall_ip = input("Enter firewall IP:\n")
        api_key = input("Enter your API key here:\n")
        data = requests.get(f'https://{firewall_ip}/api/?type=config&action=get&key={api_key}&xpath='
                            f'/config/devices/entry[@name=\'localhost.localdomain\']/vsys/entry[@name=\'vsys1\']'
                            f'/rulebase/security', verify=False)
        tree = ElementTree.fromstring(data.content)
        break
    else:
        continue


if choice_s == "y":
    sec_grp_name = input("Enter security profile group name:\n")
    sec_set = []

    # for child in tree.iter('entry'):  # This is where we get the root of each node for the individual rules.
    #     sec_set.append(child.attrib["name"])
    for elem in tree.iter(tag="security"):
        for rules in elem:
            for entry in rules:
                sec_set.append(entry.attrib["name"])
                print(entry.attrib["name"])
if choice_l == "y":
    logging_name = input("Enter log forwarding group name:\n")
    log_set = []
    # for child in tree.iter('entry'):  # This is where we get the root of each node for the individual rules.
    #     log_set.append(child.attrib["name"])

    for elem in tree.iter(tag="security"):
        for rules in elem:
            for entry in rules:
                log_set.append(entry.attrib["name"])
                # print(entry.attrib["name"])

# print("\nset cli scripting-mode on\nconfigure")
set_cmds = ["\nset cli scripting-mode on\n\nconfigure\n\n"]
if sec_set:
    for name in sec_set:
        # print(f'set rulebase security rules "{name}" profile-setting group "{sec_grp_name}"')
        set_cmds.append(f'set rulebase security rules "{name}" profile-setting group "{sec_grp_name}"\n')
if log_set:
    for name in log_set:
        # print(f'set rulebase security rules "{name}" log-setting "{logging_name}"')
        set_cmds.append(f'set rulebase security rules "{name}" log-setting "{logging_name}"\n')
try:
    with open(asksaveasfilename(initialdir=os.path.expanduser("~/Desktop"),
                                title="Create set command output file:", defaultextension='.txt',
                                filetypes=[('Text File', '.txt')]), "w+") as output:
        for cmd in set_cmds:
            output.write(cmd)
except FileNotFoundError:
    print("Process cancelled.")
    exit()
