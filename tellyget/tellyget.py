from tellyget.auth import Auth
from tellyget.guide import Guide

import argparse

parser = argparse.ArgumentParser(description='Generate iptv configs')

parser.add_argument('-u', '--user', type=str, required=True, help='user name for login')
parser.add_argument('-p', '--passwd', type=str, required=True, help='password for login')
parser.add_argument('-m', '--mac', type=str, required=True, help='MAC of box')
parser.add_argument('-i', '--imei', type=str, default='', help='imei of box (STBID in ValidAuthenticationHWCTC.jsp request form)')
parser.add_argument('-a', '--address', type=str, default='', help='IP address of box')
parser.add_argument('-I', '--interface', type=str, help='interface of iptv')
parser.add_argument('-U', '--authurl', type=str, default='http://itvbf.zj.vnet.cn:8082/EDS/jsp/AuthenticationURL', help='authenticate url')
parser.add_argument('-o', '--output', type=str, default='./', help='iptv.m3u8 and egp.xml output path')
parser.add_argument('-f', '--filter', nargs='+', default=['^\d+$'], help='channel filter')
parser.add_argument('-A', '--all-channel', default=False, action='store_true', help='no filter sd channels')
parser.add_argument('-v', '--soft-version', type=str, default='A6.13.06', help='Software version of box')
parser.add_argument('-M', '--model', type=str, default='TY1613', help='Model of box (STBType)')
parser.add_argument('-g', '--igmpProxy', type=str, default='',  help='igmp proxy prefix')


def main():
    args = parser.parse_args()
    print(args)
    auth = Auth(args)
    auth.authenticate()
    guide = Guide(args, auth)
    guide.save()
