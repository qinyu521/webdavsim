#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from p115 import P115Client, P115FileSystem
import time
import traceback
import os
import re
import sys
import traceback

count=0
failcount=0

fullscan=True

def walk_dir(fs,f,replaceroot):
    dirlist=list()
    try:
        #print("try listdir")
        file_list = fs.listdir_attr()
    except KeyboardInterrupt:
        print("get ctrl+c, exit")
        sys.exit(1)
    except:
        traceback.print_exc()
        time.sleep(1)
        return
    #filetype_re=re.compile(r'\.(png|jpg|jpeg|bmp|gif|doc|nfo|flac|mp3|wma|ape|cue|wav|dst|dff|dts|ac3|eac3|txt|db|pdf)$')
    filetype_re=re.compile(r'\.(png|jpg|jpeg|bmp|gif|doc|nfo|txt|db|pdf)$')
    for file_obj in file_list:
        if not file_obj.is_directory:
            path = file_obj.path
            if filetype_re.search(path) != None or "BDMV" in path:
                continue
            size=int(file_obj.size)
            if size>0 and size<4096:
                continue
            paths = path.split("/")
            if replaceroot!="":
                if len(paths)>=3:
                    path=os.path.join("/",replaceroot,*paths[2:])
                    path=path.replace("\\/","|")

            print(f"{path}\t{file_obj.size}")
            f.write(f"{path}\t{file_obj.size}\n")
            f.flush()
        else:
            dirlist.append(file_obj.path)
    for dirItem in dirlist:
        fs.chdir(dirItem)
        global count
        count=count+1
        if count%3==0:
            time.sleep(1)
        try:
            walk_dir(fs,f,replaceroot)
        except KeyboardInterrupt:
            print("get ctrl+c, exit")
            sys.exit(1)
        except:
            traceback.print_exc()
            time.sleep(1)
    return

def main():
    parser = argparse.ArgumentParser(description='快速遍历115分享目录')
    parser.add_argument('--cookie', type=str, required=True, help='115Cookie')
    parser.add_argument('--url', type=str, required=True, help='115ShareUrl')
    parser.add_argument('--output', type=str, required=True, help='outputfile')
    parser.add_argument('--replaceroot', type=str, default="", required=False, help='替换根目录名称')
    args = parser.parse_args()
    cookie=args.cookie
    shareUrl=args.url
    client=P115Client(cookie)

    if not shareUrl.startswith("http"):
        shareUrl = "https://115.com/s/" + shareUrl

    print("cookie:"+args.cookie+", shareurl:"+shareUrl)
    cidre = re.compile(r'cid=([0-9]+)')
    matches = cidre.findall(shareUrl)
    cid = None
    if len(matches)>0:
        cid=int(matches[0])
        shareUrl = cidre.sub("", shareUrl).replace("?&","?").replace("&&","&")

    fs = client.get_share_fs(shareUrl)

    #if cid != None:
    #    fs.chdir(cid)


    count=0
    f=open(args.output, mode="a", encoding="utf-8")
    walk_dir(fs,f,args.replaceroot)

if __name__ == '__main__':
    main()
