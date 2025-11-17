#!/usr/bin/env python3
"""
Wallet Data Repair Script
Fixes incomplete wallet entries that are missing nonce or salt data
"""

import os
import shelve


def repair_wallet_data():
    """Repair incomplete wallet entries"""
    print("🔧 CalorieAppTestnet Wallet Data Repair Tool")
    print("=" * 50)

    try:
        # Check if wallet_data exists
        if not os.path.exists("wallet_data.dat"):
            print("❌ No wallet_data.dat found. No repair needed.")
            return

        with shelve.open("wallet_data") as wallet_data:
            print(f"📁 Found wallet data with {len(wallet_data)} entries")

            # Find all public keys
            public_keys = [key for key in wallet_data.keys() if key.startswith("public_key")]
            print(f"🔑 Found {len(public_keys)} wallet entries: {public_keys}")

            incomplete_wallets = []

            for pub_key in public_keys:
                account_num = pub_key.replace("public_key", "")
                private_key = f"private_key{account_num}"
                nonce_key = f"nonce{account_num}"
                salt_key = f"salt{account_num}"

                missing = []
                if private_key not in wallet_data:
                    missing.append(private_key)
                if nonce_key not in wallet_data:
                    missing.append(nonce_key)
                if salt_key not in wallet_data:
                    missing.append(salt_key)

                if missing:
                    print(f"❌ Wallet {account_num} is incomplete - missing: {missing}")
                    incomplete_wallets.append(account_num)
                else:
                    print(f"✅ Wallet {account_num} is complete")

            # Remove incomplete wallets
            if incomplete_wallets:
                print(f"\n🗑️  Removing {len(incomplete_wallets)} incomplete wallet(s)...")
                for account_num in incomplete_wallets:
                    keys_to_remove = [
                        f"public_key{account_num}",
                        f"private_key{account_num}",
                        f"nonce{account_num}",
                        f"salt{account_num}",
                        f"keys{account_num}",
                    ]

                    for key in keys_to_remove:
                        if key in wallet_data:
                            del wallet_data[key]
                            print(f"  🗑️  Removed {key}")

                print(f"✅ Cleanup complete! Removed incomplete wallets: {incomplete_wallets}")
            else:
                print("✅ All wallets are complete - no repair needed!")

    except Exception as e:
        print(f"❌ Error during repair: {e}")


if __name__ == "__main__":
    repair_wallet_data()
    print("\n🎉 Wallet repair completed! You can now run the app.")
