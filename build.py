# Copyright (C) 2020, M.B.Moessner
#
# SPDX-License-Identifier: Apache-2.0 
#

import argparse
from scripts.Utils import *

CTNG_BIN_DIR      = os.getcwd() + "/ctng"
CTNG_BINARY       = os.getcwd() + "/ctng/bin/ct-ng"  
CTNG_REPO         = "https://github.com/crosstool-ng/crosstool-ng"
CTNG_COMMIT_HASH  = "3f461da11f1f8e9dcfdffef24e1982b5ffd10305"


def apply_patches(topDir, srcDir, patchDir):

    patches = sorted(glob.glob(patchDir + "/*.patch"))

    for patch in patches:
        logger.info("Apply patch: {0}".format(patch))
        rela = os.path.relpath(topDir, srcDir)
        relb = os.path.relpath(patchDir, topDir)
        cmd = "patch -p1 < {0}".format(patch)
        run_cmd(cmd, srcDir)

def build_ctng(topDir, ctngSrc):
    logger.info("Boostrap crosstool-ng source")
    cmd = "./bootstrap"
    run_cmd(cmd, ctngSrc)
    cmd_env = os.environ.copy()
    cmd_env["CFLAGS"] = "-DKBUILD_NO_NLS"
    cmd = "./configure --prefix={0}".format(CTNG_BIN_DIR)
    run_cmd(cmd, ctngSrc, env=cmd_env)
    cmd = "make"
    run_cmd(cmd, ctngSrc, env=cmd_env)
    cmd = "make install"
    run_cmd(cmd, ctngSrc, env=cmd_env)


def fetch_ctng(topDir, tmpDir, forceRebuild):

    ctngSrc = tmpDir + "/crosstool-ng"

    if forceRebuild == 1:
        if os.path.exists(CTNG_BIN_DIR):
            shutil.rmtree(CTNG_BIN_DIR, ignore_errors=True)

    
    logger.info("Check if crosstool-ng has already been build...")

    if not os.path.isfile(CTNG_BINARY):
        logger.info("Binary not found")
        
        if os.path.exists(ctngSrc):
            shutil.rmtree(ctngSrc, ignore_errors=True)

        logger.info("Download crosstool-ng source")

        cmd = "git clone {0}".format(CTNG_REPO)
        run_cmd(cmd, tmpDir)

        cmd = "git checkout {0}".format(CTNG_COMMIT_HASH)
        run_cmd(cmd, ctngSrc)

        apply_patches(topDir, ctngSrc ,topDir + "/patches/crosstool-ng")

        build_ctng(topDir, ctngSrc)
  

def build_toolchain(topDir,tmpDir, arch, opsys):

    buildDir =  tmpDir+"/build_" + arch + "_" + opsys
    outputDir =  topDir+"/out_" + arch + "_" + opsys
    cfgInputFile = topDir + "/configs/" + arch + ".config"

    if not os.path.isfile(cfgInputFile):
        logger.error("Configuration for target {0} not found".format(arch))
        sys.exit(-1)

    shutil.copy(cfgInputFile, tmpDir)
    cfgInputFile = tmpDir + "/" + arch + ".config"

    if opsys == "windows":
        f=open(cfgInputFile, "a+")
        f.write("CT_CANADIAN=y\n")
        f.write("CT_HOST=\"x86_64-w64-mingw32\"\n")
        f.close()


    if os.path.exists(buildDir):
        shutil.rmtree(buildDir, ignore_errors=True)
    if os.path.exists(outputDir):
        shutil.rmtree(outputDir, ignore_errors=True)

    os.mkdir(buildDir)

    cmd = "{0} clean".format(CTNG_BINARY)
    run_cmd(cmd, buildDir)
    cmd = "{0} defconfig DEFCONFIG={1}".format(CTNG_BINARY, cfgInputFile)
    run_cmd(cmd, buildDir)
    cmd = "{0} savedefconfig DEFCONFIG={1}.config".format(CTNG_BINARY,arch)
    run_cmd(cmd, buildDir)
    cmd = "{0} build.{1}".format(CTNG_BINARY,psutil.cpu_count())
    run_cmd_ng(cmd, buildDir)



if __name__ == '__main__':
    argParser = argparse.ArgumentParser(description='Open SICK AG SDK')
    optArgs = argParser._action_groups.pop()
    optArgs.add_argument('-a', '--architecture',
                         help="select the target architecture"
                         "(default=arm)",
                         default="arm")
    optArgs.add_argument('-host', '--hostos',
                         help="select the host operating system"
                         "(default=linux)",
                         default="linux")
    
    
    argParser._action_groups.append(optArgs)
    args = argParser.parse_args()
    cwd = os.getcwd()
    tmpDir = cwd + "/tmp"
  
    logger.info("Initialize...")
    logger.info("Current directory: {0}".format(cwd))

    if os.path.exists(tmpDir):
        shutil.rmtree(tmpDir, ignore_errors=True)
    os.mkdir(tmpDir)

    fetch_ctng(cwd,tmpDir,0)

    build_toolchain(cwd,tmpDir,args.architecture,args.hostos)

