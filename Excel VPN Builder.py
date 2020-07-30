import openpyxl
import os
from sys import exit
from tkinter.filedialog import askopenfilename, Tk, asksaveasfilename
from tkinter import messagebox
Tk().withdraw()  # Prevents tkinter window from opening


def import_workbook():
    try:
        wb = openpyxl.load_workbook(askopenfilename(initialdir=os.path.expanduser("~/Desktop"),
                                                    title="Select Input Excel File"))
        return wb
    except FileNotFoundError:  # Handles user selecting 'Cancel'
        messagebox.showinfo("Process aborted", "Workbook import cancelled.")
        exit()


def first_steps():
    # Determine if this is for Panorama and define the virtual router
    is_panorama = input("Is this for Panorama?   y or n\n")
    if is_panorama == "n":
        is_panorama = None
    else:
        is_panorama = "y"
    temp = None
    dev_g = None
    if is_panorama == "y":
        temp = input("Enter Template name:\n")
        dev_g = input("Enter Device Group name:\n")
    vr = input("Enter virtual router name:\n")
    return vr, is_panorama, temp, dev_g


def parse_vpn_sheet(import_sheet):
    """
    :param import_sheet: worksheet
    :return: dictionary of VPN info
    """
    d = {}
    # index = 1
    for row in import_sheet.iter_rows(min_row=2):
        d[row[0].value] = {"name": row[1].value, "tunnel_num": row[2].value, "gtwy_intf": row[3].value,
                           "loc_gtwy_ip": row[4].value, "peer_gtwy_ip": row[5].value, "ike_ver": row[6].value,
                           "ike_exch_mode": row[7].value, "ike_loc_id": row[8].value, "loc_id_type": row[9].value,
                           "ike_remote_id": row[10].value, "remote_id_type": row[11].value, "p1_enc": row[12].value,
                           "p1_auth": row[13].value, "p1_dh": row[14].value, "p1_lifetime": row[15].value,
                           "p1_life_units": row[16].value, "p2_enc": row[17].value, "p2_auth": row[18].value,
                           "p2_dh": row[19].value, "p2_lifetime": row[20].value, "p2_life_units": row[21].value,
                           "psk": row[22].value, "nat_t": row[23].value, "proxy_id_needed": row[24].value,
                           "local_nets": row[25].value.split(","), "remote_nets": row[26].value.split(","),
                           "int_zone": row[27].value, "vpn_zone": row[28].value, "tun_ip": row[29].value}

        # P1 substitutes for 'multi'
        if d[row[0].value]["p1_enc"] == "multi":
            d[row[0].value]["p1_enc"] = "[ 3des aes-128-cbc aes-192-cbc aes-256-cbc ]"
        if d[row[0].value]["p1_auth"] == "multi":
            d[row[0].value]["p1_auth"] = "[ sha1 sha256 sha384 sha512 ]"
        if d[row[0].value]["p1_dh"] == "multi":
            d[row[0].value]["p1_dh"] = "[  group2 group5 group14 group19 group20 ]"

        # P2 substitutes for 'multi'
        if d[row[0].value]["p2_enc"] == "multi":
            d[row[0].value]["p2_enc"] = "[ 3des aes-128-cbc aes-192-cbc aes-256-cbc aes-128-gcm aes-256-gcm ]"
        if d[row[0].value]["p2_auth"] == "multi":
            d[row[0].value]["p2_auth"] = "[ sha1 sha256 sha384 sha512 ]"

    return d


vpn_wb = import_workbook()
working_sheet = vpn_wb["VPN_INFO"]
vpn_dict = parse_vpn_sheet(working_sheet)
vrouter, is_pano, template, dev_grp = first_steps()
output_list = []

