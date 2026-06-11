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

print("\n===== CLEAN SOLANA TOKEN CREATOR (NO TAX) =====\n")

# INPUTS
name = input("Token Name: ")
symbol = input("Token Symbol: ")

github = input("GitHub metadata.json link: ")
uri = github.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

decimals = input("Decimals (default 9): ") or "9"
supply = input("Total Supply: ")

revoke_mint = input("Revoke mint authority? (y/n): ").lower() == "y"
revoke_freeze = input("Revoke freeze authority? (y/n): ").lower() == "y"

# 1. CREATE TOKEN
print("\n[1] Creating Token-2022 mint...\n")

output = subprocess.check_output(
    f"spl-token create-token --program-id {PROGRAM_ID} --enable-metadata --decimals {decimals}",
    shell=True
).decode()

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
print("Status: NO TAX / NO TRANSFER FEES")
