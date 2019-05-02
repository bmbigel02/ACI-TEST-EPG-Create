################################################################################
#                 _    ____ ___   _____           _ _    _ _                   #
#                / \  / ___|_ _| |_   _|__   ___ | | | _(_) |_                 #
#               / _ \| |    | |    | |/ _ \ / _ \| | |/ / | __|                #
#              / ___ \ |___ | |    | | (_) | (_) | |   <| | |_                 #
#        ____ /_/   \_\____|___|___|_|\___/ \___/|_|_|\_\_|\__|                #
#       / ___|___   __| | ___  / ___|  __ _ _ __ ___  _ __ | | ___  ___        #
#      | |   / _ \ / _` |/ _ \ \___ \ / _` | '_ ` _ \| '_ \| |/ _ \/ __|       #
#      | |__| (_) | (_| |  __/  ___) | (_| | | | | | | |_) | |  __/\__ \       #
#       \____\___/ \__,_|\___| |____/ \__,_|_| |_| |_| .__/|_|\___||___/       #
#                                                    |_|                       #
################################################################################
#                                                                              #
# Copyright (c) 2015 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
#    Licensed under the Apache License, Version 2.0 (the "License"); you may   #
#    not use this file except in compliance with the License. You may obtain   #
#    a copy of the License at                                                  #
#                                                                              #
#         http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                              #
#    Unless required by applicable law or agreed to in writing, software       #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
#    License for the specific language governing permissions and limitations   #
#    under the License.                                                        #
#                                                                              #
################################################################################
from acitoolkit.acitoolkit import *
import csv

"""
Create a tenant with a single EPG and assign it statically to 2 interfaces.
This is the minimal configuration necessary to enable packet forwarding
within the ACI fabric.
"""

# Get the APIC login credentials
description = 'acitoolkit tutorial application'
creds = Credentials('apic', description)
creds.add_argument('--delete', action='store_true',
                   help='Delete the configuration from the APIC')
args = creds.get()

# pull domain info
session = Session(args.url, args.login, args.password)
session.login()

#define global varibles
dom = EPGDomain.get_by_name(session, 'phys')
vmmdom1 = EPGDomain.get_by_name(session, 'Fin_A')
vmmdom2 = EPGDomain.get_by_name(session, 'Fin_B')

interface = {'type': 'eth',
             'pod': '1', 'node': '101', 'module': '1', 'port': '65'}

# Create the EPG Tenant
tenant = Tenant('BIGOTEST')
shared_tenant = Tenant('common')

# Create the Application Profile
app = AppProfile('myapp', tenant)

with open('myvlans.csv') as csvfile:
    file = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in file:
        vlan_id = row[0]
        vlan_name = row[1]
        print(vlan_id, vlan_name)

        # Create the EPG
        epg = EPG("" + vlan_name + "_EPG",app)
        print "making epg and bridge domain combo " + (vlan_name)

        #add domains
        epg.add_infradomain(dom)
        epg.add_infradomain(vmmdom1)
        epg.add_infradomain(vmmdom2)


        # Create a Context and BridgeDomain and place them in the common tenant
        context = Context('default', shared_tenant)
        bd = BridgeDomain("" + vlan_name + "_BD",shared_tenant)
        bd.set_arp_flood('yes')
        bd.set_unicast_route('no')
        bd.add_context(context)
        bd.unknown_mac_unicast = 'flood'
        bd.unicast_route = 'yes'

        # Place the EPG in the BD
        epg.add_bd(bd)


        resp = tenant.push_to_apic(session)
        if resp.ok:
            print 'Success'
        else:
            print 'Failure'
        print 'Pushed the following JSON to the APIC'
        print 'URL:', tenant.get_url()
        print 'JSON:', tenant.get_json()





