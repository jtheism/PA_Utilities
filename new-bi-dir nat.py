import openpyxl
import os
from sys import exit
from tkinter.filedialog import askopenfilename, Tk, asksaveasfilename
from tkinter import messagebox
Tk().withdraw()  # Prevents tkinter window from opening


# This only works for panorama, need an excel sheet from regular FW csv export of nat rules and then build
# different set cmds from that


# Determine if this is for Panorama and define the virtual router
is_panorama = input("Is this for Panorama?   y or n\n")
if is_panorama.lower() == "n":
    is_panorama = None
else:
    dev_g = input("Enter Device Group name:\n")

set_cmds_list = []


def import_workbook():
    try:
        wbook = openpyxl.load_workbook(askopenfilename(initialdir=os.path.expanduser("~/Desktop"),
                                                       title="Select Input Excel File"))
        return wbook
    except FileNotFoundError:  # Handles user selecting 'Cancel'
        messagebox.showinfo("Process aborted", "Workbook import cancelled.")
        exit()


def parse_nat_sheet(import_sheet):
    """
    :param import_sheet: worksheet
    :return: dictionary of VPN info
    """
    d = {}
    # index = 1
    for row in import_sheet.iter_rows(min_row=2):
        if is_panorama:
            # print(row[10].value)
            d[row[0].value] = {"rule": row[1].value, "zone": row[5].value, "internal_ip": row[7].value,
                               "public_ip": row[10].value[10:-20]}
        else:
            d[row[0].value] = {"rule": row[1].value, "zone": row[4].value, "internal_ip": row[6].value,
                               "public_ip": row[9].value[10:-20]}
    return d


wb = import_workbook()
nat_sheet = wb.active
nat_d = parse_nat_sheet(nat_sheet)


for r in nat_d:
    if is_panorama:
        set_cmds_list.append(f'set device-group {dev_g} pre-rulebase nat rules "{nat_d[r]["rule"][:55]}-In" from '
                             f'"{nat_d[r]["zone"]}" to "{nat_d[r]["zone"]}" source any destination '
                             f'"{nat_d[r]["public_ip"]}" service any destination-translation translated-address '
                             f'"{nat_d[r]["internal_ip"]}"\n')

        set_cmds_list.append(f'move device-group {dev_g} pre-rulebase nat rules "{nat_d[r]["rule"][:55]}-In" before '
                             f'"{nat_d[r]["rule"]}"\n')
        set_cmds_list.append(f'rename device-group {dev_g} pre-rulebase nat rules "{nat_d[r]["rule"]}" to '
                             f'"{nat_d[r]["rule"][:55]}-Out"\n')
        set_cmds_list.append(f'set device-group {dev_g} pre-rulebase nat rules "{nat_d[r]["rule"][:55]}-Out" '
                             f'source-translation static-ip bi-directional no\n\n')
    else:
        set_cmds_list.append(
            f'set rulebase nat rules "{nat_d[r]["rule"][:55]}-In" from "{nat_d[r]["zone"]}" to '
            f'"{nat_d[r]["zone"]}" source any destination "{nat_d[r]["public_ip"]}" service'
            f' any destination-translation translated-address "{nat_d[r]["internal_ip"]}"\n')

        set_cmds_list.append(
            f'move rulebase nat rules "{nat_d[r]["rule"][:55]}-In" before "{nat_d[r]["rule"]}"\n')
        set_cmds_list.append(
            f'rename rulebase nat rules "{nat_d[r]["rule"]}" to "{nat_d[r]["rule"][:55]}-Out"\n')
        set_cmds_list.append(
            f'set rulebase nat rules "{nat_d[r]["rule"][:55]}-Out" source-translation static-ip '
            f'bi-directional no\n\n')

try:
    temp_out = open(asksaveasfilename(initialdir=os.path.expanduser("~/Desktop"), title="Select Output file",
                                      defaultextension='.txt', filetypes=[('Text File', '.txt')]), "w")
except FileNotFoundError:  # Handles user selecting 'Cancel'
    temp_out = None
    messagebox.showinfo("Process aborted", "PAN CLI Set commands text file not saved.")
    exit()

for each in set_cmds_list:
    temp_out.write(each)

temp_out.close()
messagebox.showinfo("Success", f"PAN CLI Set commands text file saved as: {temp_out.name}.")
