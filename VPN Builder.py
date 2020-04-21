import os
from sys import exit
from tkinter.filedialog import Tk, asksaveasfilename
from tkinter import messagebox
Tk().withdraw()  # Prevents tkinter window from opening

#
p1_crypto_dict = {"encrypt": {1: "des", 2: "3des", 3: "aes-128-cbc", 4: "aes-192-cbc", 5: "aes-256-cbc"},
                  "auth": {1: "sha1", 2: "sha256", 3: "sha384", 4: "sha512", 5: "md5"},
                  "dh": {1: "group1", 2: "group2", 5: "group5", 14: "group14", 19: "group19", 20: "group20"},
                  "lifetime": {1: ["days", "1-365", range(1, 366)],
                               2: ["hours", "1-65535", range(1, 65536)],
                               3: ["minutes", "3-65535", range(3, 65536)],
                               4: ["seconds", "180-65535", range(180, 65536)]}
                  }

p2_crypto_dict = {"encrypt": {1: "des", 2: "3des", 3: "aes-128-cbc", 4: "aes-192-cbc", 5: "aes-256-cbc",
                              6: "aes-128-gcm", 7: "aes-192-gcm", 8: "aes-256-gcm"},
                  "auth": {1: "sha1", 2: "sha256", 3: "sha384", 4: "sha512", 5: "md5"},
                  "dh": {0: "no-pfs", 1: "group1", 2: "group2", 5: "group5", 14: "group14", 19: "group19",
                         20: "group20"},
                  "lifetime": {1: ["days", "1-365", range(1, 366)],
                               2: ["hours", "1-65535", range(1, 65536)],
                               3: ["minutes", "3-65535", range(3, 65536)],
                               4: ["seconds", "180-65535", range(180, 65536)]}
                  }

ike_id_types = {1: "ipaddr", 2: "fqdn", 3: "ufqdn"}
ike_gtwy_version = {1: "ikev1", 2: "ikev2", 3: "ikev2-preferred"}
ike_mode = {1: "main", 2: "aggressive", 3: "auto"}

pano_template = input("Is this for Panorama?  Enter template name, or hit ENTER if not.\n")
if pano_template:
    dev_grp = input("Enter Device Group name for security policies:\n")
# same for each VPN tunnel
virtual_router = input("Set virtual router name:\n")
ike_gtwy_intf = "ethernet1/" + input('Enter PAN Gateway Interface number: (e.g. ethernet1/x). '
                                     'Do not type the "ethernet1/", just enter the x value.\n')
ike_gtwy_intf_ip = input("Enter PAN Gateway Interface IP address with mask (e.g. 1.2.3.4/30):\n")
master_list_out = []
if pano_template:
    master_list_out.append('### Create shared security profile group for policies ###\nset shared profile-group '
                           '"Threat Prevention Group"\n')
else:
    master_list_out.append('### Create security profile group for policies ###\nset profile-group '
                           '"Threat Prevention Group"\n')

# different for each VPN tunnel - Gets overwritten later if multiple setups
vpn_tunnel_name = input("Enter the name for this VPN connection (no spaces):\n")
ike_peer_gtwy = input("Enter Peer Gateway IP address:\n")


def vpn_builder():
    tunnel_name_out = [f'\n\t###### Start {vpn_tunnel_name} ######\n']
    p1c_out = ike_crypto()
    p2c_out = ipsec_crypto()
    ike_gate_out = ike_gateway()
    tun_out, tun_zn, tun_num = tunnel_interface()
    rem_n, loc_n, ipsec_tun_out = ipsec_tunnel(tun_num)
    sec_pol_out = sec_pols(rem_n, tun_zn, loc_n)
    out_cmd_lists = [tunnel_name_out, p1c_out, p2c_out, ike_gate_out, tun_out, ipsec_tun_out, sec_pol_out]
    for lst in out_cmd_lists:
        for entry in lst:
            master_list_out.append(entry)
    return


