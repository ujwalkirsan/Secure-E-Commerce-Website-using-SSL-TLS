import json
import hashlib

def calculate_hash(block):
    block_content = {
        'index': block['index'],
        'timestamp': block['timestamp'],
        'data': block['data'],
        'previous_hash': block['previous_hash'],
        'nonce': block['nonce']
    }
    block_string = json.dumps(block_content, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def is_block_mined(block, difficulty):
    return block['hash'].startswith('0' * difficulty)

def validate_blockchain(filename, difficulty=4):
    with open(filename, 'r') as f:
        chain = json.load(f)

    for i, block in enumerate(chain):
        calculated_hash = calculate_hash(block)
        
        # Hash validation
        if block['hash'] != calculated_hash:
            print(f"❌ Block {block['index']} has invalid hash.")
            return

        # Previous hash validation (except genesis block)
        if i > 0 and block['previous_hash'] != chain[i - 1]['hash']:
            print(f"❌ Block {block['index']} has invalid previous hash.")
            return

    print("✅ Blockchain is valid.")

    # Check mining status of latest block
    latest_block = chain[-1]
    if is_block_mined(latest_block, difficulty):
        print(f"✅ Latest block (Index {latest_block['index']}) is mined. Hash: {latest_block['hash']}")
    else:
        print(f"⚠️ Latest block (Index {latest_block['index']}) is NOT mined properly. Hash: {latest_block['hash']}")

# Run the validator
validate_blockchain('blockchain_transactions.json', difficulty=5)  # You can adjust difficulty
