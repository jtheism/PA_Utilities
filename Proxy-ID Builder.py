import os
from sys import exit
from tkinter.filedialog import Tk, asksaveasfilename
from tkinter import messagebox
Tk().withdraw()  # Prevents tkinter window from opening


def proxy_builder():
    ipsec_name = input("Enter IPSEC Tunnel Name:\n")
    local_nets = []
    remote_nets = []
    p_num = 1
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
            if panorama_template != '':
                output_list.append(f'set template \"{panorama_template}\" config network tunnel ipsec \"{ipsec_name}\" '
                                   f'auto-key proxy-id p{p_num} local {lnet} remote {rnet}\n')
            else:
                output_list.append(f'set network tunnel ipsec \"{ipsec_name}\" auto-key proxy-id p{p_num} local {lnet} '
                                   f'remote {rnet}\n')
            p_num += 1

    net_tup = (ipsec_name, local_nets, remote_nets)
    network_sets.append(net_tup)


output_list = []  # for the set commands
network_sets = []  # holds the tuples of the tunnel name with local and remote nets, prints at top of the output file.

panorama_template = input("If this is for Panorama, enter the Template name. Otherwise, press Enter.\n")

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
temp_out.write("\n")

# Output the actual set commands
for each in output_list:
    temp_out.write(each)


temp_out.close()
messagebox.showinfo("Success", f"Proxy-ID Set commands text file saved as: {temp_out.name}.")
