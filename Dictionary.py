driver_dict = {'Cisco': 'cisco_ios', 'OpenSSH': 'alcatel_sros'}

cmd_dict = {
    'cisco_ios': {
        'BGP_G_IP': 'show ip bgp ipv4 unicast neighbor',
        'BGP_G_RR_IP': 'show ip bgp ipv4 unicast neighbor',
        'BGP_G_AR_IP': 'show ip bgp ipv4 unicast neighbor',
        'BGP_G_AS': 'show ip bgp ipv4 unicast',
        'BGP_G_RR_AS': 'show ip bgp ipv4 unicast',
        'BGP_G_AR_AS': 'show ip bgp ipv4 unicast',
        'BGP_V_IP': 'show ip bgp vpnv4 vrf',
        'BGP_V_RR_IP': 'show ip bgp vpnv4 vrf',
        'BGP_V_AR_IP': 'show ip bgp vpnv4 vrf',
        'BGP_V_AS': 'show ip bgp vpnv4 vrf',
        'BGP_V_RR_AS': 'show ip bgp vpnv4 vrf',
        'BGP_V_AR_AS': 'show ip bgp vpnv4 vrf',
        'GRX_ARP_IP': 'show ip arp vrf',
        'GRX_BGP_N_AS': 'show ip bgp vpnv4 vrf',
        'GRX_BGP_N_IP': 'show ip bgp vpnv4 vrf',
        'GRX_BGP_N_RR_IP': 'show ip bgp vpnv4 vrf',
        'GRX_BGP_N_AR_IP': 'show ip bgp vpnv4 vrf',
        'GRX_BGP_R_AS': 'show ip bgp vpnv4 vrf',
        'GRX_RTF': 'show ip bgp vpnv4 vrf',
        'R_INT': 'show interface',
        'R_INT_C': 'show interface',

    },
    'alcatel_sros': {
        'BGP_G_IP': 'show router bgp neighbor',
        'BGP_G_RR_IP': 'show router bgp neighbor',
        'BGP_G_AR_IP': 'show router bgp neighbor',
        'BGP_G_AS': 'show router bgp neighbor',
        'BGP_G_RR_AS': 'show router bgp neighbor',
        'BGP_G_AR_AS': 'show router bgp neighbor',
        'BGP_V_IP': 'show router',
        'BGP_V_RR_IP': 'show router',
        'BGP_V_AR_IP': 'show router',
        'BGP_V_AS': 'show router',
        'BGP_V_RR_AS': 'show router',
        'BGP_V_AR_AS': 'show router',
        'GRX_ARP_IP': 'show router',
        'GRX_BGP_N_AS': 'show router',
        'GRX_BGP_N_IP': 'show router',
        'GRX_BGP_N_RR_IP': 'show router',
        'GRX_BGP_N_AR_IP': 'show router',
        'GRX_BGP_R_AS': 'show router',
        'GRX_RTF': 'show router',
        'R_INT': 'show port',
        'R_INT_C': 'show port',
    }
}
