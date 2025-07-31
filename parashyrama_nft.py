import json
import os
import time
from dotenv import load_dotenv
from web3 import Web3
from solcx import compile_standard, install_solc

# 📦 Load environment variables
load_dotenv()
private_key = os.getenv("PRIVATE_KEY")
wallet_address = os.getenv("WALLET_ADDRESS")
rpc_url = os.getenv("RPC_URL")

# 🔌 Connect to blockchain
web3 = Web3(Web3.HTTPProvider(rpc_url))
assert web3.is_connected(), "❌ RPC connection failed!"

# ⚒️ Install and set compiler
install_solc("0.8.17")
with open("ParashyramaNFT.sol", "r") as file:
    contract_source_code = file.read()

compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {
        "ParashyramaNFT.sol": {
            "content": contract_source_code
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "metadata", "evm.bytecode"]
            }
        }
    }
}, solc_version="0.8.17")

# 📦 Extract ABI and Bytecode
contract_interface = compiled_sol["contracts"]["ParashyramaNFT.sol"]["ParashyramaNFT"]
abi = contract_interface["abi"]
bytecode = contract_interface["evm"]["bytecode"]["object"]

# 💾 Save ABI
with open("ParashyramaNFT_abi.json", "w") as f:
    json.dump(abi, f)

# 🚀 Deploy contract
contract = web3.eth.contract(abi=abi, bytecode=bytecode)
nonce = web3.eth.get_transaction_count(wallet_address)

transaction = contract.constructor().build_transaction({
    'from': wallet_address,
    'nonce': nonce,
    'gas': 8000000,
    'gasPrice': web3.to_wei('100', 'gwei')
})

signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
print(f"📤 Deployment TX: {web3.to_hex(tx_hash)}")

# ⏳ Wait for deployment
receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = receipt.contractAddress
print(f"✅ Contract Deployed at: {contract_address}")

# 🔧 Rebuild contract instance
contract = web3.eth.contract(address=contract_address, abi=abi)

# 📝 Poem and Title for NFT
nft_title = "Echoes of the Horizon"
nft_description = """Beneath the endless sky of dreams,
A river winds, a song that gleams.
Where shadows dance with the rising sun,
A journey calls, a race begun."""

nft_description = nft_description.replace("\n", " ")

# 🎨 Mint NFT with title and description
nonce += 1
mint_txn = contract.functions.mintTextNFT(nft_title, nft_description).build_transaction({
    'from': wallet_address,
    'nonce': nonce,
    'gas': 500000,
    'gasPrice': web3.to_wei('100', 'gwei')
})

signed_mint = web3.eth.account.sign_transaction(mint_txn, private_key)
mint_tx_hash = web3.eth.send_raw_transaction(signed_mint.raw_transaction)
print(f"📤 Mint TX: {web3.to_hex(mint_tx_hash)}")

# ⌛ Confirm mint
mint_receipt = web3.eth.wait_for_transaction_receipt(mint_tx_hash)
print(f"✅ Mint Confirmed: {mint_receipt}")

# ⏱️ Add delay to give OpenSea time to update metadata
time.sleep(30)

# 🔍 Verify token and save links
try:
    token_id = contract.functions.tokenCounter().call()
    owner = contract.functions.ownerOf(token_id).call()
    token_uri = contract.functions.tokenURI(token_id).call()

    print(f"🎯 Token ID: {token_id}")
    print(f"👤 Owner: {owner}")
    print(f"🖼 Token URI: {token_uri}")

    if token_uri.startswith("data:application/json;utf8,"):
        raw_json = token_uri[len("data:application/json;utf8,"):]
        try:
            metadata = json.loads(raw_json)
            print("\n📦 Parsed Metadata:")
            print(f"🖋 Title: {metadata.get('name')}")
            print(f"📜 Description: {metadata.get('description')}")
            print(f"🖼 Image (SVG embedded): {metadata.get('image')}")
            print(f"🔖 Attributes: {metadata.get('attributes')}")
        except Exception as e:
            print(f"❌ Failed to parse tokenURI JSON: {e}")

    opensea_url = f"https://opensea.io/assets/matic/{contract_address}"
    polygonscan_url = f"https://polygonscan.com/address/{contract_address}"

    print(f"OpenSea: {opensea_url}")
    print(f"PolygonScan: {polygonscan_url}")

    filename = "ParashyramaNFT_Links.txt"
    if os.path.exists(filename):
        filename = f"ParashyramaNFT_Links_{int(time.time())}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"🌊 OpenSea: {opensea_url}\n")
        f.write(f"🔍 PolygonScan: {polygonscan_url}\n")

    print(f"📁 Links saved to {filename}")

except Exception as e:
    print(f"⚠️ Verification failed: {e}")
