#!/usr/bin/env python3
"""
Complete Wallet Database Cleanup Script
Removes all existing test wallet addresses to eliminate corruption
"""
import shelve


def clean_wallet_database():
    """
    Completely clean the wallet database of all test wallets
    """
    print("🧹 Starting complete wallet database cleanup...")

    try:
        with shelve.open("wallet_data") as wallet_data:
            # Get all keys
            all_keys = list(wallet_data.keys())
            print(f"📊 Found {len(all_keys)} total keys in database")

            # Identify wallet-related keys
            wallet_keys = []
            for key in all_keys:
                if any(
                    key.startswith(prefix)
                    for prefix in ["public_key", "private_key", "nonce_key", "salt_key"]
                ):
                    wallet_keys.append(key)

            print(f"🔑 Found {len(wallet_keys)} wallet-related keys:")
            for key in sorted(wallet_keys):
                print(f"   - {key}")

            # Remove all wallet keys
            removed_count = 0
            for key in wallet_keys:
                if key in wallet_data:
                    del wallet_data[key]
                    removed_count += 1
                    print(f"🗑️  Removed: {key}")

            # Keep non-wallet data (like password)
            remaining_keys = [key for key in all_keys if key not in wallet_keys]
            print(f"✅ Kept {len(remaining_keys)} non-wallet keys: {remaining_keys}")

            print("\n✅ Cleanup completed!")
            print(f"   - Removed: {removed_count} wallet-related keys")
            print(f"   - Preserved: {len(remaining_keys)} system keys")

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

    return True


def verify_cleanup():
    """
    Verify that the cleanup was successful
    """
    print("\n🔍 Verifying cleanup...")

    try:
        with shelve.open("wallet_data") as wallet_data:
            all_keys = list(wallet_data.keys())
            wallet_keys = [
                key
                for key in all_keys
                if any(
                    key.startswith(prefix)
                    for prefix in ["public_key", "private_key", "nonce_key", "salt_key"]
                )
            ]

            if wallet_keys:
                print(f"⚠️  Warning: Still found {len(wallet_keys)} wallet keys:")
                for key in wallet_keys:
                    print(f"   - {key}")
                return False
            else:
                print("✅ Verification passed - no wallet keys remain")
                print(f"📋 Remaining keys: {all_keys}")
                return True

    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧹 WALLET DATABASE COMPLETE CLEANUP")
    print("=" * 60)
    print("This will remove ALL existing test wallet addresses")
    print("to eliminate any corruption issues.")
    print()

    # Perform cleanup
    if clean_wallet_database():
        verify_cleanup()
        print()
        print("🎉 Wallet database cleaned successfully!")
        print("🚀 You can now create new wallets without switching issues")
    else:
        print("❌ Cleanup failed - please check error messages above")
