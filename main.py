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
from acitoolkit.acisession import *
import csv
import requests
requests.packages.urllib3.disable_warnings()

"""
Create endpoint groups and Bridge Domains read in from a file
Place EPG in specified tenant
Place BDs in common tenant
"""

# Get the APIC login credentials
description = 'acitoolkit tutorial application'
creds = Credentials('apic', description)
creds.add_argument('--delete', action='store_true',
                   help='Delete the configuration from the APIC')
args = creds.get()

# pull domain info
#session = Session(args.url, args.login, args.password,verify_ssl=False)
#session.login()

#define global varibles
#dom = EPGDomain.get_by_name(session, 'L2-OUT')
#vmmdom1 = EPGDomain.get_by_name(session, 'HS-AVE')
#vmmdom2 = EPGDomain.get_by_name(session, 'TD-AVE')

# Create the EPG Tenant
tenant = Tenant('TCU-PROD')
shared_tenant = Tenant('common')
# Create the Application Profile
app = AppProfile('NETWORK-AP', tenant)

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
        #epg.add_infradomain(dom)
        #epg.add_infradomain(vmmdom1)
        #epg.add_infradomain(vmmdom2)

        # Create a Context and BridgeDomain and place them in the common tenant
        context = Context('default', shared_tenant)
        bd = BridgeDomain("" + str(vlan_name) + "_BD",shared_tenant)
        bd.set_arp_flood('yes')
        bd.set_unicast_route('no')
        bd.add_context(context)
        bd.unknown_mac_unicast = 'flood'
        bd.unicast_route = 'yes'

        # Place the EPG in the BD
        epg.add_bd(bd)


        # Get the APIC login credentials
        description = 'acitoolkit tutorial application'
        creds = Credentials('apic', description)
        creds.add_argument('--delete', action='store_true',
                                 help='Delete the configuration from the APIC')
        args = creds.get()

        #push the configuration
        session = Session(args.url, args.login, args.password, verify_ssl=False)
        session.login()
        resp = tenant.push_to_apic(session)

        if resp.ok:
            print 'Tenant Success'
        else:
            print 'Tenant Failure'
        print 'Pushed the following JSON to the APIC'
        print 'URL:', tenant.get_url()
        print 'JSON:', tenant.get_json()

        common_resp = shared_tenant.push_to_apic(session)
        if common_resp.ok:
            print 'Common Success'
        else:
            print 'Common Failure'



