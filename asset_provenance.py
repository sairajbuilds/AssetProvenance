import json

from solcx import compile_standard, install_solc
from web3 import Web3

install_solc('0.8.5')
with open("AssetProvenance.sol", "r") as file:
    contract_code = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"AssetProvenance.sol": {"content": contract_code}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.sourceMap"
                    ]
                },
            }
        }
    },
    solc_version="0.8.5"
)

abi = compiled_sol['contracts']['AssetProvenance.sol']['AssetProvenance']['abi']
bytecode = compiled_sol['contracts']['AssetProvenance.sol']['AssetProvenance']['evm']['bytecode']['object']

with open("abi.json", "w") as file:
    json.dump(abi, file, indent=2)

print("ABI saved to abi.json")

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
chain_id = 1337
private_key = "0xf80f230d8a8178a847219d2c5127970af499e4ddff68fc5ef696a9dac25caa5e"
account = w3.eth.account.from_key(private_key)
my_address = account.address

AssetProvenance = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.get_transaction_count(my_address)
transaction = AssetProvenance.constructor().build_transaction({
    "chainId": chain_id,
    "from": my_address,
    "nonce": nonce,
    "gas": 3000000,
    "gasPrice": w3.to_wei("20", "gwei"),
})
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt['contractAddress']
print(f"Contract Address: {contract_address}")