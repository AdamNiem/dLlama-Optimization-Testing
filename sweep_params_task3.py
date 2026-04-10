import subprocess
import time
import itertools
import csv
import re

# --- CREDENTIALS & WORKER CONFIG ---
SSH_USER = "your_ssh_username"
WORKER_NODES = {
    "worker6": "sudo_password_for_6", 
    "worker7": "sudo_password_for_7",
    "worker8": "sudo_password_for_8"
}

# --- TASK 2 MODEL PATHS ---
PROMPT_FILE = "../dLlamaPrompts/SS.txt"
MODEL = "models/llama3_1_8b_instruct_q40/dllama_model_llama3_1_8b_instruct_q40.m"
TOKENIZER = "models/llama3_1_8b_instruct_q40/dllama_tokenizer_llama3_1_8b_instruct_q40.t"
WORKERS = "192.168.1.107:9999 192.168.1.108:9999 192.168.1.109:9999"
STEPS = 512

# --- OPTIMIZATION SWEEP PARAMETERS ---
# In Task 2, try more aggressive thread counts and different buffer types
NTHREADS = [2, 4, 6, 8]
MAX_SEQ_LENS = [4096] 
BUFFER_FLOAT_TYPES = ["q80", "q40", "f16"] # Check which types your optimized code supports

CSV_FILENAME = "llama3_optimization_results.csv"

def restart_workers():
    print("  -> Restarting remote workers...")
    for host, pwd in WORKER_NODES.items():
        # Optimization: We ensure the worker also uses high priority (-20)
        remote_cmd = (
            f"echo '{pwd}' | sudo -S sh -c '"
            f"pkill -9 -f \"dllama worker\" ; "
            f"cd /shared/DLlamaTest/distributed-llama/ && "
            f"nohup nice -n -20 ./dllama worker --port 9999 --nthreads 2 > /dev/null 2>&1 &'"
        )
        ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", f"{SSH_USER}@{host}", remote_cmd]
        try:
            subprocess.run(ssh_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except:
            print(f"     [!] Failed to reach {host}")
    time.sleep(5)

def extract_throughput(output):
    """
    Parses dllama output for throughput. 
    Adjust the regex if your modified source code changes the output format.
    """
    # Look for patterns like "12.50 tokens/s" or "tokens per second: 12.50"
    match = re.search(r"(\d+\.\d+)\s+tokens/s", output)
    if match:
        return float(match.group(1))
    return 0.0

def main():
    with open(PROMPT_FILE, 'r') as f:
        prompt_text = f.read()

    combinations = list(itertools.product(NTHREADS, MAX_SEQ_LENS, BUFFER_FLOAT_TYPES))
    
    with open(CSV_FILENAME, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["nthreads", "max_seq_len", "buffer_type", "tokens_per_sec", "status"])
        
        for nthreads, max_seq_len, buffer_type in combinations:
            print(f"Testing: threads={nthreads}, buffer={buffer_type}...")
            
            # Using 'nice' on the head node as well for maximum priority
            command = [
                "nice", "-n", "-20",
                "./dllama", "inference",
                "--prompt", prompt_text,
                "--steps", str(STEPS),
                "--model", MODEL,
                "--tokenizer", TOKENIZER,
                "--buffer-float-type", buffer_type,
                "--nthreads", str(nthreads),
                "--max-seq-len", str(max_seq_len),
                "--workers"
            ] + WORKERS.split()
            
            try:
                # Capture stderr as well because some engines print stats there
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                throughput = extract_throughput(result.stdout + result.stderr)
                status = "Success"
                print(f"  -> Throughput: {throughput} t/s")
                
            except subprocess.CalledProcessError:
                throughput = 0.0
                status = "Failed"
                restart_workers()
                
            writer.writerow([nthreads, max_seq_len, buffer_type, throughput, status])
            csv_file.flush()

if __name__ == "__main__":
    main()
