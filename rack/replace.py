#!/usr/bin/python3

import fileinput
import sys
import json
import shutil
import subprocess
import glob
import os
import argparse

rack_version = '2'

parser = argparse.ArgumentParser(description='Personal information')

parser.add_argument('--spec-template', dest='spec_template', type=str, default='template.spec', help='Path to the template file')
parser.add_argument('--spec-dir', dest='spec_dir', type=str, default='spec', help='Path to the directory where to write specs')
parser.add_argument('--library', dest='library_dir', type=str, default='library', help='Path to the community git repository')
parser.add_argument('--plugin', dest='plugin_name', type=str, default=None, help='A name of plugin to process')

args = parser.parse_args()

# Static data which overrides the ones found in VCV Rack library files
static_values = {
    "ArableInstruments": {
        "sourceUrl": r"https://github.com/adbrant/ArableInstruments",
        "source1": "ArableInstruments.tar.gz",
    },
    "AudibleInstruments": {
        "source1": "AudibleInstruments.tar.gz",
    },
    "AuraAudio": {
        "sourceUrl": r"https://github.com/emurray2/auraaudio-vcv-rack",
        "source1": r"https://github.com/emurray2/auraaudio-vcv-rack/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz",
    },
    "BaconMusic": {
        "source1": "BaconPlugs.tar.gz",
    },
    "CharredDesert": {
        "source1": "CharredDesert.tar.gz",
    },
    "DrumKit": {
        "source1": "DrumKit.tar.gz",
    },
    "ErraticInstruments": {
        "source1": "Erratic.tar.gz",
    },
    "HamptonHarmonics": {
        "source1": r"https://gitlab.com/hampton-harmonics/hampton-harmonics-modules/-/archive/%{commit0}/%{name}-%{shortcommit0}.tar.gz",
    },
    "HolonicSystems-Free": {
        "vcvrackcxxflags": "-include cstdio ",
    },
    "ImpromptuModular": {
        "vcvrackcxxflags": "-include limits ",
    },
    "JE": {
        "source1": "VCVRack-plugin-JE.tar.gz",
        "vcvrackcxxflags": "-include limits ",
    },
    "ODDSound_MTS_ESP": {
        "sourceUrl": r"https://oddsound.com",
        "source1": r"https://github.com/ODDSound/MTS-ESP-VCVRack/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz",
    },
    "ParableInstruments": {
        "source1": "ArableInstruments.tar.gz",
    },
    "SA-Seasons": {
        "sourceUrl": r"https://github.com/SpektroAudio/Seasons",
        "source1": r"https://github.com/SpektroAudio/Seasons/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz",
    },
    "SonusModular": {
        "sourceUrl": r"https://gitlab.com/sonusdept/sonusmodular",
        "source1": r"https://gitlab.com/sonusdept/sonusmodular/-/archive/%{commit0}/%{name}-%{shortcommit0}.tar.gz",
    },
    "Southpole": {
        "source1": "southpole-vcvrack.tar.gz",
    },
    "SurgeRack": {
        "source1": "surge-rack.tar.gz",
    },
    "TheXOR": {
        "vcvrackcxxflags": "-include limits ",
    },
    "moDllz": {
        "source1": r"https://github.com/dllmusic/moDllz/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz",
    },
    "luckyxxl": {
        "vcvrackcxxflags": "-include limits ",
    },
    "modular80": {
        "source1": "modular80.tar.gz",
    },
    "rcm": {
        "vcvrackcxxflags": "-include limits ",
    },
    "unless_modules": {
        "sourceUrl": r"http://gitlab.com/unlessgames/unless_modules",
        "source1": r"http://gitlab.com/unlessgames/unless_modules/-/archive/%{commit0}/%{name}-%{shortcommit0}.tar.gz",
    },
    "voxglitch": {
        "vcvrackcxxflags": "-include algorithm -include limits ",
    },
}

# this script must be started a level before the 'library' rack repo
# A directory 'spec' with a file 'template.spec' containing the tag SLUGNAME, VERSION, COMMITID and SOURCEURL must be created

def get_git_revision_hash(git_path):
    curr_path = os.getcwd()
    os.chdir(git_path)
    commit_id = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode("utf-8")
    os.chdir(curr_path)
    return commit_id.rstrip()

