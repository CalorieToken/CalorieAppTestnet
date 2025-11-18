"""
Robust XRPL Transaction Utilities with Multiple Server Failover
Provides robust transaction submission with automatic server switching
"""

import logging
from typing import Any

from xrpl.clients import XRPLRequestFailureException
from xrpl.transaction import submit_and_wait

from src.utils.xrpl_client_manager import get_global_client_manager

# Configure logging for this module
logger = logging.getLogger(__name__)


def robust_submit_and_wait(transaction: Any, wallet: Any, max_retries: int = 3) -> Any:
    """
    Submit a transaction using the robust client manager with automatic failover

    Args:
        transaction: XRPL transaction object
        wallet: Wallet object for signing
        max_retries: Maximum number of server failovers to attempt

    Returns:
        Transaction response object

    Raises:
        XRPLRequestFailureException: If all servers fail
    """
    client_manager = get_global_client_manager()
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            # Get current client from the manager
            current_client = client_manager.get_client()

            if not current_client:
                # Force reconnection if no client available
                if not client_manager.force_reconnect():
                    if last_exception:
                        raise last_exception
                    else:
                        raise XRPLRequestFailureException(
                            "No XRPL servers available for transaction"
                        )
                current_client = client_manager.get_client()

            # Attempt the transaction submission
            logger.info(f"Submitting transaction via {client_manager.get_current_server()}")
            response = submit_and_wait(transaction, current_client, wallet)

            # Debug: log the response type and structure
            logger.info(f"Response type: {type(response)}")
            logger.info(f"Response has result: {hasattr(response, 'result')}")
            if hasattr(response, "result"):
                logger.info(f"Result type: {type(response.result)}")

            # Check if transaction was successful
            if hasattr(response, "result"):
                result = response.result
                if isinstance(result, dict) and "meta" in result:
                    tx_result = result["meta"].get("TransactionResult", "Unknown")
                    if tx_result == "tesSUCCESS":
                        logger.info(
                            f"Transaction successful via {client_manager.get_current_server()}"
                        )
                        return response
                    else:
                        logger.warning(f"Transaction failed with result: {tx_result}")
                        # Don't treat transaction failures as server failures
                        return response
                else:
                    logger.warning(f"Unexpected result format: {type(result)}")
                    return response
            else:
                logger.warning("Response has no result attribute")
                return response

        except XRPLRequestFailureException as e:
            logger.warning(f"Transaction failed on {client_manager.get_current_server()}: {e}")
            last_exception = e

            # Force a reconnection attempt for next iteration
            client_manager.force_reconnect()

            # Don't continue if this was the last attempt
            if attempt >= max_retries:
                break

            continue

        except Exception as e:
            logger.error(
                f"Unexpected error during transaction on {client_manager.get_current_server()}: {e}"
            )

            # Check if this is a transaction failure (not a network error)
            if (
                "Transaction failed" in str(e)
                or "tec" in str(e)
                or "tem" in str(e)
                or "ter" in str(e)
            ):
                # This is a transaction result error, re-raise it
                raise

            last_exception = XRPLRequestFailureException(f"Unexpected error: {e}")

            # Force a reconnection attempt for next iteration
            client_manager.force_reconnect()

            # Don't continue if this was the last attempt
            if attempt >= max_retries:
                break

            continue

    # If we get here, all attempts failed
    if last_exception:
        raise last_exception
    else:
        raise XRPLRequestFailureException(
            "Transaction failed on all XRPL servers after maximum retries"
        )


def get_transaction_status_message(response: Any) -> str:
    """
    Get a user-friendly status message from a transaction response

    Args:
        response: Transaction response object

    Returns:
        User-friendly status message
    """
    try:
        if hasattr(response, "result") and "meta" in response.result:
            tx_result = response.result["meta"].get("TransactionResult", "Unknown")

            if tx_result == "tesSUCCESS":
                return "✅ Transaction completed successfully!"
            # Common tec (failed but fee charged)
            elif tx_result == "tecUNFUNDED_PAYMENT":
                return "❌ Insufficient funds for this transaction"
            elif tx_result == "tecDST_TAG_NEEDED":
                return "❌ Destination tag required for this transaction"
            elif tx_result == "tecNO_DST":
                return "❌ Destination account does not exist"
            elif tx_result == "tecNO_PERMISSION":
                return "❌ Transaction not permitted"
            elif tx_result == "tecNO_LINE":
                return "❌ No trustline exists for the specified currency"
            elif tx_result == "tecPATH_DRY":
                return "❌ No viable payment path (path dry)"
            elif tx_result == "tecINSUFFICIENT_RESERVE":
                return "❌ Not enough XRP reserve to complete this action"
            elif tx_result == "tecUNFUNDED_OFFER":
                return "❌ Offer unfunded"
            elif tx_result == "tecUNFUNDED_PAYMENT":
                return "❌ Insufficient funds for this transaction"
            elif tx_result == "tecNO_AUTH":
                return "❌ Issuer requires authorization for this trustline"
            elif tx_result == "tecINSUF_RESERVE_LINE":
                return "❌ Not enough reserve to create/modify trustline"
            elif tx_result.startswith("tec"):
                return f"❌ Transaction failed: {tx_result}"
            # tem (malformed)
            elif tx_result.startswith("tem"):
                return f"❌ Transaction malformed: {tx_result}"
            # ter (retry later)
            elif tx_result.startswith("ter"):
                return f"❌ Transaction retry later: {tx_result}"
            elif tx_result.startswith("tes"):
                return f"✅ Transaction successful: {tx_result}"
            else:
                return f"❓ Transaction status: {tx_result}"
        else:
            return "❓ Transaction submitted - status unknown"

    except Exception as e:
        logger.error(f"Error parsing transaction response: {e}")
        return "❓ Could not determine transaction status"
