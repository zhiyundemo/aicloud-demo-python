import requests
import os
import json
import time

from utils.AuthV4Util import addAuthParams

# 您的应用ID
APP_KEY = ''
# 您的应用密钥
APP_SECRET = ''

# 待转写的音频文件路径，例 windows 路径：PATH = "C:\\youdao\\media.jpg"
PATH = ''
# 单个文件分片大小 : 10M
SLICE_SIZE = 10485760

def createRequest():
    # 计算文件分片数量
    file_len = os.path.getsize(PATH)
    slice_num = int(file_len / SLICE_SIZE) + (0 if(file_len % SLICE_SIZE == 0) else 1)

    # 1、预处理
    prepare_result = prepareHelper(file_len, slice_num)
    print('prepase_result:' + prepare_result)
    prepare_result_json = json.loads(prepare_result)
    if(prepare_result_json["errorCode"] != "0"):
        exit(0)
    taskId = prepare_result_json["result"]

    # 2、对文件进行分片并上传
    file = open(PATH, 'rb')
    try:
        sliceId = 1
        while True:
            content = file.read(SLICE_SIZE)
            if not content or len(content) == 0:
                break
            files = {'file': content}
            upload_result = uploadHelper(taskId, sliceId, files)
            print('upload_result:' + upload_result + '  sliceId:' + str(sliceId))
            upload_result_json = json.loads(upload_result)
            if(upload_result_json["errorCode"] != "0"):
                exit(0)
            sliceId += 1
    finally:
        file.close()

    # 3、合并文件
    merge_result = mergeHelper(taskId)
    print('merge_result:' + merge_result)
    merge_result_json = json.loads(merge_result)
    if(merge_result_json["errorCode"] != "0"):
        exit(0)

    # 4、查看转写进度
    while True:
        print('sleep a while')
        time.sleep(20)
        get_process_result = getProcessHelper(taskId)
        print('get_process_result:' + get_process_result)
        get_process_result_json = json.loads(get_process_result)
        if(get_process_result_json["errorCode"] == "0"):
            result = get_process_result_json["result"]
            item = result[0]
            if(item["status"] == "9"):
                print('任务处理成功')
                break
        else:
            print('任务处理失败')
            exit(0)

    # 5、获取结果
    get_result_result = getResultHelper(taskId)
    print('get_result_result:' + get_result_result)

def getResultHelper(taskId):
    data = {'q': taskId}
    addAuthParams(APP_KEY, APP_SECRET, data)
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = doCall('https://openapi.youdao.com/api/audio/get_result', header, data, 'post')
    return str(res.content, 'utf-8')

def getProcessHelper(taskId):
    data = {'q': taskId}
    addAuthParams(APP_KEY, APP_SECRET, data)
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = doCall('https://openapi.youdao.com/api/audio/get_progress', header, data, 'post')
    return str(res.content, 'utf-8')

def mergeHelper(taskId):
    data = {'q': taskId}
    addAuthParams(APP_KEY, APP_SECRET, data)
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = doCall('https://openapi.youdao.com/api/audio/merge', header, data, 'post')
    return str(res.content, 'utf-8')

def uploadHelper(taskId, sliceId, file):
    type = '1'
    data = {'q': taskId, 'sliceId': sliceId, 'type': type, 'file': file}
    addAuthParams(APP_KEY, APP_SECRET, data)
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = requests.post('https://openapi.youdao.com/api/audio/upload', data, files = file)
    return str(res.content, 'utf-8')

def prepareHelper(file_len, slice_num):
    '''
    note: 将下列变量替换为需要请求的参数
    取值参考文档：https://ai.youdao.com/DOCSIRMA/html/tts/api/cyyzx/index.html
    '''
    lang_type = '音频文件对应的语种'
    name = os.path.basename(PATH)
    format = os.path.splitext(PATH)[-1][1:]
    type = '1'

    data = {'name': name, 'format': format, 'langType': lang_type, 'sliceNum': str(slice_num), 'fileSize': str(file_len), 'type': type}
    addAuthParams(APP_KEY, APP_SECRET, data)

    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = doCall('https://openapi.youdao.com/api/audio/prepare', header, data, 'post')
    return str(res.content, 'utf-8')

def doCall(url, header, params, method):
    if 'get' == method:
        return requests.get(url, params)
    elif 'post' == method:
        return requests.post(url, params, header)

# 网易有道智云长语音转写服务api调用demo
if __name__ == '__main__':
    createRequest()