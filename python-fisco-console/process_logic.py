from client_config import client_config
from client.bcosclient import (
    BcosClient,
    BcosError
)
import os
from client.common.compiler import Compiler
from eth_utils import to_checksum_address
from client.datatype_parser import DatatypeParser

import json
import time
import hashlib
import datetime

client = BcosClient()
info = client.init()


def get_data_parser():
    if os.path.isfile(client_config.solc_path) or os.path.isfile(client_config.solcjs_path):
        Compiler.compile_file("contracts/HelloWorld.sol")
        Compiler.compile_file("contracts/SimpleInfo.sol")

    abi_file = "contracts/SimpleInfo.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    return data_parser, abi_file


def get_to_address():
    # 从文件加载abi定义
    if os.path.isfile(client_config.solc_path) or os.path.isfile(client_config.solcjs_path):
        Compiler.compile_file("contracts/HelloWorld.sol")
        Compiler.compile_file("contracts/SimpleInfo.sol")

    data_parser, abi_file = get_data_parser()
    contract_abi = data_parser.contract_abi

    # 部署合约
    print("\n>>Deploy:---------------------------------------------------------------------")
    with open("contracts/SimpleInfo.bin", 'r') as load_f:
        contract_bin = load_f.read()
        load_f.close()
    result = client.deploy(contract_bin)
    print("deploy", result)
    print("new address : ", result["contractAddress"])
    contract_name = os.path.splitext(os.path.basename(abi_file))[0]

    to_address = result['contractAddress'] #use new deploy address
    # to_address = "0xcda895ec53a73fbc3777648cb4c87b38e252f876" #use new deploy address
    return to_address, contract_abi, result

def check_contract():
    """
    通过 json文件 ，检查合约是否已经部署过，如果没有，则部署一次并生成json文件
    :return:
    """
    file_path = '/root/fisco/nodes/contracts.json'
    if os.path.isfile(file_path):
        with open(file_path, 'r') as load_f:
            load_data = json.load(load_f)
            to_address, contract_abi, result = load_data['to_address'], load_data['contract_abi'], load_data['result']
        try:
            get_transaction_detail_data(result['transactionHash'])
        except Exception:
            print("\n>>check fail")
            os.remove(file_path)
            check_contract()
    else:
        to_address, contract_abi, result = get_to_address()
        with open(file_path, 'w') as save_f:
            json.dump({
                'to_address': to_address,
                'contract_abi': contract_abi,
                'result': result,
            }, save_f)
    return to_address, contract_abi

def get_one_block(res):
    number = int(res.get("number"), 16)
    add_time = time.strftime("%Y-%m-%d %H:%M:%S",
                             time.localtime(int(str(int(res.get("timestamp"), 16))[0:10]))),
    transaction_num = len(res.get("transactions"))
    block_hash = res.get("hash")
    parentHash = res.get("parentHash")
    result = {
        "number": number,
        "add_time": add_time[0],
        "transaction_num": transaction_num,
        "block_hash": block_hash,
        "parentHash": parentHash
    }
    return result


def by_blockNumber_get_transaction_list(res):
    transactions = res.get("transactions")
    for i in transactions:
        i["blockNumber"] = int(i.get("blockNumber"), 16)
        i["transactionIndex"] = int(i.get("transactionIndex"), 16)
        i["time"] = time.strftime("%Y-%m-%d %H:%M:%S",
                                  time.localtime(int(str(int(res.get("timestamp"), 16))[0:10])))

    transaction_list = transactions
    return transaction_list


def get_one_transaction(res):
    blockNumber = int(res.get("blockNumber", ""), 16)
    block_res = client.getBlockByNumber(blockNumber)
    transactionTime = time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(int(str(int(block_res.get("timestamp"), 16))[0:10])))
    result = {
        "hash": res.get("hash", ""),
        "from": res.get("from", ""),
        "to": res.get("to", ""),
        "blockNumber": int(res.get("blockNumber", ""), 16),
        "transactionIndex": int(res.get("transactionIndex", ""), 16),
        "time": transactionTime
    }
    return result


