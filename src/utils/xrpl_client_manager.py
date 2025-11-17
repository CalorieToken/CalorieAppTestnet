"""
XRPL Client Manager with Multiple Server Failover
Provides robust XRPL connectivity with automatic server switching
"""

import logging
import time
from typing import Any, List, Optional

from xrpl.clients import JsonRpcClient, XRPLRequestFailureException
from xrpl.models.requests import AccountInfo, AccountTx, Fee, LedgerCurrent, ServerInfo

# Configure logging for this module
logger = logging.getLogger(__name__)


class XRPLClientManager:
    """
    Manages XRPL client connections with automatic failover to backup servers
    """

    def __init__(self, servers: Optional[List[str]] = None, timeout: int = 10):
        """
        Initialize the client manager

        Args:
            servers: List of XRPL server URLs to try
            timeout: Timeout in seconds for each server attempt
        """
        self.servers = servers or [
            "https://testnet.xrpl-labs.com",  # Primary: XRPL Labs testnet
            "https://s.altnet.rippletest.net:51234",  # Backup: Ripple altnet
            "https://testnet.xrplapi.com",  # Backup: Another testnet API
            "https://xrplcluster.com",  # Backup: Community cluster (if available)
        ]
        self.timeout = timeout
        self.current_client = None
        self.current_server = None
        self.failed_servers = set()  # Track failed servers to avoid rapid retries
        self.last_failure_time = {}  # Track when each server last failed
        self.retry_delay = 300  # 5 minutes before retrying a failed server

        # Simple in-memory cache for selected XRPL request responses
        # Structure: { cache_key: (timestamp, response) }
        self._cache = {}
        # TTL mapping per request type for fine-grained caching
        self.cache_ttl_map = {
            ServerInfo: 30,
            Fee: 15,
            LedgerCurrent: 10,
            # Short TTL caching for high-frequency calls to reduce churn
            AccountInfo: 6,
            AccountTx: 6,
        }
        self.cacheable_request_types = set(self.cache_ttl_map.keys())

        # Initialize connection
        self._connect_to_best_server()

    def _connect_to_best_server(self) -> bool:
        """
        Try to connect to the best available server

        Returns:
            bool: True if connected successfully, False otherwise
        """
        current_time = time.time()

        # Reset failed servers that haven't been tried for retry_delay seconds
        servers_to_retry = []
        for server in list(self.failed_servers):
            if current_time - self.last_failure_time.get(server, 0) > self.retry_delay:
                servers_to_retry.append(server)
                self.failed_servers.discard(server)

        if servers_to_retry:
            logger.info(f"Retrying previously failed servers: {servers_to_retry}")

        # Try servers in order, skipping recently failed ones
        for server_url in self.servers:
            if server_url in self.failed_servers:
                continue

            try:
                logger.info(f"Attempting to connect to: {server_url}")
                client = JsonRpcClient(server_url)

                # Test the connection with a simple request
                test_request = ServerInfo()
                response = client.request(test_request)

                if hasattr(response, "status") and response.status.name == "SUCCESS":
                    logger.info(f"✅ Successfully connected to: {server_url}")
                    self.current_client = client
                    self.current_server = server_url
                    return True
                else:
                    logger.warning(f"❌ Server {server_url} responded but not successfully")
                    self._mark_server_failed(server_url)

            except Exception as e:
                logger.warning(f"❌ Failed to connect to {server_url}: {e}")
                self._mark_server_failed(server_url)
                continue

        logger.error("❌ Could not connect to any XRPL servers")
        self.current_client = None
        self.current_server = None
        return False

    def _mark_server_failed(self, server_url: str):
        """Mark a server as failed and record the failure time"""
        self.failed_servers.add(server_url)
        self.last_failure_time[server_url] = time.time()

    def request(self, request_obj: Any, max_retries: int = 3) -> Any:
        """
        Make a request with automatic failover

        Args:
            request_obj: XRPL request object
            max_retries: Maximum number of server failovers to attempt

        Returns:
            Response object from XRPL server

        Raises:
            XRPLRequestFailureException: If all servers fail
        """
        last_exception = None
        cache_key = None
        # Attempt cache lookup if request is cacheable
        if type(request_obj) in self.cacheable_request_types:
            cache_key = type(request_obj).__name__
            cached = self._cache.get(cache_key)
            if cached:
                ts, resp = cached
                ttl = self.cache_ttl_map.get(type(request_obj), 0)
                if time.time() - ts < ttl:
                    logger.debug(f"Cache hit for {cache_key}")
                    return resp
                self._cache.pop(cache_key, None)

        for attempt in range(max_retries + 1):
            # If we don't have a current client, try to connect
            if not self.current_client:
                if not self._connect_to_best_server():
                    # If we can't connect to any server, raise the last exception
                    if last_exception:
                        raise last_exception
                    else:
                        raise XRPLRequestFailureException(
                            result={"error": "no_servers", "message": "No XRPL servers available"}
                        )

            try:
                # Attempt the request
                # Guard: current_client should not be None here, but be defensive
                if self.current_client is None:
                    raise XRPLRequestFailureException(
                        result={"error": "no_client", "message": "XRPL client unavailable"}
                    )
                response = self.current_client.request(request_obj)

                # Check if response indicates success
                if hasattr(response, "status") and response.status.name == "SUCCESS":
                    # Store in cache if applicable
                    if cache_key:
                        self._cache[cache_key] = (time.time(), response)
                    return response
                elif hasattr(response, "result") and "error" in response.result:
                    # This is a valid response with an error (like account not found)
                    # Don't treat this as a server failure
                    if cache_key:
                        self._cache[cache_key] = (time.time(), response)
                    return response
                else:
                    # Unknown response format, treat as server issue
                    logger.warning(f"Unknown response format from {self.current_server}")
                    if self.current_server is not None:
                        self._mark_server_failed(self.current_server)
                    self.current_client = None
                    continue

            except XRPLRequestFailureException as e:
                logger.warning(f"Request failed on {self.current_server}: {e}")
                last_exception = e

                # Mark current server as failed and try next one
                if self.current_server:
                    self._mark_server_failed(self.current_server)
                self.current_client = None

                # Don't continue if this was the last attempt
                if attempt >= max_retries:
                    break

                # Try to connect to next server
                continue

            except Exception as e:
                logger.error(f"Unexpected error on {self.current_server}: {e}")
                last_exception = XRPLRequestFailureException(
                    result={"error": "unexpected", "message": str(e)}
                )

                # Mark current server as failed and try next one
                if self.current_server:
                    if self.current_server is not None:
                        self._mark_server_failed(self.current_server)
                self.current_client = None

                # Don't continue if this was the last attempt
                if attempt >= max_retries:
                    break

                continue

        # If we get here, all attempts failed
        if last_exception:
            raise last_exception
        else:
            raise XRPLRequestFailureException(
                result={
                    "error": "exhausted",
                    "message": "All XRPL servers failed after maximum retries",
                }
            )

    def clear_cache(self):
        """Clear all cached XRPL responses."""
        self._cache.clear()
        logger.info("XRPL client cache cleared.")

    def get_current_server(self) -> Optional[str]:
        """Get the currently connected server URL"""
        return self.current_server

    def get_client(self) -> Optional[JsonRpcClient]:
        """Get the current client (may be None if no connection)"""
        return self.current_client

    def is_connected(self) -> bool:
        """Check if currently connected to a server"""
        return self.current_client is not None

    def force_reconnect(self):
        """Force a reconnection attempt to all servers"""
        logger.info("Forcing reconnection...")
        self.current_client = None
        self.current_server = None
        self.failed_servers.clear()  # Clear failed servers list for immediate retry
        self.last_failure_time.clear()
        return self._connect_to_best_server()

    def get_status(self) -> dict:
        """Get detailed status information"""
        return {
            "connected": self.is_connected(),
            "current_server": self.current_server,
            "failed_servers": list(self.failed_servers),
            "available_servers": [s for s in self.servers if s not in self.failed_servers],
            "last_failure_times": self.last_failure_time.copy(),
        }


