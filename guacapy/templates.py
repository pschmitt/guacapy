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

ORG_CONNECTION_GROUP = {
    "parentIdentifier":"1",
    "name":"",
    "type":"ORGANIZATIONAL",
    "attributes":{
        "max-connections":"",
        "max-connections-per-user":""
    }
}

SYSTEM_PERMISSIONS=[{"op":"add","path":"/systemPermissions","value":"ADMINISTER"}]