def proceed(json_file):
    # read json file
    # skip some files:
    if 'Core.json' in json_file:
        return
    if 'VCV-Prototype.json' in json_file:
        return
    if 'settings.json' in json_file:
        return
    
    print(f'Reading {json_file} json library file\n')
    
    with open(json_file, 'r') as fjson:
        conf_rack = json.load(fjson)
        if 'license' in conf_rack and conf_rack['license'] in ('proprietary', 'Proprietary', 'PROPRIETARY'):
            print('Proprietary license\n')
            return

        slug_name   = conf_rack['slug']
        version     = conf_rack['version']
        if 'sourceUrl' in conf_rack:
            if slug_name in static_values and 'sourceUrl' in static_values[slug_name]:
                sourceurl = static_values[slug_name]['sourceUrl']
            else:
                sourceurl = conf_rack['sourceUrl'].replace('.git','') # remove the trailing '.git'
        else:
            sourceurl = ''
        
        source1     = r'{}/archive/%{{commit0}}.tar.gz#/%{{name}}-%{{shortcommit0}}.tar.gz'.format(sourceurl)
        if slug_name in static_values and 'source1' in static_values[slug_name]:
            source1 = static_values[slug_name]['source1']

        vcvrackcxxflags = ''
        if slug_name in static_values and 'vcvrackcxxflags' in static_values[slug_name]:
            vcvrackcxxflags = static_values[slug_name]['vcvrackcxxflags']

        description = ''
        if 'modules' in conf_rack and 'description' in conf_rack['modules'][0]:
            description = conf_rack['modules'][0]['description']

        if not os.path.exists(args.spec_dir + os.sep + args.spec_template):
            print('template file not found in {}\n'.format(args.spec_dir + os.sep))
            sys.exit(-1)
        
        if not os.path.exists(args.library_dir + os.sep + 'repos' + os.sep + slug_name):
            print('repos slug_name doesn\'t exists\n')
            return
        
        commit_id = get_git_revision_hash(args.library_dir + os.sep + 'repos' + os.sep + slug_name)

        print(f'SLUGNAME    -> {slug_name}\n')
        print(f'VERSION     -> {version}\n')
        print(f'SOURCEURL   -> {sourceurl}\n')
        print(f'SOURCE1     -> {source1}\n')
        print(f'COMMITID    -> {commit_id}\n')
        print(f'DESCRIPTION -> {description}\n')
        
        spec_filename = f'rack-v{rack_version}-library-{slug_name}.spec'
        
        # copy template into spec file
        shutil.copyfile(args.spec_dir + os.sep + args.spec_template, args.spec_dir + os.sep + spec_filename)
        # copy json file into spec dire
        shutil.copyfile(json_file, args.spec_dir + os.sep + slug_name + '_plugin.json')
        
        #with fileinput.FileInput(args.spec_dir + os.sep + spec_filename, inplace=True, backup='.bak') as file:
        with fileinput.FileInput(args.spec_dir + os.sep + spec_filename, inplace=True) as file:
            for line in file:
                if 'SLUGNAME' in line:
                    print(line.replace('SLUGNAME',  slug_name), end='')
                elif 'VERSION' in line:
                    print(line.replace('VERSION',   version), end='')
                elif 'COMMITID' in line:
                    print(line.replace('COMMITID',  commit_id), end='')
                elif 'SOURCEURL' in line:
                    print(line.replace('SOURCEURL', sourceurl), end='')
                elif 'SOURCE1' in line:
                    print(line.replace('SOURCE1', source1), end='')
                elif 'VCVRACKCXXFLAGS' in line:
                    print(line.replace('VCVRACKCXXFLAGS', vcvrackcxxflags), end='')
                elif 'DESCRIPTION' in line:
                    if description:
                        print(line.replace('DESCRIPTION', description), end='')
                elif 'JSONFILE' in line:
                    print(line.replace('JSONFILE', slug_name + '_plugin.json'), end='')
                else:
                    print(line, end='')
    
if __name__ == "__main__":
    if len(sys.argv) != 1:
        proceed(args.library_dir + os.sep + 'manifests' + os.sep + args.plugin_name + '.json')
    else:
        # we iterate through library/manifests/*.json and we generate spec/*.spec
        for json_file in glob.glob(args.library_dir + os.sep + 'manifests' + os.sep + '*.json'):
            proceed(json_file)
