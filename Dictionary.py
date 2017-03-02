driver_dict = {'Cisco': 'cisco_ios', 'OpenSSH': 'alcatel_sros'}

cmd_dict = {
    'cisco_ios': {
        'BGP_N_G': 'show ip bgp ipv4 unicast neighbor',
        'BGP_N_G_RR': 'show ip bgp ipv4 unicast neighbor',
        'BGP_N_G_AR': 'show ip bgp ipv4 unicast neighbor',
        'BGP_N_V': 'show ip bgp vpnv4 vrf',
        'BGP_N_V_RR': 'show ip bgp vpnv4 vrf',
        'BGP_N_V_AR': 'show ip bgp vpnv4 vrf',
        'R_INT': 'show interface',
        'R_INT_C': 'show interface',
    },
    'alcatel_sros': {
        'BGP_N_G': 'show router bgp neighbor',
        'BGP_N_G_RR': 'show router bgp neighbor',
        'BGP_N_G_AR': 'show router bgp neighbor',
        'BGP_N_V': 'show router',
        'BGP_N_V_RR': 'show router',
        'BGP_N_V_AR': 'show router',
        'R_INT': 'show port',
        'R_INT_C': 'show port',
    }
}
