type1_dict = {
        "tags": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/tag to-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**dst_vsys']/tag mode **mode",
        "interfaces": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/network/interface to-xpath /config/devices/entry[@name='localhost.localdomain']/network/interface mode **mode",
        "routers": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/network/virtual-router to-xpath /config/devices/entry[@name='localhost.localdomain']/network/virtual-router mode **mode",
        "zones": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/zone to-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**dst_vsys']/zone mode **mode",
        "services": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/service to-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**dst_vsys']/service mode **mode",
        "svc_groups": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/service-group to-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**dst_vsys']/service-group mode **mode",
        "addresses": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/address to-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**dst_vsys']/address mode **mode",
        "addr_groups": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/address-group to-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**dst_vsys']/address-group mode **mode",
        "sec_pols": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/rulebase/security/rules to-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**dst_vsys']/rulebase/security/rules mode **mode",
        "nat_pols": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/rulebase/nat/rules to-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**dst_vsys']/rulebase/nat/rules mode **mode",
        "ike": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/network/ike to-xpath /config/devices/entry[@name='localhost.localdomain']/network/ike mode **mode",
        "ipsec": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/network/tunnel/ipsec to-xpath /config/devices/entry[@name='localhost.localdomain']/network/tunnel/ipsec mode **mode"
        }

type2_dict = {
        "tags": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/tag to-xpath /config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='**dev_grp']/tag mode **mode",
        "interfaces": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/network/interface to-xpath /config/devices/entry[@name='localhost.localdomain']/template/entry[@name='**template']/config/devices/entry[@name='localhost.localdomain']/network/interface mode **mode",
        "routers": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/network/virtual-router to-xpath /config/devices/entry[@name='localhost.localdomain']/template/entry[@name='**template']/config/devices/entry[@name='localhost.localdomain']/network/virtual-router mode **mode",
        "services": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/service to-xpath /config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='**dev_grp']/service mode **mode",
        "svc_groups": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/service-group to-xpath /config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='**dev_grp']/service-group mode **mode",
        "addresses": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/address to-xpath /config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='**dev_grp']/address mode merge",
        "addr_groups": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/address-group to-xpath /config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='**dev_grp']/address-group mode **mode",
        "sec_pols_pre": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/rulebase/security/rules to-xpath /config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='**dev_grp']/pre-rulebase/security/rules mode **mode",
        "sec_pols_post": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/rulebase/security/rules to-xpath /config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='**dev_grp']/post-rulebase/security/rules mode **mode",
        "nat_pols_pre": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/rulebase/security/rules to-xpath /config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='**dev_grp']/pre-rulebase/nat/rules mode **mode",
        "nat_pols_post": "load config partial from **src_config from-xpath /config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='**src_vsys']/rulebase/nat/rules to-xpath /config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='**dev_grp']/post-rulebase/nat/rules mode **mode"
        }

type3_dict = {
    "dev-grp": "load config partial from running-config.xml from-xpath /config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='**src_devgrp'] to-xpath /config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='**dest_devgrp'] mode **mode",
    "template": "load config partial from running-config.xml from-xpath /config/devices/entry[@name='localhost.localdomain']/template/entry[@name='**src_template'] to-xpath /config/devices/entry[@name='localhost.localdomain']/template/entry[@name='**dest_template'] mode **mode"
    }

modes = {"1": "merge", "2": "append", "3": "replace"}


def type_select():
    while True:
        migrate_type = input("Enter type number:\n\t1. Firewall to Firewall\n\t2. Firewall to Panorama\n\t"
                             "3. Panorama to Panorama (Copy Device Group or Template)\n\t4. Exit\n")
        if migrate_type == "4":
            exit()
        elif migrate_type not in ["1", "2", "3"]:
            continue
        else:
            return migrate_type


