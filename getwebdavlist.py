#!/usr/bin/env python
# -*- coding: utf- -*-

import argparse
from webdav3.client import Client
import os
import time
import re
import sys
import traceback

count=0
failcount=0

fullscan=True

def walk(client, current_path="/", output_file=None, replaceroot=None, lastpath=None):
    global failcount
    try:
        items=client.list(current_path)
        failcount=0
    except KeyboardInterrupt:
        print("get ctrl+c, exit")
        sys.exit(1)
    except:
        traceback.print_exc()
        time.sleep(1)
        failcount+=1
        if failcount>10:
            sys.exit(1)
        return
    filetype_re=re.compile(r'\.(png|jpg|jpeg|bmp|gif|doc|nfo|flac|mp3|wma|ape|cue|wav|dst|dff|dts|ac3|eac3|txt|db|pdf)$')
    # print(items)
    for item in items[1:]:
        full_path = f"{current_path}/{item}".replace("//", "/")
        try:
            # is_dir = client.is_dir(full_path)
            is_dir = full_path.endswith("/")
        except:
            continue
        global fullscan
        # print(f"fullscan:{fullscan}, full_path:{full_path}, lastpath:{lastpath}")
        if is_dir:  # 判断是否为目录
            #global count
            #count=count+1
            #if count%4==0:
            #    time.sleep(1)
            if not fullscan and not full_path in lastpath:
                continue
            if full_path == lastpath:
                fullscan = True
            try:
                walk(client, full_path, output_file, replaceroot, lastpath)
            except KeyboardInterrupt:
                print("get ctrl+c, exit")
                sys.exit(1)
            except:
                time.sleep(1)
                #sys.exit(1)
                pass
        elif not fullscan:
            continue
        else:
            if filetype_re.search(full_path) != None or "BDMV" in full_path:
                continue
            size = int(client.info(full_path).get('size', 0))
            if size>0 and size<4096:
                continue
            if replaceroot!=None:
                if replaceroot=="":
                    full_path=os.path.join("/",*full_path.split("/")[2:])
                else:
                    full_path=os.path.join("/",replaceroot,*full_path.split("/")[2:])
                full_path=full_path.replace("\\/","|")
            print(f"{full_path}\t{size}")
            if output_file != None:
                output_file.write(f"{full_path}\t{size}\n")
                output_file.flush()


from urllib.parse import urlparse

def extract_url_components(url):
    """分解 URL 为 schema（协议）、hostname（主机地址）、path（路径）"""
    parsed = urlparse(url)

    # 提取核心组件
    schema = parsed.scheme or "http"  # 默认协议处理
    hostname = f"{parsed.hostname}:{parsed.port}"        # 自动过滤端口和认证信息
    path = parsed.path.rstrip('/') or '/'  # 路径标准化

    return schema, hostname, path


def main():
    parser = argparse.ArgumentParser(description='快速遍历WebDAV目录')
    parser.add_argument('--url', type=str, required=True, help='WebDAV URL')
    parser.add_argument('--username', type=str, required=True, help='WebDAV username')
    parser.add_argument('--password', type=str, required=True, help='WebDAV password')
    parser.add_argument('--output', type=str, required=True, help='输出文件')
    parser.add_argument('--lastpath', type=str, default=None, required=False, help='最后扫到的路径（从此开始继续）')
    parser.add_argument('--replaceroot', type=str, default=None, required=False, help='替换根目录名称')
    args = parser.parse_args()

    schema, hostname, path = extract_url_components(args.url)
    print(schema,hostname,path)

    options = {
        'webdav_hostname': schema+"://"+hostname,
        'webdav_root': '/',
        'webdav_login': args.username,
        'webdav_password': args.password,
        'disable_check': True,  # 跳过 SSL 证书验证:ml-citation{ref="6" data="citationList"}
        'disable_head': True,  # 跳过 SSL 证书验证:ml-citation{ref="6" data="citationList"}
    }
    client = Client(options)

    print("WebDAV URL:", args.url)
    if args.lastpath == None:
        try:
            with open(args.output, "r", encoding="utf-8") as f:
                tmplines = f.readlines()
                for i in range(len(tmplines)-1, -1, -1):
                    line=tmplines[i].strip()
                    if line != None and line != "":
                        args.lastpath = os.path.dirname(line.split("\t")[0])
                        break
        except:
            traceback.print_exc()
    output_file = open(args.output, mode="a", encoding="utf-8")
    if args.lastpath != None and args.lastpath != "":
        global fullscan
        fullscan = False
    if args.lastpath != None:
        if not args.lastpath.endswith("/"):
            args.lastpath = args.lastpath+"/"
    print(f"lastpath:{args.lastpath}")
    walk(client, path, output_file,args.replaceroot, args.lastpath)
    output_file.close()

if __name__ == '__main__':
    main()
