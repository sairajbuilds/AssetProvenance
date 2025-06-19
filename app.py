from flask import Flask, render_template, request, redirect, url_for, jsonify
from web3 import Web3
import json

from web3.exceptions import ContractLogicError

from asset_provenance import contract_address

app = Flask(__name__)

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
chain_id = 1337
private_key = "0xf80f230d8a8178a847219d2c5127970af499e4ddff68fc5ef696a9dac25caa5e"
account = w3.eth.account.from_key(private_key)
my_address = account.address

with open('abi.json') as f:
    abi = json.load(f)
contract = w3.eth.contract(address= contract_address, abi=abi)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        serial = request.form['serial']
        model = request.form['model']
        warranty_years = int(request.form['warranty'])
        warranty_seconds = warranty_years * 365 * 24 * 60 * 60

        nonce = w3.eth.get_transaction_count(my_address)
        txn = contract.functions.registerDevice(serial, model, warranty_seconds).build_transaction({
            "chainId": chain_id,
            "from": my_address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": w3.to_wei("20", "gwei"),
        })
        signed_txn = w3.eth.account.sign_transaction(txn, private_key)
        try:
            tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            w3.eth.wait_for_transaction_receipt(tx_hash)
            return redirect(url_for('index'))
        except ContractLogicError as e:
            error = str(e)
        except Exception as e:
            error = f"Unexpected error: {e}"
    return render_template('register.html', error=error)

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        serial = request.form['serial']
        new_owner = request.form['new_owner']

        nonce = w3.eth.get_transaction_count(my_address)
        txn = contract.functions.transferOwnership(serial, new_owner).build_transaction({
            "chainId": chain_id,
            "from": my_address,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("20", "gwei"),
        })
        signed_txn = w3.eth.account.sign_transaction(txn, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return redirect(url_for('index'))
    return render_template('transfer_ownership.html')

@app.route('/service', methods=['GET', 'POST'])
def service():
    if request.method == 'POST':
        serial = request.form['serial']
        description = request.form['description']

        nonce = w3.eth.get_transaction_count(my_address)
        txn = contract.functions.addServiceEvent(serial, description).build_transaction({
            "chainId": chain_id,
            "from": my_address,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("20", "gwei"),
        })
        signed_txn = w3.eth.account.sign_transaction(txn, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return redirect(url_for('index'))
    return render_template('add_service_event.html')

@app.route('/device', methods=['GET', 'POST'])
def device():
    device  = None
    if request.method == 'POST':
        serial = request.form['serial']
        result = contract.functions.getDevice(serial).call()
        device = {
            "model": result[0],
            "owner": result[1],
            "expiry": result[2],
            "service_count": result[3],
        }
    return render_template('view_device.html', device=device)

@app.route('/service-history', methods=['GET', 'POST'])
def service_history():
    events = []
    if request.method == 'POST':
        serial = request.form['serial']
        device = contract.functions.getDevice(serial).call()
        service_count = device[3]
        for i in range(service_count):
            event = contract.functions.getServiceEvent(serial, i).call()
            events.append({
                "date": event[0],
                "description": event[1],
                "center": event[2],
            })
    return render_template('service_history.html', events=events)

if __name__ == '__main__':
    app.run(debug=True)