# vpn_dict[key]
for key in vpn_dict:
    # P1 Crypto Output
    if is_pano:
        output_list.append(f'set template \"{template}\"config network ike crypto-profiles ike-crypto-profiles '
                           f'P1_{vpn_dict[key]["name"]} hash {vpn_dict[key]["p1_auth"]}\n'
                           f'set template \"{template}\"config network ike crypto-profiles ike-crypto-profiles '
                           f'P1_{vpn_dict[key]["name"]} dh-group {vpn_dict[key]["p1_dh"]}\n'
                           f'set template \"{template}\"config network ike crypto-profiles ike-crypto-profiles '
                           f'P1_{vpn_dict[key]["name"]} encryption {vpn_dict[key]["p1_enc"]}\n'
                           f'set template \"{template}\"config network ike crypto-profiles ike-crypto-profiles '
                           f'P1_{vpn_dict[key]["name"]} lifetime {vpn_dict[key]["p1_life_units"]} '
                           f'{vpn_dict[key]["p1_lifetime"]}\n')
    else:
        output_list.append(f'set network ike crypto-profiles ike-crypto-profiles P1_{vpn_dict[key]["name"]} '
                           f'hash {vpn_dict[key]["p1_auth"]}\n'
                           f'set network ike crypto-profiles ike-crypto-profiles P1_{vpn_dict[key]["name"]} '
                           f'dh-group {vpn_dict[key]["p1_dh"]}\n'
                           f'set network ike crypto-profiles ike-crypto-profiles P1_{vpn_dict[key]["name"]} '
                           f'encryption {vpn_dict[key]["p1_enc"]}\n'
                           f'set network ike crypto-profiles ike-crypto-profiles P1_{vpn_dict[key]["name"]} '
                           f'lifetime {vpn_dict[key]["p1_life_units"]} '
                           f'{vpn_dict[key]["p1_lifetime"]}\n')
   
    # P2 Crypto Output
    if is_pano:
        output_list.append(f'set template \"{template}\" config network ike crypto-profiles '
                           f'ipsec-crypto-profiles P2_{vpn_dict[key]["name"]} esp authentication '
                           f'{vpn_dict[key]["p2_auth"]} encryption {vpn_dict[key]["p2_enc"]}\n')
        output_list.append(f'set template \"{template}\" config network ike crypto-profiles '
                           f'ipsec-crypto-profiles P2_{vpn_dict[key]["name"]} dh-group {vpn_dict[key]["p2_dh"]} '
                           f'lifetime {vpn_dict[key]["p2_life_units"]} {vpn_dict[key]["p2_lifetime"]}\n')
    else:
        output_list.append(f'set network ike crypto-profiles ipsec-crypto-profiles P2_{vpn_dict[key]["name"]} '
                           f'esp authentication {vpn_dict[key]["p2_auth"]} encryption {vpn_dict[key]["p2_enc"]}\n')
        output_list.append(f'set network ike crypto-profiles ipsec-crypto-profiles P2_{vpn_dict[key]["name"]} '
                           f'dh-group {vpn_dict[key]["p2_dh"]} lifetime {vpn_dict[key]["p2_life_units"]} '
                           f'{vpn_dict[key]["p2_lifetime"]}\n')

    # Zone and Tunnel Interface Output
    if is_pano:
        output_list.append(f'set template \"{template}\" config network interface tunnel units '
                           f'tunnel.{vpn_dict[key]["tunnel_num"]} comment {vpn_dict[key]["name"]}\n')
        if vpn_dict[key]["tun_ip"]:
            output_list.append(f'set template \"{template}\" config network interface tunnel units '
                               f'tunnel.{vpn_dict[key]["tunnel_num"]} ip {vpn_dict[key]["tun_ip"]}\n')
        output_list.append(f'set template \"{template}\" config vsys vsys1 import network interface '
                           f'tunnel.{vpn_dict[key]["tunnel_num"]}\n')
        output_list.append(f'set template \"{template}\" config vsys vsys1 zone "{vpn_dict[key]["vpn_zone"]}" '
                           f'network enable-packet-buffer-protection yes layer3 tunnel.{vpn_dict[key]["tunnel_num"]}\n')
        output_list.append(f'set template \"{template}\" config network virtual-router \"{vrouter}\" '
                           f'interface tunnel.{vpn_dict[key]["tunnel_num"]}\n')

    else:
        output_list.append(f'set zone "{vpn_dict[key]["vpn_zone"]}" network layer3 [ ]\n')
        output_list.append(f'set network interface tunnel units tunnel.{vpn_dict[key]["tunnel_num"]} comment '
                           f'{vpn_dict[key]["name"]}\n')
        output_list.append(f'set zone "{vpn_dict[key]["vpn_zone"]}" network enable-packet-buffer-protection yes layer3 '
                           f'tunnel.{vpn_dict[key]["tunnel_num"]}\n')
        output_list.append(f'set network virtual-router "{vrouter}" interface tunnel.{vpn_dict[key]["tunnel_num"]}\n')
    if vpn_dict[key]["tun_ip"]:
        output_list.append(f'set network interface tunnel units tunnel.{vpn_dict[key]["tunnel_num"]} '
                           f'ip {vpn_dict[key]["tun_ip"]}\n')

    # IKE Gateway Output
    if is_pano == "y":
        # PSK
        output_list.append(f'set template \"{template}\" config network ike gateway {vpn_dict[key]["name"]} '
                           f'authentication pre-shared-key key {vpn_dict[key]["psk"]}\n')
    
        # Local gateway interface and IP
        output_list.append(f'set template \"{template}\" config network ike gateway {vpn_dict[key]["name"]} '
                           f'local-address interface {vpn_dict[key]["gtwy_intf"]} ip {vpn_dict[key]["loc_gtwy_ip"]}\n')
    
        # Peer gateway IP
        output_list.append(f'set template \"{template}\" config network ike gateway {vpn_dict[key]["name"]} '
                           f'peer-address ip {vpn_dict[key]["peer_gtwy_ip"]}\n')
    
        # NAT-T
        if vpn_dict[key]["nat_t"]:
            output_list.append(f'set template \"{template}\" config network ike gateway {vpn_dict[key]["name"]} '
                               f'protocol-common nat-traversal enable yes\n')
    
        # Set local and peer IDs if being used
        if vpn_dict[key]["ike_loc_id"]:
            output_list.append(f'set template \"{template}\" config network ike gateway {vpn_dict[key]["name"]} '
                               f'local-id type {vpn_dict[key]["loc_id_type"]} id {vpn_dict[key]["ike_loc_id"]}\n')
        if vpn_dict[key]["ike_remote_id"]:
            output_list.append(f'set template \"{template}\" config network ike gateway {vpn_dict[key]["name"]} '
                               f'peer-id type {vpn_dict[key]["remote_id_type"]} id {vpn_dict[key]["ike_remote_id"]}\n')
    
        # IKEv1 specific
        if vpn_dict[key]["ike_ver"] == "ikev1":
            # ikev1 exchange and crypto
            output_list.append(f'set template \"{template}\" config network ike gateway {vpn_dict[key]["name"]} '
                               f'protocol version ikev1 ikev1 exchange-mode {vpn_dict[key]["ike_exch_mode"]} '
                               f'ike-crypto-profile P1_{vpn_dict[key]["name"]} dpd enable yes\n')
                               # f' interval {dpd_int} retry {dpd_retry}\n\n')
                               
        # IKEv2 specific
        else:
            output_list.append(f'set template \"{template}\" config network ike gateway {vpn_dict[key]["name"]} '
                               f'protocol version ikev2 ikev2 ike-crypto-profile P1_{vpn_dict[key]["name"]} dpd '
                               f'enable yes\n\n')
                               # f'interval {ikev2_liveness}\n')
    else:
        # PSK
        output_list.append(f'set network ike gateway {vpn_dict[key]["name"]} authentication pre-shared-key '
                           f'key {vpn_dict[key]["psk"]}\n')
    
        # Local gateway interface and IP
        output_list.append(f'set network ike gateway {vpn_dict[key]["name"]} local-address interface '
                           f'{vpn_dict[key]["gtwy_intf"]} ip {vpn_dict[key]["loc_gtwy_ip"]}\n')
    
        # Peer gateway IP
        output_list.append(f'set network ike gateway {vpn_dict[key]["name"]} peer-address ip '
                           f'{vpn_dict[key]["peer_gtwy_ip"]}\n')
    
        # NAT-T
        if vpn_dict[key]["nat_t"]:
            output_list.append(f'set network ike gateway {vpn_dict[key]["name"]} protocol-common nat-traversal '
                               f'enable yes\n')
    
        # Set local and peer IDs if being used
        if vpn_dict[key]["ike_loc_id"]:
            output_list.append(f'set network ike gateway {vpn_dict[key]["name"]} local-id type '
                               f'{vpn_dict[key]["loc_id_type"]} id {vpn_dict[key]["ike_loc_id"]}\n')
        if vpn_dict[key]["ike_remote_id"]:
            output_list.append(f'set network ike gateway {vpn_dict[key]["name"]} peer-id type '
                               f'{vpn_dict[key]["remote_id_type"]} id {vpn_dict[key]["ike_remote_id"]}\n')
    
        # IKEv1 specific
        if vpn_dict[key]["ike_ver"] == "ikev1":
            # ikev1 exchange and crypto
            output_list.append(f'set network ike gateway {vpn_dict[key]["name"]} protocol version ikev1 ikev1 '
                               f'exchange-mode {vpn_dict[key]["ike_exch_mode"]} ike-crypto-profile '
                               f'P1_{vpn_dict[key]["name"]} dpd enable yes\n')
                               # interval {dpd_int} retry {dpd_retry}\n\n')
    
        # IKEv2 specific
        else:
            output_list.append(f'set network ike gateway {vpn_dict[key]["name"]} protocol version ikev2 ikev2 '
                               f'ike-crypto-profile P1_{vpn_dict[key]["name"]} dpd enable yes\n')
                               # interval {ikev2_liveness}\n\n')

    # IPSEC Tunnel Output
    if is_pano:
        output_list.append(f'set template \"{template}\" config network tunnel ipsec {vpn_dict[key]["name"]} auto-key '
                           f'ike-gateway {vpn_dict[key]["name"]}\n')
        output_list.append(f'set template \"{template}\" config network tunnel ipsec {vpn_dict[key]["name"]} auto-key '
                           f'ipsec-crypto-profile P2_{vpn_dict[key]["name"]}\n')
        output_list.append(f'set template \"{template}\" config network tunnel ipsec {vpn_dict[key]["name"]} '
                           f'tunnel-monitor enable no\n')
        output_list.append(f'set template \"{template}\" config network tunnel ipsec {vpn_dict[key]["name"]} '
                           f'tunnel-interface tunnel.{vpn_dict[key]["tunnel_num"]}\n')
        output_list.append(f'set template \"{template}\" config network tunnel ipsec {vpn_dict[key]["name"]} '
                           f'disabled no\n')
        output_list.append(f'set template \"{template}\" config network tunnel ipsec {vpn_dict[key]["name"]} '
                           f'copy-tos yes\n')
    else:
        output_list.append(f'set network tunnel ipsec {vpn_dict[key]["name"]} auto-key ike-gateway '
                           f'{vpn_dict[key]["name"]}\n')
        output_list.append(f'set network tunnel ipsec {vpn_dict[key]["name"]} auto-key ipsec-crypto-profile '
                           f'P2_{vpn_dict[key]["name"]}\n')
        output_list.append(f'set network tunnel ipsec {vpn_dict[key]["name"]} tunnel-monitor enable no\n')
        output_list.append(f'set network tunnel ipsec {vpn_dict[key]["name"]} tunnel-interface '
                           f'tunnel.{vpn_dict[key]["tunnel_num"]}\n')
        output_list.append(f'set network tunnel ipsec {vpn_dict[key]["name"]} disabled no\n')
        output_list.append(f'set network tunnel ipsec {vpn_dict[key]["name"]} copy-tos yes\n')

    # Proxy-ID Output
    if vpn_dict[key]["proxy_id_needed"]:
        p_num = 1
        for lnet in vpn_dict[key]["local_nets"]:
            for rnet in vpn_dict[key]["remote_nets"]:
                if is_pano:
                    output_list.append(
                        f'set template \"{template}\" config network tunnel ipsec \"{vpn_dict[key]["name"]}\" '
                        f'auto-key proxy-id p{p_num} local {lnet} remote {rnet}\n')
                else:
                    output_list.append(
                        f'set network tunnel ipsec \"{vpn_dict[key]["name"]}\" auto-key proxy-id p{p_num} local {lnet} '
                        f'remote {rnet}\n')
                p_num += 1

    # Routes Output
    for rnet in vpn_dict[key]["remote_nets"]:
        if is_pano:
            output_list.append(f'set template {template} config network virtual-router \"{vrouter}\" '
                               f'routing-table ip static-route {vpn_dict[key]["name"][:11]}-{rnet.replace("/", "_")} '
                               f'interface tunnel.{vpn_dict[key]["tunnel_num"]} metric 10 destination {rnet}\n')
        else:
            output_list.append(f'set network virtual-router \"{vrouter}\" routing-table ip static-route '
                               f'{vpn_dict[key]["name"][:11]}-{rnet.replace("/", "_")} interface '
                               f'tunnel.{vpn_dict[key]["tunnel_num"]} metric 10 destination {rnet}\n')

    # Security Policies Output

    # Inbound Rule
    if is_pano:
        output_list.append(f'set device-group {dev_grp} tag {vpn_dict[key]["vpn_zone"]} color color14\n')
        output_list.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_dict[key]["name"]}_Inbound to '
                           f'{vpn_dict[key]["int_zone"]} from {vpn_dict[key]["vpn_zone"]}\n')
        output_list.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_dict[key]["name"]}_Inbound '
                           f'application any service application-default\n')
        output_list.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_dict[key]["name"]}_Inbound '
                           f'action allow\n')

        for l_net in vpn_dict[key]["local_nets"]:
            output_list.append(f'set device-group {dev_grp} pre-rulebase security rules '
                               f'{vpn_dict[key]["name"]}_Inbound destination {l_net}\n')
        for r_net in vpn_dict[key]["remote_nets"]:
            output_list.append(f'set device-group {dev_grp} pre-rulebase security rules '
                               f'{vpn_dict[key]["name"]}_Inbound source {r_net}\n')
        output_list.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_dict[key]["name"]}_Inbound '
                           f'profile-setting group "Threat Prevention Group"\n')

        # Outbound Rule
        output_list.append(f'set device-group {dev_grp} pre-rulebase security rules '
                           f'{vpn_dict[key]["name"]}_Outbound to {vpn_dict[key]["vpn_zone"]} '
                           f'from {vpn_dict[key]["int_zone"]}\n')
        output_list.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_dict[key]["name"]}_Outbound '
                           f'application any service application-default\n')
        output_list.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_dict[key]["name"]}_Outbound '
                           f'action allow\n')

        for r_net in vpn_dict[key]["remote_nets"]:
            output_list.append(f'set device-group {dev_grp} pre-rulebase security rules '
                               f'{vpn_dict[key]["name"]}_Outbound destination {r_net}\n')
        for l_net in vpn_dict[key]["local_nets"]:
            output_list.append(f'set device-group {dev_grp} pre-rulebase security rules '
                               f'{vpn_dict[key]["name"]}_Outbound source {l_net}\n')
        output_list.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_dict[key]["name"]}_Outbound '
                           f'profile-setting group "Threat Prevention Group"\n\n\n')

    else:
        # Inbound Rule
        output_list.append(f'set tag {vpn_dict[key]["vpn_zone"]} color color14\n')
        output_list.append(f'set rulebase security rules {vpn_dict[key]["name"]}_Inbound to '
                           f'{vpn_dict[key]["int_zone"]} from {vpn_dict[key]["vpn_zone"]}\n')
        output_list.append(f'set rulebase security rules {vpn_dict[key]["name"]}_Inbound application any service '
                           f'application-default\n')
        output_list.append(f'set rulebase security rules {vpn_dict[key]["name"]}_Inbound action allow\n')
        for l_net in vpn_dict[key]["local_nets"]:
            output_list.append(f'set rulebase security rules {vpn_dict[key]["name"]}_Inbound destination {l_net}\n')
        for r_net in vpn_dict[key]["remote_nets"]:
            output_list.append(f'set rulebase security rules {vpn_dict[key]["name"]}_Inbound source {r_net}\n')
        output_list.append(f'set rulebase security rules {vpn_dict[key]["name"]}_Inbound profile-setting group '
                           f'"Threat Prevention Group"\n')

        # Outbound Rule
        output_list.append(f'set rulebase security rules {vpn_dict[key]["name"]}_Outbound to '
                           f'{vpn_dict[key]["vpn_zone"]} from {vpn_dict[key]["int_zone"]}\n')
        output_list.append(f'set rulebase security rules {vpn_dict[key]["name"]}_Outbound application any service '
                           f'application-default\n')
        output_list.append(f'set rulebase security rules {vpn_dict[key]["name"]}_Outbound action allow\n')
        for l_net in vpn_dict[key]["local_nets"]:
            output_list.append(f'set rulebase security rules {vpn_dict[key]["name"]}_Outbound source {l_net}\n')
        for r_net in vpn_dict[key]["remote_nets"]:
            output_list.append(f'set rulebase security rules {vpn_dict[key]["name"]}_Outbound destination {r_net}\n')
        output_list.append(f'set rulebase security rules {vpn_dict[key]["name"]}_Outbound profile-setting group '
                           f'"Threat Prevention Group"\n\n\n')


try:
    temp_out = open(asksaveasfilename(initialdir=os.path.expanduser("~/Desktop"), title="Select Output file",
                                      defaultextension='.txt', filetypes=[('Text File', '.txt')]), "w")
except FileNotFoundError:  # Handles user selecting 'Cancel'
    temp_out = None
    messagebox.showinfo("Process aborted", "IPSEC VPN Tunnel set commands text file not saved.")
    exit()

# Output the actual set commands
for each in output_list:
    temp_out.write(each)

temp_out.write("\n")  # Create a blank line in output file.

temp_out.close()
messagebox.showinfo("Success", f"IPSEC VPN Tunnel Set commands text file saved as: {temp_out.name}.")