# set for Pano
def ike_crypto():
    while True:
        try:
            p1_enc = int(input("Select Phase 1 Encryption:\n\t1: des\n\t2: 3des\n\t3: aes-128-cbc\n\t4: aes-192-cbc\n\t"
                               "5: aes-256-cbc\n"))
            if p1_enc not in [1, 2, 3, 4, 5]:
                raise ValueError
            break
        except ValueError:
            print("!!! Invalid entry. Please try again.\n")
    while True:
        try:
            p1_auth = int(input("Select Phase 1 Authentication:\n\t"
                                "1: sha1\n\t2: sha256\n\t3: sha384\n\t4: sha512\n\t5: md5\n"))
            if p1_auth not in [1, 2, 3, 4, 5]:
                raise ValueError
            break
        except ValueError:
            print("!!! Invalid entry. Please try again.")

    while True:
        try:
            p1_dh = int(input("Select Phase 1 Diffie-Hellman Group:\n\t"
                              "1: group1\n\t2: group2\n\t5: group5\n\t14: group14\n\t19: group19\n\t20: group20\n"))
            if p1_dh not in [1, 2, 5, 14, 19, 20]:
                raise ValueError
            break
        except ValueError:
            print("!!! Invalid entry. Please try again.")

    while True:
        try:
            p1_lifetime = int(input("Select Phase 1 Lifetime:\n\t1: days, 2: hours, 3: minutes, 4: seconds\n"))
            if p1_lifetime not in [1, 2, 3, 4]:
                raise ValueError
            break
        except ValueError:
            print("!!! Invalid entry. Please try again.")

    while True:
        try:
            p1_life_val = int(input(f'Enter Phase 1 Lifetime value (range: '
                                    f'{p1_crypto_dict["lifetime"][p1_lifetime][1]}):\n'))
            if p1_life_val not in p1_crypto_dict["lifetime"][p1_lifetime][2]:
                raise ValueError
            break
        except ValueError:
            print("!!! Invalid entry. Please try again.")

    # Start Output
    if pano_template:
        p1_crypto_string = (f'\n\t### IKE Crypto ###\n'
                            f'set template \"{pano_template}\"config network ike crypto-profiles ike-crypto-profiles '
                            f'P1_{vpn_tunnel_name} hash {p1_crypto_dict["auth"][p1_auth]} '
                            f'dh-group {p1_crypto_dict["dh"][p1_dh]} encryption {p1_crypto_dict["encrypt"][p1_enc]} '
                            f'lifetime {p1_crypto_dict["lifetime"][p1_lifetime][0]} {p1_life_val}\n\n')
    else:
        p1_crypto_string = (f'\n\t### IKE Crypto ###\n'
                            f'set network ike crypto-profiles ike-crypto-profiles P1_{vpn_tunnel_name} '
                            f'hash {p1_crypto_dict["auth"][p1_auth]} '
                            f'dh-group {p1_crypto_dict["dh"][p1_dh]} encryption {p1_crypto_dict["encrypt"][p1_enc]} '
                            f'lifetime {p1_crypto_dict["lifetime"][p1_lifetime][0]} {p1_life_val}\n\n')

    return p1_crypto_string


