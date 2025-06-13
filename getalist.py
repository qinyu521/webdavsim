#!/usr/bin/env python
# -*- coding: utf- -*-

import argparse
import os
import time
import re
import requests
import traceback
import json
import sys

count=0

failcount=0

fullscan=True

def walk(headers:dict, api_url:str, current_path="/", output_file=None, replaceroot=None, lastpath=None):
    params = {"path": current_path}
    #print(f"params:{params}")
    try:
        resp = requests.post(
            api_url+"/api/fs/list",
            headers=headers,
            json=params,
            stream=True,
            timeout=(5,15),
        )
    except KeyboardInterrupt:
        print("get ctrl+c, exit")
        sys.exit(1)
    except:
        traceback.print_exc()
        print(f"request fail to server:{api_url}")
        time.sleep(1)
        #sys.exit(1)
        return
    resp.raise_for_status()
    body = resp.content.decode('utf-8')
    resp.close()
    # 解析 JSON 数据
    data_dict = json.loads(body)

    # 获取 raw_url
    global failcount
    try:
        items = data_dict['data']['content']
        failcount=0
    except:
        traceback.print_exc()
        time.sleep(1)
        #sys.exit(1)
        failcount += 1
        if failcount>10:
            sys.exit(1)
        return

    print(f"contentlist len:{len(items)}")
    # items=client.list(current_path)

    filetype_re=re.compile(r'\.(png|jpg|jpeg|bmp|gif|doc|nfo|flac|mp3|wma|ape|cue|wav|dst|dff|dts|ac3|eac3|txt|db|pdf)$')
    # print(items)
    for item in items:
        full_path = f"{current_path}/{item['name']}".replace("//", "/")
        try:
            # is_dir = client.is_dir(full_path)
            # is_dir = full_path.endswith("/")
            is_dir = item["is_dir"]
        except:
            continue
        global fullscan
        # print(f"fullscan:{fullscan}, full_path:{full_path}, lastpath:{lastpath}")
        if is_dir:  # 判断是否为目录
            global count
            count=count+1
            if fullscan:
                if count%2==0:
                    time.sleep(1)
            #else:
            #    if count%10==0:
            #        time.sleep(1)
            if not fullscan and not full_path in lastpath:
                print(f"not fullscan and full_path:{full_path} not in lastpath:{lastpath}, skip")
                continue
            if full_path == lastpath:
                print(f"found full_path:{full_path} equal lastpath:{lastpath}, enter fullscan mode")
                time.sleep(3)
                fullscan = True
            try:
                walk(headers, api_url, full_path, output_file, replaceroot, lastpath)
            except KeyboardInterrupt:
                print("get ctrl+c, exit")
                sys.exit(1)
            except:
                traceback.print_exc()
                #sys.exit(1)
                pass
        elif not fullscan:
            continue
        else:
            if filetype_re.search(full_path) != None or "BDMV" in full_path:
                continue
            # size = client.info(full_path).get('size', 0)
            size = int(item["size"])
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
    parser = argparse.ArgumentParser(description='快速遍历AList目录')
    parser.add_argument('--url', type=str, required=True, help='AList URL')
    parser.add_argument('--token', type=str, default=None, required=False, help='AList token')
    parser.add_argument('--output', type=str, required=True, help='输出文件')
    parser.add_argument('--lastpath', type=str, default=None, required=False, help='最后扫到的路径（从此开始继续）')
    parser.add_argument('--replaceroot', type=str, default=None, required=False, help='替换根目录名称')
    args = parser.parse_args()

    schema, hostname, path = extract_url_components(args.url)
    print(schema,hostname,path)

    print("AList URL:", args.url)
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
        args.lastpath=args.lastpath.rstrip('/')
    print(f"lastpath:{args.lastpath}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
    }
    if args.token != None and args.token != "":
        headers["Authorization"] = args.token
    walk(headers, schema+"://"+hostname, path, output_file,args.replaceroot, args.lastpath)
    output_file.close()

if __name__ == '__main__':
    main()
