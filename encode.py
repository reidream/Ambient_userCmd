import os
from dotenv import load_dotenv
from web3 import Web3
from eth_abi import encode

load_dotenv("web3.env")
chain = "scroll"
rpc = f"https://{chain}-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_PRC')}" # 自分のRPC
w3 = Web3(Web3.HTTPProvider(rpc))
if w3.is_connected():
    print("w3 connect is True")

# Contract addresses
CROCSWAP_DEX = w3.to_checksum_address('0xaaaaAAAACB71BF2C8CaE522EA5fa455571A74106')
USDC = w3.to_checksum_address('0x06efdbff2a14a7c8e15944d1f4a48f9f95f663a4')
USDT = w3.to_checksum_address('0xf55bec9cafdbe8730f096aa55dad6d22d44099df')

# Swap parameters
SWAP_PROXY = 1 # swap 関数呼び出し
POOL_IDX = 420 #pool id
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

cmd = create_exact_cmd()
cmd_hex = bytes_to_hex(cmd)
print("Generated cmd (hex):")
print(cmd_hex)