# set for Pano
def ipsec_crypto():
    p2_crypto_list = [f'\t### IPSEC Crypto ###\n']
    while True:
        try:
            p2_enc = int(input("Select Phase 2 Encryption:\n\t"
                               "1: des\n\t2: 3des\n\t3: aes-128-cbc\n\t4: aes-192-cbc\n\t5: aes-256-cbc\n\t"
                               "6: aes-128-gcm\n\t7: aes-192-gcm\n\t8: aes-256-gcm\n"))
            if p2_enc not in range(1, 9):
                raise ValueError
            break
        except ValueError:
            print("!!! Invalid entry. Please try again.")

    while True:
        try:
            p2_auth = int(input("Select Phase 2 Authentication:\n\t"
                                "1: sha1\n\t2: sha256\n\t3: sha384\n\t4: sha512\n\t5: md5\n"))
            if p2_auth not in range(1, 6):
                raise ValueError
            break
        except ValueError:
            print("!!! Invalid entry. Please try again.")

    while True:
        try:
            p2_dh = int(input("Select Phase 2 Diffie-Hellman Group:\n\t"
                              "0: no-pfs\n\t1: group1\n\t2: group2\n\t5: group5\n\t14: group14\n\t"
                              "19: group19\n\t20: group20\n"))
            if p2_dh not in [0, 1, 2, 5, 14, 19, 20]:
                raise ValueError
            break
        except ValueError:
            print("!!! Invalid entry. Please try again.")

    while True:
        try:
            p2_lifetime = int(input("Select Phase 2 Lifetime:\n\t1: days, 2: hours, 3: minutes, 4: seconds\n"))
            if p2_lifetime not in range(1, 5):
                raise ValueError
            break
        except ValueError:
            print("!!! Invalid entry. Please try again.")

    while True:
        try:
            p2_life_val = int(input(f'Enter Phase 2 Lifetime value (range: '
                                    f'{p2_crypto_dict["lifetime"][p2_lifetime][1]}):\n'))
            if p2_life_val not in p1_crypto_dict["lifetime"][p2_lifetime][2]:
                raise ValueError
            break
        except ValueError:
            print("!!! Invalid entry. Please try again.")

    # Start Output
    if pano_template:
        p2_crypto_list.append(f'set template \"{pano_template}\" config network ike crypto-profiles '
                              f'ipsec-crypto-profiles P2_{vpn_tunnel_name} esp authentication '
                              f'{p2_crypto_dict["auth"][p2_auth]} '
                              f'encryption {p2_crypto_dict["encrypt"][p2_enc]}\n')
        p2_crypto_list.append(f'set template \"{pano_template}\" config network ike crypto-profiles '
                              f'ipsec-crypto-profiles P2_{vpn_tunnel_name} dh-group {p2_crypto_dict["dh"][p2_dh]} '
                              f'lifetime {p2_crypto_dict["lifetime"][p2_lifetime][0]} {p2_life_val}\n\n')
    else:
        p2_crypto_list.append(f'set network ike crypto-profiles ipsec-crypto-profiles P2_{vpn_tunnel_name} '
                              f'esp authentication {p2_crypto_dict["auth"][p2_auth]} '
                              f'encryption {p2_crypto_dict["encrypt"][p2_enc]}\n')
        p2_crypto_list.append(f'set network ike crypto-profiles ipsec-crypto-profiles P2_{vpn_tunnel_name} '
                              f'dh-group {p2_crypto_dict["dh"][p2_dh]} lifetime '
                              f'{p2_crypto_dict["lifetime"][p2_lifetime][0]} {p2_life_val}\n\n')

    return p2_crypto_list


