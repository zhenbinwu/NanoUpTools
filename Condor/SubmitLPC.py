#!/usr/bin/env python
# coding: utf-8

import os
import re
import time
import subprocess
import glob
import tarfile
import shutil
import getpass
import argparse
from collections import defaultdict

DelExe    = '../test/test_processor.py'
# OutDir = '/store/user/%s/Phase2L1/JetPerf/' %  getpass.getuser()
# OutDir = '/store/user/%s/Stop19/QCDHEMStudy/' %  getpass.getuser()
OutDir = '/store/user/%s/Stop19/PUWeightfiles' %  getpass.getuser()
tempdir = '/uscmst1b_scratch/lpc1/3DayLifetime/benwu/TestCondor/'
ProjectName = 'PU_v5'
argument = "--inputFiles=%s.$(Process).list --outputFile=%s_$(Process).root"
# argument = "--inputFiles=%s.$(Process).list --outputFile=%s_$(Process).root --jettype=L1PuppiJets"
defaultLperFile = 2000

Process = {
    # "QCD_Good"             : ["Filelist/QCD_Good.list",        5],
    # "QCD_HEM"              : ["Filelist/QCD_HEM.list",         5],
    # "T1bbbb_1500_100" : ["Filelist/T1bbbb_1500_100.list", 3],
    # "T1tttt_2000_100" : ["Filelist/T1tttt_2000_100.list", 3],
    # "T2tt_1200_100"   : ["Filelist/T2tt_1200_100.list",   3],
    # "T2tt_850_100"    : ["Filelist/T2tt_850_100.list",    3],
    "TTbar_PU200"    : ["Filelist/P2L1Jets.list",    250],

}

def tar_cmssw():
    print("Tarring up CMSSW, ignoring file larger than 100MB")
    cmsswdir = os.environ['CMSSW_BASE']
    cmsswtar = os.path.abspath('%s/CMSSW.tar.gz' % tempdir)
    if os.path.exists(cmsswtar):
        ans = raw_input('CMSSW tarball %s already exists, remove? [yn] ' % cmsswtar)
        if ans.lower()[0] == 'y':
            os.remove(cmsswtar)
        else:
            return cmsswtar

    def exclude(tarinfo):
        if tarinfo.size > 100*1024*1024:
            tarinfo = None
            return tarinfo
        exclude_patterns = ['/.git/', '/tmp/', '/jobs.*/', '/logs/', '/.SCRAM/', '.pyc']
        for pattern in exclude_patterns:
            if re.search(pattern, tarinfo.name):
                # print('ignoring %s in the tarball', tarinfo.name)
                tarinfo = None
                break
        return tarinfo

    with tarfile.open(cmsswtar, "w:gz") as tar:
        tar.add(cmsswdir, arcname=os.path.basename(cmsswdir), filter=exclude)
    return cmsswtar

def Condor_Sub(condor_file):
    curdir = os.path.abspath(os.path.curdir)
    os.chdir(os.path.dirname(condor_file))
    print "To submit condor with " + condor_file
    os.system("condor_submit " + condor_file)
    os.chdir(curdir)


def SplitPro(key, file, lineperfile=20):
    splitedfiles = []
    filelistdir = tempdir + '/' + "FileList"
    try:
        os.makedirs(filelistdir)
    except OSError:
        pass

    filename = os.path.abspath(file)

    f = open(filename, 'r')
    lines = f.readlines()

    if len(lines) <= lineperfile:
        shutil.copy2(os.path.abspath(filename), "%s/%s.0.list" % (filelistdir, key))
        splitedfiles.append(os.path.abspath("%s/%s.0.list" % (filelistdir, key)))
        return splitedfiles

    fraction = len(lines) / lineperfile
    if len(lines) % lineperfile > 0:
        fraction += 1

    for i in range(0, fraction):
        wlines = []
        if i == fraction - 1 :
            wlines = lines[lineperfile*i :]
        else:
            wlines = lines[lineperfile*i : lineperfile*(i+1)]
        if len(wlines) > 0:
            outf = open("%s/%s.%d.list" % (filelistdir, key, i), 'w')
            outf.writelines(wlines)
            splitedfiles.append(os.path.abspath("%s/%s.%d.list" % (filelistdir, key, i)))
        outf.close()

    return splitedfiles