def get_index_data():
    res = client.getTotalTransactionCount()
    high_block_num = blockNumber = int(res.get("blockNumber", "0x0"), 16)
    txSum = int(res.get("txSum", "0x0"), 16)
    failedTxSum = int(res.get("failedTxSum", "0x0"), 16)
    pbftView = int(client.getPbftView(), 16)
    # print("首页数据:", blockNumber, txSum, failedTxSum, pbftView)
    consensusStatus = client.getConsensusStatus()
    highestblockNumber = consensusStatus[0].get("highestblockNumber")
    nodeList = consensusStatus[1]
    for i in nodeList:
        i["highestblockNumber"] = highestblockNumber
        i["static"] = "正常"
    block_list = []
    all_transaction_list = []
    transaction_list = []

    for x in range(high_block_num):
        # if get_block_Number >= 0:
        res = client.getBlockByNumber(high_block_num)
        transactions = res.get("transactions")
        for i in transactions:
            i["blockNumber"] = int(i.get("blockNumber"), 16)
            i["transactionIndex"] = int(i.get("transactionIndex"), 16)
            i["time"] = time.strftime("%Y-%m-%d %H:%M:%S",
                                      time.localtime(int(str(int(res.get("timestamp"), 16))[0:10])))
        all_transaction_list += transactions
        high_block_num -= 1
    # print(all_transaction_list)

    now_time = time.time()
    data_list = []
    for i in range(15):
        data_list.append(time.strftime('%m-%d', time.localtime(now_time)))
        now_time -= 86400
    data_list = data_list[::-1]
    count_list = [0 for _ in range(15)]

    for one_transaction in all_transaction_list:
        try:
            index = data_list.index(one_transaction.get("time").split(" ")[0][5:])
            count_list[index] += 1
        except:
            pass
    for j in range(4):
        get_blockNumber = blockNumber - j
        if get_blockNumber > 0:
            block_msg = client.getBlockByNumber(get_blockNumber)
            # print("【{}】".format(block_msg))
            one_block_msg = {
                "block_num": get_blockNumber,
                "block_hash": block_msg.get("hash"),
                "time": time.strftime("%Y-%m-%d %H:%M:%S",
                                      time.localtime(int(str(int(block_msg.get("timestamp"), 16))[0:10]))),
                "transaction_num": len(block_msg.get("transactions"))
            }
            one_transaction_msg = {
                "transaction_hash": block_msg.get("transactions")[0].get("hash", ""),
                "from": block_msg.get("transactions")[0].get("from", ""),
                "to": block_msg.get("transactions")[0].get("to", ""),
                "time": time.strftime("%Y-%m-%d %H:%M:%S",
                                      time.localtime(int(str(int(block_msg.get("timestamp"), 16))[0:10]))),
            }
            block_list.append(one_block_msg)
            transaction_list.append(one_transaction_msg)

    result = {
        "blockNumber": blockNumber,
        "txSum": txSum,
        "failedTxSum": failedTxSum,
        "pbftView": pbftView,
        "nodeList": nodeList,
        "block_list": block_list,
        "transaction_list": transaction_list,
        "data_list": data_list,
        "count_list": count_list
    }
    return result


def get_block_list_data(blockNumber, blockHash, page):
    block_list = []
    # blockNumber = request.args.get('blockNumber', '')
    # blockHash = request.args.get('blockHash', '')
    if blockNumber != '':
        res = client.getBlockByNumber(blockNumber)
        one_block = get_one_block(res)
        block_list.append(one_block)
        result = {
            "block_num": 1,
            "block_list": block_list
        }
    elif blockHash != '':
        res = client.getBlockByHash(blockHash)
        one_block = get_one_block(res)
        block_list.append(one_block)
        result = {
            "block_num": 1,
            "block_list": block_list
        }
    else:
        res = client.getTotalTransactionCount()
        blockNumber = int(res.get("blockNumber", "0x0"), 16)
        # page = request.args.get('page', '')
        get_block_Number = blockNumber - 10 * (int(page) - 1)
        for i in range(10):
            if get_block_Number >= 0:
                res = client.getBlockByNumber(get_block_Number)
                one_block = get_one_block(res)
                block_list.append(one_block)
            get_block_Number -= 1
        result = {
            "block_num": blockNumber + 1,
            "block_list": block_list
        }
    return result