# set for Pano
def ike_gateway():
    ike_gtwy_out_list = [f'\t### IKE Gateway ###\n']
    ike_gtwy_name = f'GW-{vpn_tunnel_name}'
    while True:
        try:
            ike_version_sel = ike_gtwy_version[int(input(f'Select IKE Version:\n\t1: IKEv1\n\t2: IKEv2\n\t'
                                                         f'3: IKEv2-preferred\n'))]
            if ike_version_sel not in ["ikev1", "ikev2", "ikev2-preferred"]:
                raise ValueError
            break
        except ValueError:
            print("!!! Invalid entry. Please try again.")

    if ike_version_sel == "ikev1":
        while True:
            try:
                ike_v1_exch_mode = int(input("Select IKEv1 Exchange Mode:\n\t1: Main\n\t2: Aggressive\n\t3: Auto\n"))
                if ike_v1_exch_mode not in range(1, 4):
                    raise ValueError
                break
            except ValueError:
                print("!!! Invalid entry. Please try again.")

        ikev1_dpd_check = input("IKEv1 Dead Peer Detection (default) is: Interval 5 seconds, Retry 5 seconds. "
                                "Is this ok?   Hit ENTER for yes or \"n\" for no.\n")
        if ikev1_dpd_check == "n":
            while True:
                try:
                    dpd_int = input("Enter DPD interval (2-100):\n\t")
                    if dpd_int not in range(2, 101):
                        raise ValueError
                    break
                except ValueError:
                    print("!!! Invalid entry. Please try again.")
            while True:
                try:
                    dpd_retry = input("Enter DPD retry (2-100):\n\t")
                    if dpd_retry not in range(2, 101):
                        raise ValueError
                    break
                except ValueError:
                    print("!!! Invalid entry. Please try again.")

        else:
            dpd_int = "5"
            dpd_retry = "5"
    else:
        while True:
            try:
                ikev2_liveness = int(input("\nIKEv2 Liveness check default is 5 seconds. If ok, hit ENTER, "
                                           "else enter value between 2-100\n") or 5)
                if ikev2_liveness not in range(2, 101):
                    raise ValueError
                break
            except ValueError:
                print("!!! Invalid entry. Please try again.")

    while True:
        ike_psk = input("Enter Pre-Shared Key:\n")
        print(f'\nPreshared Key: {ike_psk}\n')
        psk_ok = input("Is this Pre-Shared Key correct?   Hit ENTER if yes, else \"n\"\n")
        if psk_ok == '' or psk_ok.lower() == "y":
            break
        else:
            continue
    local_id = input("\nDo you need to enter an IKE LOCAL ID?  "
                     "Hit ENTER to skip or 'y' to create :\n")
    remote_id = input("\nDo you need to enter an IKE REMOTE ID? "
                      "Hit ENTER to skip or 'y' to create :\n")
    if local_id.lower() == "y":
        while True:
            try:
                loc_id_type = int(input("\nWhat is the LOCAL ID type?\n\t1: IP Address\n\t2: FQDN\n\t"
                                        "3: Email Address\n"))
                if loc_id_type not in range(1, 4):
                    raise ValueError
                break
            except ValueError:
                print("!!! Invalid entry. Please try again.")
        loc_id_value = input("\nEnter the LOCAL ID value:\n")
    if remote_id.lower() == "y":

        while True:
            try:
                rem_id_type = int(input("\nWhat is the REMOTE ID type?\n\t1: IP Address\n\t2: FQDN\n\t"
                                        "3: Email Address\n"))
                if rem_id_type not in range(1, 4):
                    raise ValueError
                break
            except ValueError:
                print("!!! Invalid entry. Please try again.")
        rem_id_value = input("\nEnter the REMOTE ID value:\n")
    while True:
        ike_nat_trav = input("Enable Nat Traversal?  y or n\n").lower()
        if ike_nat_trav not in ["y", "n"]:
            raise ValueError
        else:
            break

    # START OUTPUT
    if pano_template:
        # PSK
        ike_gtwy_out_list.append(f'set template \"{pano_template}\" config network ike gateway {ike_gtwy_name} '
                                 f'authentication pre-shared-key key {ike_psk}\n')

        # Local gateway interface and IP
        ike_gtwy_out_list.append(f'set template \"{pano_template}\" config network ike gateway {ike_gtwy_name} '
                                 f'local-address interface {ike_gtwy_intf} ip {ike_gtwy_intf_ip}\n')

        # Peer gateway IP
        ike_gtwy_out_list.append(f'set template \"{pano_template}\" config network ike gateway {ike_gtwy_name} '
                                 f'peer-address ip {ike_peer_gtwy}\n')

        # NAT-T
        if ike_nat_trav == "y":
            ike_gtwy_out_list.append(f'set template \"{pano_template}\" config network ike gateway {ike_gtwy_name} '
                                     f'protocol-common nat-traversal enable yes\n')

        # Set local and peer IDs if being used
        if local_id == "y":
            ike_gtwy_out_list.append(f'set template \"{pano_template}\" config network ike gateway {ike_gtwy_name} '
                                     f'local-id type {ike_id_types[loc_id_type]} id {loc_id_value}\n')
        if remote_id == "y":
            ike_gtwy_out_list.append(f'set template \"{pano_template}\" config network ike gateway {ike_gtwy_name} '
                                     f'peer-id type {ike_id_types[rem_id_type]} id {rem_id_value}\n')

        # IKEv1 specific
        if ike_version_sel == "ikev1":
            # ikev1 exchange and crypto
            ike_gtwy_out_list.append(f'set template \"{pano_template}\" config network ike gateway {ike_gtwy_name} '
                                     f'protocol version ikev1 ikev1 exchange-mode {ike_mode[ike_v1_exch_mode]} '
                                     f'ike-crypto-profile P1_{vpn_tunnel_name} dpd enable yes interval {dpd_int} '
                                     f'retry {dpd_retry}\n\n')

        # IKEv2 specific
        else:
            ike_gtwy_out_list.append(f'set template \"{pano_template}\" config network ike gateway {ike_gtwy_name} '
                                     f'protocol version ikev2 ikev2 ike-crypto-profile P1_{vpn_tunnel_name} '
                                     f'dpd enable yes interval {ikev2_liveness}\n\n')
    else:
        # PSK
        ike_gtwy_out_list.append(f'set network ike gateway {ike_gtwy_name} authentication pre-shared-key '
                                 f'key {ike_psk}\n')

        # Local gateway interface and IP
        ike_gtwy_out_list.append(f'set network ike gateway {ike_gtwy_name} local-address interface {ike_gtwy_intf} '
                                 f'ip {ike_gtwy_intf_ip}\n')

        # Peer gateway IP
        ike_gtwy_out_list.append(f'set network ike gateway {ike_gtwy_name} peer-address ip {ike_peer_gtwy}\n')

        # NAT-T
        if ike_nat_trav == "y":
            ike_gtwy_out_list.append(f'set network ike gateway {ike_gtwy_name} protocol-common nat-traversal '
                                     f'enable yes\n')

        # Set local and peer IDs if being used
        if local_id == "y":
            ike_gtwy_out_list.append(f'set network ike gateway {ike_gtwy_name} local-id type '
                                     f'{ike_id_types[loc_id_type]} id {loc_id_value}\n')
        if remote_id == "y":
            ike_gtwy_out_list.append(f'set network ike gateway {ike_gtwy_name} peer-id type '
                                     f'{ike_id_types[rem_id_type]} id {rem_id_value}\n')

        # IKEv1 specific
        if ike_version_sel == "ikev1":
            # ikev1 exchange and crypto
            ike_gtwy_out_list.append(f'set network ike gateway {ike_gtwy_name} protocol version ikev1 ikev1 '
                                     f'exchange-mode {ike_mode[ike_v1_exch_mode]} ike-crypto-profile '
                                     f'P1_{vpn_tunnel_name} dpd enable yes interval {dpd_int} retry {dpd_retry}\n\n')

        # IKEv2 specific
        else:
            ike_gtwy_out_list.append(f'set network ike gateway {ike_gtwy_name} protocol version ikev2 ikev2 '
                                     f'ike-crypto-profile P1_{vpn_tunnel_name} dpd enable yes '
                                     f'interval {ikev2_liveness}\n\n')

    return ike_gtwy_out_list


