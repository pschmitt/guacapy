#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function

RDP_CONNECTION = {
    "name":"",
    "identifier":"",
    "parentIdentifier":"ROOT",
    "protocol":"rdp",
    "attributes": {
        "max-connections":"","max-connections-per-user":""
    },
    "activeConnections":0,
    "parameters": {
        "disable-audio":"",
        "server-layout":"",
        "domain":"",
        "hostname":"",
        "enable-font-smoothing":"",
        "security":"rdp",
        "port":"3389",
        "disable-auth":"",
        "ignore-cert":"",
        "console":"",
        "width":"",
        "height":"",
        "dpi":"",
        "color-depth":"",
        "console-audio":"",
        "enable-printing":"",
        "enable-drive":"",
        "create-drive-path":"",
        "enable-wallpaper":"",
        "enable-theming":"",
        "enable-full-window-drag":"",
        "enable-desktop-composition":"",
        "enable-menu-animations":"",
        "preconnection-id":"",
        "enable-sftp":"",
        "sftp-port":""
    }
}

VNC_CONNECTION = {
    "parentIdentifier": "ROOT",
    "name": "",
    "protocol": "vnc",
    "parameters": {
        "port": "5900",
        "read-only": "",
        "swap-red-blue": "",
        "cursor": "",
        "color-depth": "",
        "clipboard-encoding": "",
        "dest-port": "",
        "create-recording-path": "",
        "enable-sftp": "",
        "sftp-port": "",
        "sftp-server-alive-interval": "",
        "enable-audio": "",
        "hostname": "",
        "password": ""
    },
    "attributes": {
        "max-connections": "",
        "max-connections-per-user": "",
        "weight": "",
        "failover-only": "",
        "guacd-port": "",
        "guacd-encryption": "",
        "guacd-hostname": ""
    }
}

SSH_CONNECTION = {
    'activeConnections': 0,
    'attributes': {
        'max-connections': '',
        'max-connections-per-user': ''
    },
    'identifier': '',
    'name': '',
    'parameters': {
        'hostname': '',
        'password': '',
        'port': '22',
        'username': ''
    },
    'parentIdentifier': 'ROOT',
    'protocol': 'ssh'
}

USER = {
    'username': '',
     'password': '',
     'attributes':  {
        'disabled': '',
        'expired': '',
        'access-window-start': '',
        'access-window-end': '',
        'valid-from': '',
        'valid-until': '',
        'timezone': ''
    }
}

ORG_CONNECTION_GROUP = {
    "parentIdentifier":"ROOT",
    "name":"",
    "type":"ORGANIZATIONAL",
    "attributes":{
        "max-connections":"",
        "max-connections-per-user":""
    }
}

SYSTEM_PERMISSIONS=[{"op":"add","path":"/systemPermissions","value":"ADMINISTER"}]

ADD_READ_PERMISSION={"op": "add", "path": "", "value": "READ"}