# Global instance for easy access throughout the app
_global_client_manager = None


def get_global_client_manager() -> XRPLClientManager:
    """Get or create the global XRPL client manager instance"""
    global _global_client_manager
    if _global_client_manager is None:
        _global_client_manager = XRPLClientManager()
    return _global_client_manager


def reset_global_client_manager():
    """Reset the global client manager (useful for testing or configuration changes)"""
    global _global_client_manager
    _global_client_manager = None
    logger.info("Global XRPL client manager reset; cache cleared on next init.")


# Convenience functions for backward compatibility
def make_request(request_obj: Any) -> Any:
    """Make a request using the global client manager"""
    return get_global_client_manager().request(request_obj)


def online_status() -> bool:
    """Check if we have an online XRPL connection (alias for is_online)."""
    return get_global_client_manager().is_connected()


def get_reserve_requirements() -> dict:
    """
    Fetch current reserve requirements from the XRPL server.

    Returns:
        dict: {
            'base_reserve_xrp': float,  # Base reserve in XRP (e.g., 10)
            'owner_reserve_xrp': float,  # Per-object reserve in XRP (e.g., 2)
            'available': bool           # Whether data was fetched successfully
        }
    """
    try:
        from xrpl.models.requests import ServerInfo

        client_manager = get_global_client_manager()

        if not client_manager.is_connected():
            logger.warning("Not connected to XRPL - cannot fetch reserve requirements")
            return {"base_reserve_xrp": 10.0, "owner_reserve_xrp": 2.0, "available": False}

        server_info_req = ServerInfo()
        response = client_manager.request(server_info_req)

        if hasattr(response, "status") and response.status.name == "SUCCESS":
            result = response.result
            if "info" in result and "validated_ledger" in result["info"]:
                validated = result["info"]["validated_ledger"]
                # Reserve values are in drops
                base_reserve_drops = int(validated.get("reserve_base_xrp", 10000000))
                owner_reserve_drops = int(validated.get("reserve_inc_xrp", 2000000))

                return {
                    "base_reserve_xrp": base_reserve_drops / 1_000_000,
                    "owner_reserve_xrp": owner_reserve_drops / 1_000_000,
                    "available": True,
                }

        logger.warning("Could not parse reserve requirements from server_info response")
        return {"base_reserve_xrp": 10.0, "owner_reserve_xrp": 2.0, "available": False}

    except Exception as e:
        logger.error(f"Error fetching reserve requirements: {e}")
        return {"base_reserve_xrp": 10.0, "owner_reserve_xrp": 2.0, "available": False}


def get_current_client() -> Optional[JsonRpcClient]:
    """Get the current client from the global manager"""
    return get_global_client_manager().get_client()


def is_online() -> bool:
    """Check if we have an active XRPL connection"""
    return get_global_client_manager().is_connected()