# set for pano
def tunnel_interface():
    output_list = [f'\t### Tunnel Interface ###\n']
    tunnel_num = input("\nSet Tunnel Interface number:\n")
    tun_zone = (input("\nEnter Tunnel Zone Name:\n"))
    while True:
        tun_ip = input("Enter tunnel IP address/netmask if needed, else press ENTER.\n")
        if not tun_ip:
            break
        print(f'\nTunnel IP: {tun_ip}\n')
        tun_ip_ok = input("Tunnel IP Ok?   y or n\n")
        if tun_ip_ok == 'y':
            break
        else:
            continue

    if pano_template:         
        output_list.append(f'set template \"{pano_template}\" config network interface tunnel units '
                           f'tunnel.{tunnel_num} comment {vpn_tunnel_name}\n')
        if tun_ip:
            output_list.append(f'set template \"{pano_template}\" config network interface tunnel units '
                               f'tunnel.{tunnel_num} ip tun_ip\n')
        output_list.append(f'set template \"{pano_template}\" config vsys vsys1 import network interface '
                           f'tunnel.{tunnel_num}\n')
        output_list.append(f'set template \"{pano_template}\" config vsys vsys1 zone "{tun_zone}" network layer3 '
                           f'tunnel.{tunnel_num}\n')
        output_list.append(f'set template \"{pano_template}\" config network virtual-router \"{virtual_router}\" '
                           f'interface tunnel.{tunnel_num}\n')
            
    else:
        output_list.append(f'set zone "{tun_zone}" network layer3 [ ]\n')
        output_list.append(f'set network interface tunnel units tunnel.{tunnel_num} comment {vpn_tunnel_name}\n')
        output_list.append(f'set zone "{tun_zone}" network layer3 tunnel.{tunnel_num}\n')
        output_list.append(f'set network virtual-router "{virtual_router}" interface tunnel.{tunnel_num}\n\n')
    if tun_ip:
        output_list.append(f'set network interface tunnel units tunnel.{tunnel_num} ip {tun_ip}\n\n')

    return output_list, tun_zone, tunnel_num


