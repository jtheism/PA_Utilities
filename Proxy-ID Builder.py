import os
from sys import exit
from tkinter.filedialog import Tk, asksaveasfilename
from tkinter import messagebox
Tk().withdraw()  # Prevents tkinter window from opening


def proxy_builder():
    tunnel_num = ''
    ipsec_name = input("Enter IPSEC Tunnel Name:\n")
    do_routes = input("Would you like to create routes for these remote networks? (y or n)\n")
    if do_routes == 'y':
        tunnel_num = str(input("Enter tunnel interface number:\n"))
        vrouter_name = str(input("Enter virtual router name:\n"))
    local_nets = []
    remote_nets = []
    p_num = 1  # for Proxy-ID name  p1, p2, p3, etc.
    while True:
        local_net = input("Enter a local network and hit enter. "
                          "Press Enter without input to move on to remote networks entry.\n")
        if local_net == "":
            break
        else:
            local_nets.append(local_net)
        print("\nLocal Networks:")
        for net in local_nets:
            print(net)
        print()

    while True:
        remote_net = input("Enter a remote network and hit enter. Press Enter without input to finish.\n")
        if remote_net == "":
            break
        else:
            remote_nets.append(remote_net)
        print("Remote Networks:")
        for net in remote_nets:
            print(net)

    for lnet in local_nets:
        for rnet in remote_nets:
            if is_panorama != '':
                output_list.append(f'set template \"{is_panorama}\" config network tunnel ipsec \"{ipsec_name}\" '
                                   f'auto-key proxy-id p{p_num} local {lnet} remote {rnet}\n')
            else:
                output_list.append(f'set network tunnel ipsec \"{ipsec_name}\" auto-key proxy-id p{p_num} local {lnet} '
                                   f'remote {rnet}\n')
            p_num += 1

    if do_routes == "y":
        for ext_net in remote_nets:
            if is_panorama != '':
                route_list.append(f'set template {is_panorama} config network virtual-router \"{vrouter_name}\" '
                                  f'routing-table ip static-route {ipsec_name[:11]}-{ext_net.replace("/", "_")} '
                                  f'interface tunnel.{tunnel_num} metric 10 destination {ext_net}\n')
            else:
                route_list.append(f'set network virtual-router \"{vrouter_name}\" routing-table ip static-route '
                                  f'{ipsec_name[:11]}-{ext_net.replace("/", "_")} interface tunnel.{tunnel_num} '
                                  f'metric 10 destination {ext_net}\n')

    net_tup = (ipsec_name, local_nets, remote_nets)
    network_sets.append(net_tup)


output_list = []   # for proxy-id set commands
route_list = []    # for route set commands
network_sets = []  # holds the tuples of the tunnel name with local and remote nets, prints at top of the output file.

is_panorama = input("If this is for Panorama, enter the Template name. Otherwise, press Enter.\n")

# Run the function the first time:
proxy_builder()

# Ask user if there are other tunnels, if so run function again, otherwise break out and go to output creation.
while True:
    more = input("Do you have another tunnel to enter?  (y or n)\n")
    if more == "y":
        proxy_builder()
    else:
        break

try:
    temp_out = open(asksaveasfilename(initialdir=os.path.expanduser("~/Desktop"), title="Select Output file",
                                      defaultextension='.txt', filetypes=[('Text File', '.txt')]), "w")
except FileNotFoundError:  # Handles user selecting 'Cancel'
    temp_out = None
    messagebox.showinfo("Process aborted", "Proxy-ID Set commands text file not saved.")
    exit()

#  At top of output file, create summaries of tunnel names with local and remote networks.
for net_set in network_sets:
    temp_out.write(f'{net_set[0]}: Local Nets = {net_set[1]}  Remote Nets = {net_set[2]}\n')

temp_out.write("\n")  # Create a blank line in output file.

# Output the actual set commands
for each in output_list:
    temp_out.write(each)

temp_out.write("\n")  # Create a blank line in output file.

if route_list:
    for destination_network in route_list:
        temp_out.write(destination_network)

temp_out.close()
messagebox.showinfo("Success", f"Proxy-ID Set commands text file saved as: {temp_out.name}.")
