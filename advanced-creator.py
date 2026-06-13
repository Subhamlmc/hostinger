import subprocess
import re

PROGRAM_ID = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"

def run(cmd):
    print(f"\n>>> {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def extract_mint(output):
    match = re.search(r"Creating token\s+([A-Za-z0-9]+)", output)
    if not match:
        raise Exception("Mint not found in output")
    return match.group(1)

print("\n===== FLEXIBLE SOLANA TOKEN CREATOR =====\n")

# INPUTS
name = input("Token Name: ")
symbol = input("Token Symbol: ")

github = input("GitHub metadata.json link: ")
uri = github.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

decimals = input("Decimals (default 9): ") or "9"
supply = input("Total Supply: ")

revoke_mint = input("Revoke mint authority? (y/n): ").lower() == "y"
revoke_freeze = input("Revoke freeze authority? (y/n): ").lower() == "y"

# EXTENSIONS
enable_transfer_fee = input("Enable transfer fee? (y/n): ").lower() == "y"
if enable_transfer_fee:
    print("→ Transfer Fee: Every transfer automatically withholds a % fee into accounts, later withdrawable.")

enable_interest = input("Enable interest-bearing? (y/n): ").lower() == "y"
if enable_interest:
    print("→ Interest Bearing: Token balances accrue interest over time.")

enable_delegate = input("Enable permanent delegate? (y/n): ").lower() == "y"
if enable_delegate:
    print("→ Permanent Delegate: A delegate authority can always transfer tokens.")

enable_nontransferable = input("Enable non-transferable? (y/n): ").lower() == "y"
if enable_nontransferable:
    print("→ Non-Transferable: Tokens cannot be transferred once minted.")

# 1. CREATE TOKEN
print("\n[1] Creating Token-2022 mint...\n")

cmd = f"spl-token create-token --program-id {PROGRAM_ID} --enable-metadata --decimals {decimals}"

if enable_transfer_fee:
    cmd += " --enable-transfer-fee"
if enable_interest:
    cmd += " --enable-interest-bearing"
if enable_delegate:
    cmd += " --enable-permanent-delegate"
if enable_nontransferable:
    cmd += " --enable-non-transferable"

output = subprocess.check_output(cmd, shell=True).decode()
print(output)

mint = extract_mint(output)
print(f"\nMint Address: {mint}")

# 2. METADATA
print("\n[2] Initializing metadata...\n")
run(f'spl-token initialize-metadata {mint} "{name}" "{symbol}" "{uri}"')

# 3. TOKEN ACCOUNT
print("\n[3] Creating token account...\n")
run(f"spl-token create-account {mint}")

# 4. MINT SUPPLY
print("\n[4] Minting supply...\n")
run(f"spl-token mint {mint} {supply}")

# 5. OPTIONAL SECURITY STEPS
if revoke_mint:
    print("\n[5] Revoking mint authority...\n")
    run(f"spl-token authorize {mint} mint --disable")

if revoke_freeze:
    print("\n[6] Revoking freeze authority...\n")
    run(f"spl-token authorize {mint} freeze --disable")

print("\n===== TOKEN CREATED SUCCESSFULLY =====")
print("Mint:", mint)
print("Metadata:", uri)
print("Extensions Enabled:")
if enable_transfer_fee: print(" - Transfer Fee")
if enable_interest: print(" - Interest Bearing")
if enable_delegate: print(" - Permanent Delegate")
if enable_nontransferable: print(" - Non-Transferable")
if not (enable_transfer_fee or enable_interest or enable_delegate or enable_nontransferable):
    print(" - None (Clean Token)")