def my_process(args):
    ## temp dir for submit
    global tempdir
    global ProjectName
    global Process
    ProjectName = time.strftime('%b%d') + ProjectName
    tempdir = tempdir + os.getlogin() + "/" + ProjectName +  "/"
    try:
        os.makedirs(tempdir)
    except OSError:
        pass

    ## Create the output directory
    outdir = OutDir +  "/" + ProjectName + "/"
    try:
        os.makedirs("/eos/uscms/%s" % outdir)
    except OSError:
        pass

    ## Update RunHT.csh with DelDir and pileups
    RunHTFile = tempdir + "/" + "RunExe.csh"
    with open(RunHTFile, "wt") as outfile:
        for line in open("RunExe.csh", "r"):
            #line = line.replace("DELDIR", os.environ['PWD'])
            line = line.replace("DELSCR", os.environ['SCRAM_ARCH'])
            line = line.replace("DELDIR", os.environ['CMSSW_VERSION'])
            line = line.replace("DELEXE", DelExe.split('/')[-1])
            line = line.replace("OUTDIR", outdir)
            outfile.write(line)

    ### Create Tarball
    NewNpro = {}
    Tarfiles = []
    if args.config != "":
        Process = ConfigList(os.path.abspath(args.config))
    for key, value in Process.items():
        if value[0] == "":
            value[0] = "../FileList/"+key+".list"
        if not os.path.isfile(value[0]):
            continue
        npro = GetProcess(key, value)
        Tarfiles+=npro
        NewNpro[key] = len(npro)
    Tarfiles+=glob.glob("../*py")

    tarballnames = []

    Tarfiles.append(os.path.abspath(DelExe))
    tarballname ="%s/%s.tar.gz" % (tempdir, ProjectName)
    with tarfile.open(tarballname, "w:gz", dereference=True) as tar:
        [tar.add(f, arcname=f.split('/')[-1]) for f in Tarfiles]
        tar.close()
    tarballnames.append(tarballname)
    tarballnames.append(tar_cmssw())
    tarballnames.append("/uscms/home/benwu/python-packages.tgz")

    ### Update condor files
    for key, value in Process.items():
        arg = "\nArguments = " + argument % (key, key) + "\n Queue %d \n" % NewNpro[key]

        ## Prepare the condor file
        condorfile = tempdir + "/" + "condor_" + ProjectName +"_" + key
        with open(condorfile, "wt") as outfile:
            for line in open("condor_template", "r"):
                line = line.replace("EXECUTABLE", os.path.abspath(RunHTFile))
                line = line.replace("TARFILES", ", ".join(tarballnames))
                line = line.replace("TEMPDIR", tempdir)
                line = line.replace("PROJECTNAME", ProjectName)
                line = line.replace("ARGUMENTS", arg)
                outfile.write(line)

        Condor_Sub(condorfile)

def GetProcess(key, value):
    if len(value) == 1:
        return SplitPro(key, value[0], 1)
    else :
        return SplitPro(key, value[0], value[1])

def ConfigList(config):
    process = defaultdict(list)
    lines = open(config).readlines()
    for line_ in lines:
        line = line_.strip()
        if(len(line) <= 0 or line[0] == '#'):
            continue
        entry = line.split(",")
        stripped_entry = [ i.strip() for i in entry]
        process[stripped_entry[0]] = ["%s/%s" % (stripped_entry[1], stripped_entry[2]), defaultLperFile]
    return process

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='NanoAOD postprocessing.')
    parser.add_argument('-c', '--config',
        default = "",
        help = 'Path to the input config file.')
    args = parser.parse_args()
    my_process(args)