# set for Pano
def ipsec_tunnel(tun_num):
    ipsec_out_list = [
                      f'\t### IPSEC Tunnel ###\n',
                      f'set network tunnel ipsec {vpn_tunnel_name} auto-key ike-gateway GW-{vpn_tunnel_name}\n',
                      f'set network tunnel ipsec {vpn_tunnel_name} auto-key ipsec-crypt-profile P2_{vpn_tunnel_name}\n',
                      f'set network tunnel ipsec {vpn_tunnel_name} tunnel-monitor enable no\n',
                      f'set network tunnel ipsec {vpn_tunnel_name} tunnel-interface tunnel.{tun_num}\n',
                      f'set network tunnel ipsec {vpn_tunnel_name} disabled no\n',
                      f'set network tunnel ipsec {vpn_tunnel_name} copy-tos yes\n\n'
                      ]

    ipsec_out_pano = [
                      f'\t### IPSEC Tunnel ###\n',
                      f'set template \"{pano_template}\" config network tunnel ipsec {vpn_tunnel_name} auto-key '
                      f'ike-gateway GW-{vpn_tunnel_name}\n',
                      f'set template \"{pano_template}\" config network tunnel ipsec {vpn_tunnel_name} auto-key '
                      f'ipsec-crypt-profile P2_{vpn_tunnel_name}\n',
                      f'set template \"{pano_template}\" config network tunnel ipsec {vpn_tunnel_name} tunnel-monitor '
                      f'enable no\n',
                      f'set template \"{pano_template}\" config network tunnel ipsec {vpn_tunnel_name} '
                      f'tunnel-interface tunnel.{tun_num}\n',
                      f'set template \"{pano_template}\" config network tunnel ipsec {vpn_tunnel_name} disabled no\n',
                      f'set template \"{pano_template}\" config network tunnel ipsec {vpn_tunnel_name} copy-tos yes\n\n'
                      ]

    # Section for adding Routes and Proxy-IDs
    local_nets = []
    remote_nets = []
    do_routes = input("Do you want to create routes for the remote networks? y for yes or hit ENTER for no.\n")
    if do_routes.lower() == "y":
        while True:
            remote_net = input("Enter a remote network and hit enter. Enter \"d\" to delete a network. "
                               "Press Enter without input to finish.\n")
            if remote_net == "":
                break
            elif remote_net.lower() == "d":
                try:
                    remote_nets.remove(input("Enter remote network to delete:\n"))
                    print("\nRemote Networks:")
                    for net in remote_nets:
                        print(net)
                    print()
                except ValueError:
                    print("Remote network not in list.")
                    print("\nRemote Networks:")
                    for net in remote_nets:
                        print(net)
                    print()
                    continue
            else:
                remote_nets.append(remote_net)
            print("Remote Networks:")
            for net in remote_nets:
                print(net)

        # Start Output for routes
        ipsec_out_pano.append(f'\n\t### Routes ###\n')
        ipsec_out_list.append(f'\n\t### Routes ###\n')
        for ext_net in remote_nets:
            if pano_template:
                ipsec_out_pano.append(f'set template \"{pano_template}\" config network virtual-router '
                                      f'"{virtual_router}" routing-table ip static-route '
                                      f'{vpn_tunnel_name[:11]}-{ext_net.replace("/", "_")} '
                                      f'interface tunnel.{tun_num} metric 10 destination {ext_net}\n')
            else:
                ipsec_out_list.append(f'set network virtual-router "{virtual_router}" routing-table ip '
                                      f'static-route {vpn_tunnel_name[:11]}-{ext_net.replace("/", "_")} '
                                      f'interface tunnel.{tun_num} metric 10 destination {ext_net}\n')

    # Proxy-IDs
    need_proxy_id = input("Do you need to enter proxy IDs?  y for yes or hit ENTER for no.\n")
    if need_proxy_id.lower() == "y":
        p_num = 1  # for Proxy-ID name  p1, p2, p3, etc.
        # Local Nets
        while True:
            local_net = input("Enter a local network and hit enter. Enter \"d\" to delete a network. "
                              "Press Enter without input to move on to remote networks entry.\n")
            if local_net == "":
                break
            elif local_net.lower() == "d":
                try:
                    local_nets.remove(input("Enter local network to delete:\n"))
                    print("\nLocal Networks:")
                    for net in local_nets:
                        print(net)
                    print()
                except ValueError:
                    print("Local network not in list.")
                    print("\nLocal Networks:")
                    for net in local_nets:
                        print(net)
                    print()
                    continue
            else:
                local_nets.append(local_net)
            print("\nLocal Networks:")
            for net in local_nets:
                print(net)
            print()

        # remote nets
        new_routes = input("Remote Networks taken from routes entered. To enter different routes, type 'YES' "
                           "else hit ENTER.")

        if do_routes.lower() != "y" or new_routes == "YES":
            remote_nets = []
            while True:
                remote_net = input("Enter a remote network and hit enter. Enter \"d\" to delete a network. "
                                   "Press Enter without input to finish.\n")
                if remote_net == "":
                    break
                elif remote_net.lower() == "d":
                    try:
                        remote_nets.remove(input("Enter remote network to delete:\n"))
                        print("\nRemote Networks:")
                        for net in remote_nets:
                            print(net)
                        print()
                    except ValueError:
                        print("Remote network not in list.")
                        print("\nRemote Networks:")
                        for net in remote_nets:
                            print(net)
                        print()
                        continue
                else:
                    remote_nets.append(remote_net)
                print("Remote Networks:")
                for net in remote_nets:
                        print(net)

        # Start output for Proxy-IDs
        ipsec_out_pano.append(f'\n\t### Proxy-IDs ###\n')
        ipsec_out_list.append(f'\n\t### Proxy-IDs ###\n')
        for lnet in local_nets:
            for rnet in remote_nets:
                if pano_template:
                    ipsec_out_pano.append(f'set template \"{pano_template}\" config network tunnel ipsec '
                                          f'{vpn_tunnel_name} auto-key proxy-id p{p_num} local {lnet} remote {rnet}\n')
                else:
                    ipsec_out_list.append(f'set network tunnel ipsec \"{vpn_tunnel_name}\" auto-key proxy-id p{p_num} '
                                          f'local {lnet} remote {rnet}\n')
                p_num += 1
        print()
    if pano_template:
        return remote_nets, local_nets, ipsec_out_pano
    else:
        return remote_nets, local_nets, ipsec_out_list


