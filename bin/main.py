#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import configparser
from pathlib import PurePath
import os
from datetime import date
from datetime import datetime
import jmespath
import json
import hashlib
import requests


def jsonclean(o):
    if isinstance(o, datetime):
        return o.__str__()


def list(folder):
    res = []
    for path, _, files in os.walk(folder):
        for name in files:
            res.append(PurePath(path, name))
    return res


def rename_keys(uniquekeys, jsonmap):
    tmp = {}
    for key in jsonmap.keys():
        if key in uniquekeys:
            tmp[key[2:]] = jsonmap[key]
        else:
            tmp[key] = jsonmap[key]
    return tmp


if __name__ == '__main__':

    today = date.today()
    config = configparser.RawConfigParser()
    config.read('etc/ail-feeder-jsonlogs.cfg')

    ailfeedertype = 'ail-feeder-jsonlogs-default'
    uuid = '731fefaf-8284-4cb4-9504-039297fed802'
    if 'ail' in config:
        ailfeedertype = config['ail']['ailfeedertype']
        uuid = config['ail']['uuid']

    basedir = ''
    prefix = ''
    datepattern = '%Y%m%d'
    suffix = ''
    if 'folder' in config:
        pattern = config['folder']['datepattern']
        basedir = config['folder']['basedir']
        suffix = config['folder']['suffix']
        prefix = config['folder']['prefix']
    selector = ''
    if 'selector' in config:
        selector = config['selector']['selector']
        selector = selector.strip('"')

    files = list(basedir + '/' + prefix + today.strftime(datepattern) + suffix)
    query = jmespath.compile(selector)

    # Searching for the unique keys
    with open(files[0]) as fd:
        jsonmap = query.search(json.load(fd))
        uniquekeys = [jsonmap for jsonmap, val in jsonmap.items() if 'u_' in jsonmap]

    # Building the dict of unique keys to flatten the whole thing
    uniqueset = {}
    for file in files:
        with open(file) as fd:
            jsonmap = query.search(json.load(fd))
            tmp = [({jsonmap[key] for key in uniquekeys})]
            fset = frozenset(tmp[0])
            uniqueset[fset] = rename_keys(uniquekeys, jsonmap)

    # Building ail items from transformed dataset
    for fzkey, jsmap in uniqueset.items():
        output_item = {}
        output_item['source'] = ailfeedertype
        output_item['source-uuid'] = uuid
        output_item['default-encoding'] = 'UTF-8'
        # The whole json line becomes the data
        m = hashlib.sha256()
        m.update(json.dumps(jsmap).encode('utf-8'))
        output_item['data-sha256'] = m.hexdigest()
        # Each key becomes a meta if --meta was specified
        output_item['data'] = {}
        for k, v in jsmap.items():
            output_item['data'][k] = v

    # Sending to AIL
    print(json.dumps(output_item, indent=4, sort_keys=True, default=jsonclean))
    response = requests.post(config['ail']['url'],
                             headers={'Content-Type': 'application/json', 'Authorization': config['ail']['apikey']},
                             data=json.dumps(output_item, indent=4, sort_keys=True, default=jsonclean), verify=False)
