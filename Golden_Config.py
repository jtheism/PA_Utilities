from sys import exit
import os
from tkinter.filedialog import Tk, asksaveasfilename
from tkinter import messagebox
Tk().withdraw()  # Prevents tkinter window from opening

models = {1: ["PA-220", 2100, 3990], 2: ["PA-820", 4150, 7885], 3: ["PA-850", 6500, 12350],
          4: ["PA-3220", 28500, 54150], 5: ["PA-3250", 42000, 79800], 6: ["PA-3260", 59000, 112100],
          7: ["PA-5220", 66500, 126350], 8: ["PA-5250", 142000, 269800], 9: ["PA-5260", 195000, 370500],
          10: ["PA-5280", 195000, 370500], 11: ["PA-7050", 1450000, 2755000], 12: ["PA-7080", 2400000, 4560000],
          13: ["VM-50", 1500, 2850], 14: ["VM-100", 7500, 14250], 15: ["VM-200", 7500, 14250],
          16: ["VM-300", 15000, 28500], 17: ["VM-500", 30000, 57000], 18: ["VM-700", 60000, 114000],
          19: ["VM-1000-HV", 15000, 28500]
          }


text_list = ["set deviceconfig", "set mgt-config", "set network profiles", "set zone", "set tag", "set profiles",
             "set profile-group", "set shared log-settings profiles",
             "set user-id-collector setting ip-user-mapping-timeout 240", "set external-list", "set address",
             "set application-group", "set rulebase default-security-rules rules", "set rulebase security rules"]

cmds_list = []
pano_cmds = []

panos_ver = None
while panos_ver not in ["1", "2"]:
    panos_ver = input("Select which PAN-OS version:\n\t1. 9.0\n\t2. 9.1\n")

u_zone = input(f'Enter desired outside zone name:\n')
t_zone = input(f'Enter desired inside zone name:\n')

if panos_ver == "1":
    with open("V9.0-GoldCfgSetCmds", "r") as cmds_file:
        for line in cmds_file:
            if "**Untrust" in line:
                cmds_list.append(line.replace("**Untrust", u_zone))
            elif "**Trust" in line:
                cmds_list.append(line.replace("**Trust", t_zone))
            else:
                cmds_list.append(line)


elif panos_ver == "2":
    with open("V9.1-GoldCfgSetCmds", "r") as cmds_file:
        for line in cmds_file:
            if "**Untrust" in line:
                cmds_list.append(line.replace("**Untrust", u_zone))
            elif "**Trust" in line:
                cmds_list.append(line.replace("**Trust", t_zone))
            else:
                cmds_list.append(line)


is_panorama = input("Is this for Panorama? (y or n)\n").lower()
# print(is_panorama)


if is_panorama == "y":
    template_name = input("Enter Template name:\n")
    devicegroup_name = input("Enter Device Group name:\n")
    with open("GoldCfgPanoCmds", "r") as pcmds_file:
        for line in pcmds_file:
            if "*template" in line:
                pano_cmds.append(line.replace("*template", template_name))
            elif "*devgrp" in line:
                pano_cmds.append(line.replace("*devgrp", devicegroup_name))
            else:
                pano_cmds.append(line)


while True:
    try:
        is_model = int(input("Model?\n\n1: PA-220    2: PA-820    3: PA-850\n4: PA-3220   5: PA-3250   6: PA-3260\n"
                             "7: PA-5220   8: PA-5250   9: PA-5260   10: PA-5280   11: PA-7050   12: PA-7080\n"
                             "13: VM-50   14: VM-100   15: VM-200   16: VM-300   17: VM-500   "
                             "18: VM-700   19: VM-1000HV\n"))
        break
    except ValueError:
        continue

cmds_out = [line.replace("alarm-rate a_a_rate activate-rate a_a_rate maximal-rate m_rate",
                         "alarm-rate " + str(models[is_model][1]) + " activate-rate " + str(models[is_model][1]) +
                         " maximal-rate " + str(models[is_model][2])) for line in cmds_list]


if is_panorama == "y":
    # swaps out syntax where needed for panorama commands
    pano_dict = {"set deviceconfig": f"set template {template_name} config deviceconfig",
                 "set mgt-config": f"set template {template_name} config mgt-config",
                 "set network profiles": f"set template {template_name} config network profiles",
                 "set zone": f"set template {template_name} config vsys vsys1 zone", "set tag": "set shared tag",
                 "set profiles": f"set shared profiles", "set profile-group": "set shared profile-group",
                 "set shared log-settings profiles": f"set shared log-settings profiles",
                 "set user-id-collector setting ip-user-mapping-timeout 240":
                     f"set template {template_name} config vsys vsys1 user-id-collector setting "
                     f"ip-user-mapping-timeout 240",
                 "set external-list": "set shared external-list", "set address": "set shared address",
                 "set application-group": "set shared application-group",
                 "set rulebase default-security-rules rules": f"set device-group {devicegroup_name} post-rulebase "
                                                              "default-security-rules rules",
                 "set rulebase security rules": f"set device-group {devicegroup_name} pre-rulebase security rules"}
    for line in cmds_out:
        # print(line)
        for text in text_list:
            if text in line:
                pano_cmds.append(line.replace(text, pano_dict[text]))
    try:
        temp_out = open(asksaveasfilename(initialdir=os.path.expanduser("~/Desktop"), title="Select Output file",
                                          defaultextension='.txt', filetypes=[('Text File', '.txt')]), "w+")
    except FileNotFoundError:  # Handles user selecting 'Cancel'
        temp_out = None
        messagebox.showinfo("Process aborted", "Panorama CLI Set commands text file not saved.")
        exit()
    for pk in pano_cmds:
        temp_out.write(pk)

    temp_out.close()
    messagebox.showinfo("Success", f"Panorama CLI Set commands text file saved as: {temp_out.name}.")
else:
    try:
        temp_out = open(asksaveasfilename(initialdir=os.path.expanduser("~/Desktop"), title="Select Output file",
                                          defaultextension='.txt', filetypes=[('Text File', '.txt')]), "w+")
    except FileNotFoundError:  # Handles user selecting 'Cancel'
        temp_out = None
        messagebox.showinfo("Process aborted", "PA Firewall CLI Set commands text file not saved.")
        exit()
    for k in cmds_out:
        temp_out.write(k)
    temp_out.close()
    messagebox.showinfo("Success", f"{models[is_model][0]} CLI Set commands text file saved as: {temp_out.name}.")
