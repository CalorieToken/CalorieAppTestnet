"""
Multi-Faucet Manager for XRPL Testnet
Provides robust faucet functionality with multiple fallback options
"""

import asyncio
import logging
from typing import Optional, Tuple

import aiohttp
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet, generate_faucet_wallet

# Import the robust XRPL client manager
from src.utils.xrpl_client_manager import get_global_client_manager

# Configure logging for this module
logger = logging.getLogger(__name__)


class MultiFaucetManager:
    """
    Manages multiple XRPL testnet faucets with automatic fallback
    """

    def __init__(self, client_manager=None):
        # Use the global robust client manager instead of a single client
        self.client_manager = client_manager or get_global_client_manager()
        self.faucet_configs = [
            {
                "name": "XRPL Labs Testnet (Primary)",
                "method": "library",
                "url": "https://testnet.xrpl-labs.com",
                "timeout": 30,
            },
            {
                "name": "Ripple Altnet Faucet",
                "method": "api",
                "url": "https://faucet.altnet.rippletest.net/accounts",
                "timeout": 20,
            },
            {
                "name": "XRPL Explorer Faucet",
                "method": "api",
                "url": "https://test.xrplexplorer.com/faucet/fund",
                "timeout": 20,
            },
        ]

    def try_xrpl_labs_faucet(self) -> Optional[Wallet]:
        """
        Try the XRPL Labs faucet (built into XRPL library)
        """
        try:
            logger.info("Attempting XRPL Labs faucet...")
            # Create a new event loop for this specific operation
            import concurrent.futures

            def run_faucet():
                # Run in a new event loop
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    # Use the robust client manager
                    current_client = self.client_manager.get_client()
                    if not current_client:
                        return None
                    # Use the standard XRPL library method
                    wallet = generate_faucet_wallet(current_client, debug=True)
                    return wallet
                finally:
                    new_loop.close()

            # Execute in separate thread to avoid event loop conflicts
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_faucet)
                wallet = future.result(timeout=30)
                logger.info(f"✅ XRPL Labs faucet success: {wallet.address}")
                return wallet

        except Exception as e:
            logger.warning(f"❌ XRPL Labs faucet failed: {e}")
            return None

    async def try_altnet_faucet(self, address: str) -> bool:
        """
        Try the Ripple Altnet faucet API
        """
        try:
            logger.info("Attempting Ripple Altnet faucet...")
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                payload = {"destination": address}
                async with session.post(
                    "https://faucet.altnet.rippletest.net/accounts",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ Altnet faucet success: {result}")
                        # Add a small delay to allow transaction to propagate
                        await asyncio.sleep(2)
                        return True
                    else:
                        logger.warning(f"❌ Altnet faucet failed with status {response.status}")
                        return False
        except Exception as e:
            logger.warning(f"❌ Altnet faucet error: {e}")
            return False

    async def try_xrplexplorer_faucet(self, address: str) -> bool:
        """
        Try the XRPL Explorer faucet API
        """
        try:
            logger.info("Attempting XRPL Explorer faucet...")
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                payload = {"address": address}
                async with session.post(
                    "https://test.xrplexplorer.com/faucet/fund",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ XRPL Explorer faucet success: {result}")
                        # Add a small delay to allow transaction to propagate
                        await asyncio.sleep(2)
                        return True
                    else:
                        logger.warning(
                            f"❌ XRPL Explorer faucet failed with status {response.status}"
                        )
                        return False
        except Exception as e:
            logger.warning(f"❌ XRPL Explorer faucet error: {e}")
            return False

    async def generate_funded_wallet(self) -> Tuple[Wallet, str]:
        """
        Generate a wallet and try to fund it using multiple faucets
        Returns: (wallet, funding_status_message)
        """
        # Try primary faucet first (generates wallet + funds in one call)
        wallet = self.try_xrpl_labs_faucet()  # Now synchronous
        if wallet:
            return wallet, "✅ Wallet funded via XRPL Labs faucet"

        # If primary fails, create wallet manually and try alternative faucets
        logger.info("Primary faucet failed, creating unfunded wallet and trying alternatives...")
        wallet = Wallet.create()
        logger.info(f"Created wallet: {wallet.address}")

        # Try alternative faucets
        funding_attempts = [
            ("Ripple Altnet", self.try_altnet_faucet(wallet.address)),
            ("XRPL Explorer", self.try_xrplexplorer_faucet(wallet.address)),
        ]

        for faucet_name, funding_task in funding_attempts:
            try:
                success = await funding_task
                if success:
                    return wallet, f"✅ Wallet funded via {faucet_name} faucet"
            except Exception as e:
                logger.warning(f"Failed to fund via {faucet_name}: {e}")
                continue

        # If all faucets fail
        return wallet, "⚠️  All faucets unavailable - wallet created unfunded"

    def generate_funded_wallet_sync(self) -> Tuple[Wallet, str]:
        """
        Synchronous wrapper for generate_funded_wallet
        """
        try:
            # Try primary faucet first (now thread-safe)
            wallet = self.try_xrpl_labs_faucet()
            if wallet:
                return wallet, "✅ Wallet funded via XRPL Labs faucet"

            # If primary fails, create wallet manually and try alternative faucets
            logger.info(
                "Primary faucet failed, creating unfunded wallet and trying alternatives..."
            )
            wallet = Wallet.create()
            logger.info(f"Created wallet: {wallet.address}")

            # Try alternative faucets in separate thread
            def run_async_faucets():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    # Try only Altnet faucet to avoid the xrplexplorer coroutine issue
                    success = new_loop.run_until_complete(self.try_altnet_faucet(wallet.address))
                    if success:
                        return "✅ Wallet funded via Ripple Altnet faucet"
                    else:
                        return "⚠️  Faucets unavailable - wallet created unfunded"
                finally:
                    new_loop.close()

            # Run in separate thread to avoid event loop conflicts
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_async_faucets)
                status_message = future.result(timeout=60)
                return wallet, status_message

        except concurrent.futures.TimeoutError:
            logger.error("Faucet operations timed out")
            wallet = Wallet.create()
            return wallet, "❌ Faucet timeout - wallet created unfunded"
        except Exception as e:
            logger.error(f"Error in sync wrapper: {e}")
            # Fallback to basic wallet creation
            wallet = Wallet.create()
            return wallet, f"❌ Faucet system error: {e}"


def create_faucet_manager(client_manager=None) -> MultiFaucetManager:
    """
    Factory function to create a MultiFaucetManager instance
    """
    return MultiFaucetManager(client_manager)


# Backward compatibility function
def generate_multi_faucet_wallet(client: JsonRpcClient = None) -> Tuple[Wallet, str]:
    """
    Legacy function for easy integration
    Returns: (wallet, status_message)
    """
    # Use the global client manager instead of the provided client
    manager = MultiFaucetManager()
    return manager.generate_funded_wallet_sync()


# New helper to fund an existing address (synchronously)
def fund_existing_address_sync(address: str) -> str:
    """Attempt to fund an existing XRPL Testnet address using multiple faucets.

    Tries Ripple Altnet first (reliable), then XRPL Explorer. Returns a concise
    status message indicating success or failure.
    """
    try:
        mgr = MultiFaucetManager()

        # Run async faucets in an isolated thread/loop to avoid UI event loop conflicts
        import concurrent.futures

        def _run():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                # Try Altnet faucet first
                success = new_loop.run_until_complete(mgr.try_altnet_faucet(address))
                if success:
                    return "✅ Wallet funded via Ripple Altnet faucet"
                # Try XRPL Explorer faucet as a fallback
                success2 = new_loop.run_until_complete(mgr.try_xrplexplorer_faucet(address))
                if success2:
                    return "✅ Wallet funded via XRPL Explorer faucet"
                return "⚠️ Faucets unavailable - wallet remains unfunded"
            finally:
                new_loop.close()

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            future = ex.submit(_run)
            return future.result(timeout=60)
    except concurrent.futures.TimeoutError:
        return "❌ Faucet timeout - wallet remains unfunded"
    except Exception as e:
        logger.warning(f"Funding error: {e}")
        return "❌ Faucet error - wallet remains unfunded"