def make_selections(migrate_type):
    # Works for both fw>fw and fw>pano
    if migrate_type == "1":
        options = {0: "all", 1: "tags", 2: "interfaces", 3: "routers", 4: "zones", 5: "services", 6: "svc_groups",
                   7: "addresses", 8: "addr_groups", 9: "sec_pols", 10: "nat_pols", 11: "ike", 12: "ipsec"}
        print(options)
    elif migrate_type == "2":
        options = {0: "all", 1: "tags", 2: "interfaces", 3: "routers", 4: "services", 5: "svc_groups", 6: "addresses",
                   7: "addr_groups", 8: "sec_pols_pre", 9: "sec_pols_post", 10: "nat_pols_pre", 11: "nat_pols_post"}
        print(options)
    else:
        options = {}
        exit()
    selected = []

    while True:
        current_choice = input("Enter a number for a configuration setting to migrate. "
                               "Hit enter with no input to finish.\n")
        if current_choice == "0":
            all_sel = []
            for k in options:
                if k != 0:
                    all_sel.append(options[k])
            return all_sel

        elif current_choice == "":
            break
        selected.append(options[int(current_choice)])
        # print(f'\'{options[int(current_choice)]}\' selected.')
        print(f'{selected} selected.\n')
    print(f'Migrating: {selected}')
    return selected


def type1(selected):
    cmds_list = []
    src_config = input("Enter source config name:\n")
    src_vsys = input("Enter source vsys #:\n")
    dst_vsys = input("Enter destination vsys #:\n")
    mode = input("Enter mode #:   1. Merge   2. Append   3. Replace\n")

    for each in selected:
        line = type1_dict[each]
        new_line = line.replace("**src_config", src_config)
        new_line = new_line.replace("**src_vsys", f'vsys{src_vsys}')
        new_line = new_line.replace("**dst_vsys", f'vsys{dst_vsys}')
        new_line = new_line.replace("**mode", modes[mode])
        cmds_list.append(f'{new_line}')
        # for cmd in cmds_list:
        #     print(cmd)
    return cmds_list


def type2(selected):
    cmds_list = []
    src_config = input("Enter source config name:\n")
    src_vsys = input("Enter source vsys #:\n")
    devgrp = input("Enter target Device Group name:\n")
    template = input("Enter target Template name:\n")
    mode = input("Enter mode # (1. Merge   2. Append   3. Replace\n")

    for each in selected:
        line = type2_dict[each]
        new_line = line.replace("**src_config", src_config)
        new_line = new_line.replace("**src_vsys", f'vsys{src_vsys}')
        new_line = new_line.replace("**dev_grp", devgrp)
        new_line = new_line.replace("**template", template)
        new_line = new_line.replace("**mode", modes[mode])
        cmds_list.append(f'{new_line}')
        # for cmd in cmds_list:
        #     print(cmd)
    return cmds_list


def type3():
    cmds_list = []
    while True:
        selected = input("Which are you trying to copy?  1. Device Group   2. Template   3. Both\n")
        if selected not in ["1", "2", "3"]:
            continue
        else:
            break

    mode = input("Enter mode # (1. Merge   2. Append   3. Replace\n")

    def run_1():
        src_devgrp = input("Enter source Device Group:\n")
        dest_devgrp = input("Enter target Device Group name:\n")
        line = type3_dict["dev-grp"]
        new_line = line.replace("**src_devgrp", src_devgrp)
        new_line = new_line.replace("**dest_devgrp", dest_devgrp)
        new_line = new_line.replace("**mode", modes[mode])
        cmds_list.append(new_line)

    def run_2():
        src_template = input("Enter source Template:\n")
        dest_template = input("Enter target Template name:\n")
        line = type3_dict["template"]
        new_line = line.replace("**src_template", src_template)
        new_line = new_line.replace("**dest_template", dest_template)
        new_line = new_line.replace("**mode", modes[mode])
        cmds_list.append(new_line)

    if selected == "1":
        run_1()

    elif selected == "2":
        run_2()

    elif selected == "3":
        run_1()
        run_2()

    return cmds_list


run_type = type_select()
# print(run_type)

if run_type == "1":
    output = type1(make_selections(run_type))
    for entry in output:
        print(entry)

elif run_type == "2":
    output = type2(make_selections(run_type))
    for entry in output:
        print(entry)

elif run_type == "3":
    output = type3()
    for entry in output:
        print(entry)

else:
    print("Invalid selection. Process terminating")
