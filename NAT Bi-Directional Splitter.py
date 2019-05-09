from xml.etree import ElementTree as Elem
import os.path
from tkinter.filedialog import askopenfilename, asksaveasfilename, Tk
window = Tk()
window.withdraw()
window.focus_force()


tree = Elem.parse(askopenfilename(initialdir=os.path.expanduser("~/Desktop"),
                                  title="Select Palo Alto xml configuration file."))
# root_tree = tree.getroot()

nat_dict = {}
nat_policy_count = 0
for elem in tree.iter(tag="nat"):
    for rules in elem:
        for entry in rules:
            nat_policy_count += 1
            rule_dic = {"bi_d": 'no'}
            # print(entry.tag, entry.attrib)
            nat_dict[entry.attrib["name"]] = rule_dic

            for member in entry.find("source"):
                nat_dict[entry.attrib["name"]]["source"] = member.text
                # print(member.text)

            for member in entry.find("destination"):
                nat_dict[entry.attrib["name"]]["destination"] = member.text
                # print(member.text)

            for member in entry.find("from"):
                nat_dict[entry.attrib["name"]]["from"] = member.text
                # print(member.text)

            for member in entry.find("to"):
                nat_dict[entry.attrib["name"]]["to"] = member.text
                # print(member.text)

            try:
                for static in entry.find("source-translation"):
                    if static.tag == "static-ip":
                        nat_dict[entry.attrib["name"]]["translated"] = static.find("translated-address").text
                        # print(nat_dict[entry.attrib["name"]]["translated"])
                        print(f'{nat_policy_count}')
                        nat_dict[entry.attrib["name"]]["bi_d"] = static.find("bi-directional").text
                        # print(nat_dict[entry.attrib["name"]]["bi_d"])
            except (TypeError, AttributeError):
                continue

# print(nat_dict)
# for rul in nat_dict:
#     print(rul, nat_dict[rul])

set_cmds_list = ["set cli scripting-mode on\n", "configure\n\n"]

bi_dir_nat_count = 0
for rule in nat_dict:
    if nat_dict[rule]["bi_d"] == "yes":
        bi_dir_nat_count += 1

        set_cmds_list.append(f'set rulebase nat rules "{rule[:55]}-In" from "{nat_dict[rule]["to"]}" to '
                             f'"{nat_dict[rule]["to"]}" source any destination "{nat_dict[rule]["translated"]}" service'
                             f' any destination-translation translated-address "{nat_dict[rule]["source"]}"\n')
        set_cmds_list.append(f'move rulebase nat rules "{rule[:55]}-In" before "{rule}"\n')
        set_cmds_list.append(f'rename rulebase nat rules "{rule}" to "{rule[:55]}-Out"\n\n')


print(f'\nTotal NAT policies processed: {nat_policy_count}.')
print(f'Bi-directional NAT policies split: {bi_dir_nat_count}.\n')

try:
    with open(asksaveasfilename(parent=window, initialdir=os.path.expanduser("~/Desktop"),
                                title="Create set command output file:", defaultextension='.txt',
                                filetypes=[('Text File', '.txt')]), "w+") as output:
        for cmd in set_cmds_list:
            output.write(cmd)
except FileNotFoundError:
    print("Process cancelled.")
    exit()

# for cmd in set_cmds_list:
#     print(cmd)