def sec_pols(remote_n, rem_zone, local_n):
    local_zone = input(f'Enter local zone name:\n')
    if not local_n:
        print("\nSince no Proxy-IDs were entered, enter local networks for security policies.\n\n")
        local_nets = []
        while True:
            local_net = input("Enter a local network and hit enter. Enter \"d\" to delete a network. "
                              "Press Enter without input to move on to remote networks entry.\n")
            if local_net == "":
                break
            elif local_net.lower() == "d":
                try:
                    local_nets.remove(input("Enter local network to delete:\n"))
                    print("\nLocal Networks:")
                    for net in local_nets:
                        print(net)
                    print()
                except ValueError:
                    print("Local network not in list.")
                    print("\nLocal Networks:")
                    for net in local_nets:
                        print(net)
                    print()
                    continue
            else:
                local_nets.append(local_net)
            print("\nLocal Networks:")
            for net in local_nets:
                print(net)
            print()

    # Inbound Rule
    if dev_grp:
        sec_out = []
        sec_out.append(f'\n\t### {vpn_tunnel_name} Security Policies ###\n')
        sec_out.append(f'set device-group {dev_grp} tag {rem_zone} color color14\n')
        sec_out.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_tunnel_name}_Inbound to '
                       f'{local_zone} from {rem_zone}\n')
        sec_out.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_tunnel_name}_Inbound application '
                       f'any service application-default\n')
        sec_out.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_tunnel_name}_Inbound '
                       f'action allow\n')

        for l_net in local_n:
            sec_out.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_tunnel_name}_Inbound '
                           f'destination {l_net}\n')
        for r_net in remote_n:
            sec_out.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_tunnel_name}_Inbound '
                           f'source {r_net}\n')
        sec_out.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_tunnel_name}_Inbound '
                       f'profile-setting group '
                       f'"Threat Prevention Group"\n')
        # Outbound Rule
        sec_out.append(f'\n\t### {vpn_tunnel_name} Security Policies ###\n')
        sec_out.append(f'set device-group {dev_grp} tag {rem_zone} color color14\n')
        sec_out.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_tunnel_name}_Outbound to '
                       f'{rem_zone} from {local_zone}\n')
        sec_out.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_tunnel_name}_Outbound '
                       f'application any service application-default\n')
        sec_out.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_tunnel_name}_Outbound '
                       f'action allow\n')

        for r_net in remote_n:
            sec_out.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_tunnel_name}_Outbound '
                           f'destination {r_net}\n')
        for l_net in local_n:
            sec_out.append(f'set device-group {dev_grp} pre-rulebase security rules {vpn_tunnel_name}_Outbound '
                           f'source {l_net}\n')
        sec_out.append(
            f'set device-group {dev_grp} pre-rulebase security rules {vpn_tunnel_name}_Outbound profile-setting group '
            f'"Threat Prevention Group"\n')

    else:
        # Inbound Rule
        sec_out = []
        sec_out.append(f'\n\t### {vpn_tunnel_name} Security Policies ###\n')
        sec_out.append(f'set tag {rem_zone} color color14\n')
        sec_out.append(f'set rulebase security rules {vpn_tunnel_name}_Inbound to {local_zone} from {rem_zone}\n')
        sec_out.append(f'set rulebase security rules {vpn_tunnel_name}_Inbound application any service '
                       f'application-default\n')
        sec_out.append(f'set rulebase security rules {vpn_tunnel_name}_Inbound action allow\n')
        for l_net in local_n:
            sec_out.append(f'set rulebase security rules {vpn_tunnel_name}_Inbound destination {l_net}\n')
        for r_net in remote_n:
            sec_out.append(f'set rulebase security rules {vpn_tunnel_name}_Inbound source {r_net}\n')
        sec_out.append(f'set rulebase security rules {vpn_tunnel_name}_Inbound profile-setting group '
                       f'"Threat Prevention Group"\n')

        # Outbound Rule
        sec_out.append(f'set rulebase security rules {vpn_tunnel_name}_Outbound to {rem_zone} from {local_zone}\n')
        sec_out.append(f'set rulebase security rules {vpn_tunnel_name}_Outbound application any service '
                       f'application-default\n')
        sec_out.append(f'set rulebase security rules {vpn_tunnel_name}_Outbound action allow\n')
        for l_net in local_n:
            sec_out.append(f'set rulebase security rules {vpn_tunnel_name}_Outbound source {l_net}\n')
        for r_net in remote_n:
            sec_out.append(f'set rulebase security rules {vpn_tunnel_name}_Outbound destination {r_net}\n')
        sec_out.append(f'set rulebase security rules {vpn_tunnel_name}_Outbound profile-setting group '
                       f'"Threat Prevention Group"\n')
    return sec_out


# Start running functions
vpn_builder()

while True:
    more_tunnels = input(f'\nDo you want to enter another VPN tunnel?\n\t"y" for yes or "n" for no.\n')
    if more_tunnels.lower() == 'y':
        vpn_tunnel_name = input("Enter the name for this VPN connection (no spaces):\n")
        ike_peer_gtwy = input("Enter Peer Gateway IP address:\n")
        vpn_builder()
    elif more_tunnels.lower() == "n":
        break
    else:
        print(f'Please enter "y" or "n"\n')

try:
    temp_out = open(asksaveasfilename(initialdir=os.path.expanduser("~/Desktop"), title="Select Output file",
                                      defaultextension='.txt', filetypes=[('Text File', '.txt')]), "w")
except FileNotFoundError:  # Handles user selecting 'Cancel'
    temp_out = None
    messagebox.showinfo("Process aborted", "IPSEC VPN Tunnel set commands text file not saved.")
    exit()

# Output the actual set commands
for each in master_list_out:
    temp_out.write(each)

temp_out.write("\n")  # Create a blank line in output file.

temp_out.close()
messagebox.showinfo("Success", f"IPSEC VPN Tunnel Set commands text file saved as: {temp_out.name}.")