def get_transaction_list_data(blockNumber, transactionHash, page):
    transaction_list = []
    # blockNumber = request.args.get('blockNumber', '')
    # transactionHash = request.args.get('transactionHash', '')
    if blockNumber != '':
        res = client.getBlockByNumber(blockNumber)
        transaction_list = by_blockNumber_get_transaction_list(res)
        result = {
            "transaction_num": 1,
            "transaction_list": transaction_list
        }
    elif transactionHash != '':
        res = client.getTransactionByHash(transactionHash)
        one_transaction = get_one_transaction(res)
        transaction_list.append(one_transaction)
        result = {
            "transaction_num": 1,
            "transaction_list": transaction_list
        }
    else:
        res = client.getTotalTransactionCount()
        high_block_num = blockNumber = int(res.get("blockNumber", "0x0"), 16)
        transactionNumber = int(res.get("txSum", "0x0"), 16)
        # page = int(request.args.get('page', ''))
        page = int(page)
        # get_block_Number = blockNumber - 10 * (int(page) - 1)
        for x in range(blockNumber):
            # if get_block_Number >= 0:
            res = client.getBlockByNumber(blockNumber)
            transactions = res.get("transactions")
            for i in transactions:
                i["blockNumber"] = int(i.get("blockNumber"), 16)
                i["transactionIndex"] = int(i.get("transactionIndex"), 16)
                i["time"] = time.strftime("%Y-%m-%d %H:%M:%S",
                                          time.localtime(int(str(int(res.get("timestamp"), 16))[0:10])))
            transaction_list += transactions
            blockNumber -= 1
        result = {
            "high_block_num": high_block_num,
            "transaction_num": transactionNumber,
            "transaction_list": transaction_list[10 * (page - 1):10 * page]
        }
    return result

def get_block_hash(blockNumber, blockHash):
    block_hash = number = add_time = transaction_number ='--'
    try:
        block_list = get_block_list_data(blockNumber, blockHash, '')['block_list']
    except:
        pass
    else:
        block_hash = block_list[0]['block_hash']
        number = block_list[0]['number']
        add_time = block_list[0]['add_time']
        transaction_number = block_list[0]['transaction_num']
    return block_hash, number, add_time, transaction_number

def get_summary_data(transactionHash):
    """
返回值为：
区块信息
    当前区块（Current block）
    当前区块交易数量（Current block transactions）
    区块哈希值（Block hash）
    前一个区块哈希（Previous block hash）
    后一个区块哈希（Latter block hash）
    区块创建时间（Block creation time）
交易信息
    交易哈希值（Transaction hash）
    发送者（from）：加密
    接收者（to）：加密
    输入信息（Input）：加密
    交易创建时间（Transaction create time）

"""
    transaction_detail = get_transaction_detail_data(transactionHash)
    receipt = transaction_detail['transactionReceipt']
    block_hash = receipt['blockHash']
    block_detail = get_block_detail_data(block_hash)
    _, block_number, add_time, transaction_number = get_block_hash('', block_hash)

    data = {
        'block' : {
            'blockNumber': block_number,
            'transactionNumber': transaction_number,
            'blockHash': block_hash,
            'parentHash': block_detail['parentHash'],
            'childHash': get_block_hash(block_number+1, '')[0],
            'time': add_time,

        },
        'transaction' : {
            'transactionHash': transactionHash,
            'from': receipt['from'],
            'to': receipt['to'],
            'input': receipt['input'],
            'time': get_transaction_list_data('',transactionHash, '')['transaction_list'][0]['time'],
        }
    }
    return data

def get_transaction_detail_data(transactionHash):
    # transactionHash = request.args.get('transactionHash', '')
    txresponse = client.getTransactionByHash(transactionHash)
    data_parser, abi_file = get_data_parser()
    input = data_parser.parse_transaction_input(txresponse['input'])

    transactionReceipt = client.getTransactionReceipt(transactionHash)
    receiptInput = data_parser.parse_transaction_input(transactionReceipt['input'])

    if input is None:
        chain_data = ''
    else:
        chain_data = input.get('args')[0]
    if receiptInput is None:
        receipt_data = ''
    else:
        receipt_data = receiptInput.get('args')[0]
    result = {
        "txresponse": txresponse,
        "transactionReceipt": transactionReceipt,
        "chain_data": chain_data,
        "receipt_data": receipt_data
    }
    return result


def get_block_detail_data(blockHash):
    txresponse = client.getBlockByHash(blockHash)
    return txresponse


def send_transaction_get_txhash(requestData):
    # requestData = json.loads(request.get_data().decode())
    hash = hashlib.sha1()
    hash.update(json.dumps(requestData, ensure_ascii=False).encode('utf-8'))
    requestData['hashCode'] = hash.hexdigest()
    requestData['time'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    transData = json.dumps(requestData, ensure_ascii=False)

    args = [transData, 1024, to_checksum_address('0x7029c502b4F824d19Bd7921E9cb74Ef92392FB1c')]
    receipt = client.sendRawTransactionGetReceipt(to_address, contract_abi, "set", args)
    txhash = receipt['transactionHash']
    # print("receipt:",receipt)
    return txhash

to_address, contract_abi = check_contract()
