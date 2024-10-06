import os
from dotenv import load_dotenv
from web3 import Web3
from eth_abi import encode
import time

# .env ファイルから環境変数を読み込む
load_dotenv("web3.env")
chain = "scroll"
rpc = f"https://{chain}-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_PRC')}"  # 自分のRPC
w3 = Web3(Web3.HTTPProvider(rpc))

# ウォレット情報（.envファイルから読み込む）
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS") # your private key
PRIVATE_KEY = os.getenv("PRIVATE_KEY") # your address

# Contract addresses
CROCSWAP_DEX = w3.to_checksum_address('0xaaaaAAAACB71BF2C8CaE522EA5fa455571A74106')
USDC = w3.to_checksum_address('0x06efdbff2a14a7c8e15944d1f4a48f9f95f663a4')
USDT = w3.to_checksum_address('0xf55bec9cafdbe8730f096aa55dad6d22d44099df')

# Swap parameters
SWAP_PROXY = 1  # swap 関数呼び出し
POOL_IDX = 420  # pool id
IS_BUY = False  # Selling USDT, buying USDC
IN_BASE_QTY = False  # Input quantity is in USDT
QTY = 100000  # 0.1 USDT (6 decimal places)
TIP = 0
LIMIT_PRICE = 65000  # 本当は正しい数字　今回過去のinput欄参考
MIN_OUT = 98500  # Minimum 0.098857 USDC to receive (6 decimal places) 
SETTLE_FLAGS = 0

def create_exact_cmd():
    swap_params = encode(
        ['address', 'address', 'uint256', 'bool', 'bool', 'uint256', 'uint256', 'uint256', 'uint256', 'uint8'],
        [USDC, USDT, POOL_IDX, IS_BUY, IN_BASE_QTY, QTY, TIP, LIMIT_PRICE, MIN_OUT, SETTLE_FLAGS]
    )
    return swap_params

def bytes_to_hex(byte_string):
    return '0x' + byte_string.hex()

def execute_swap():
    if not w3.is_connected():
        print("Error: Unable to connect to the Ethereum network")
        return

    # コントラクトABI（必要な部分のみ）
    abi = [{
        "inputs": [
            {"internalType": "uint16", "name": "callpath", "type": "uint16"},
            {"internalType": "bytes", "name": "cmd", "type": "bytes"}
        ],
        "name": "userCmd",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }]

    # コントラクトインスタンスの作成
    contract = w3.eth.contract(address=CROCSWAP_DEX, abi=abi)

    # トランザクションパラメータの準備
    cmd = create_exact_cmd()
    callpath = SWAP_PROXY

    # トランザクションの構築　
    transaction = contract.functions.userCmd(callpath, cmd).build_transaction({
        'from': WALLET_ADDRESS,
        'gas': 2000000,  # ガスリミットは適切に調整してください
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(WALLET_ADDRESS),
    })

    # トランザクションの署名
    signed_txn = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)

    # トランザクションの送信
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Transaction sent: {tx_hash.hex()}")

    # トランザクションの確認待ち
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if tx_receipt['status'] == 1:
        print("Swap executed successfully!")
    else:
        print("Swap failed. Check the transaction for more details.")

    return tx_receipt

if __name__ == "__main__":
    print("Starting swap execution...")
    try:
        receipt = execute_swap()
        print(f"Transaction receipt: {receipt}")
    except Exception as e:
        print(f"An error occurred: {e}")


# error の場合usdt aprove してください
# 実戦ではgas設定は最適化する必要がある。    

        