"""
Pro Issuer Features for CalorieAppTestnet

Advanced token issuance and management capabilities for Pro accounts.
Includes token creation, trustline management, and issuer controls.

REQUIRES: Pro account license
"""

import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import (
    TrustSet, Payment, AccountSet,
    NFTokenMint, NFTokenBurn, NFTokenCreateOffer
)
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import AccountInfo, AccountLines, AccountObjects
from xrpl.transaction import safe_sign_and_autofill_transaction, send_reliable_submission
from xrpl.core.keypairs import derive_classic_address
from typing import Optional, Dict, List, Any
import json


class ProIssuerManager:
    """
    Advanced token issuer capabilities for Pro accounts
    
    Features:
    - Custom token issuance
    - Trustline management
    - Issuer controls (freeze, blacklist)
    - Batch operations
    """
    
    def __init__(self, client: JsonRpcClient):
        self.client = client
    
    def create_custom_token(
        self,
        issuer_wallet: Wallet,
        currency_code: str,
        total_supply: float,
        require_auth: bool = False,
        allow_rippling: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new custom token (Pro feature)
        
        Args:
            issuer_wallet: The issuer's wallet
            currency_code: 3-letter or hex currency code
            total_supply: Total token supply
            require_auth: Whether to require authorization for trustlines
            allow_rippling: Whether to allow rippling
            
        Returns:
            Dict with token creation result
        """
        try:
            # Configure issuer account settings
            account_set_flags = 0
            
            if require_auth:
                account_set_flags |= 0x00040000  # asfRequireAuth
            if not allow_rippling:
                account_set_flags |= 0x00080000  # asfDisallowXRP (example flag)
            
            # Set account flags if needed
            if account_set_flags > 0:
                account_set_tx = AccountSet(
                    account=issuer_wallet.classic_address,
                    set_flag=account_set_flags
                )
                signed_tx = safe_sign_and_autofill_transaction(account_set_tx, issuer_wallet, self.client)
                response = send_reliable_submission(signed_tx, self.client)
                
                if response.result.get('meta', {}).get('TransactionResult') != 'tesSUCCESS':
                    return {
                        'success': False,
                        'error': f"Failed to set account flags: {response.result}"
                    }
            
            # Token creation details
            result = {
                'success': True,
                'issuer_address': issuer_wallet.classic_address,
                'currency_code': currency_code,
                'currency_hex': self._currency_to_hex(currency_code),
                'total_supply': total_supply,
                'require_auth': require_auth,
                'allow_rippling': allow_rippling,
                'timestamp': xrpl.utils.datetime_to_ripple_time()
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def issue_tokens_to_holder(
        self,
        issuer_wallet: Wallet,
        holder_address: str,
        currency_code: str,
        amount: float
    ) -> Dict[str, Any]:
        """
        Issue tokens to a holder (Pro feature)
        
        The holder must have a trustline set to the issuer first.
        
        Args:
            issuer_wallet: Issuer's wallet
            holder_address: Recipient XRPL address
            currency_code: Currency code
            amount: Amount to issue
            
        Returns:
            Transaction result
        """
        try:
            # Create payment transaction
            payment_tx = Payment(
                account=issuer_wallet.classic_address,
                destination=holder_address,
                amount=IssuedCurrencyAmount(
                    currency=self._currency_to_hex(currency_code),
                    issuer=issuer_wallet.classic_address,
                    value=str(amount)
                )
            )
            
            # Sign and submit
            signed_tx = safe_sign_and_autofill_transaction(payment_tx, issuer_wallet, self.client)
            response = send_reliable_submission(signed_tx, self.client)
            
            result_code = response.result.get('meta', {}).get('TransactionResult', 'UNKNOWN')
            
            return {
                'success': result_code == 'tesSUCCESS',
                'transaction_hash': response.result.get('hash'),
                'result_code': result_code,
                'ledger_index': response.result.get('ledger_index'),
                'amount_issued': amount,
                'recipient': holder_address
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_token_holders(
        self,
        issuer_address: str,
        currency_code: str
    ) -> List[Dict[str, Any]]:
        """
        Get list of accounts holding the token (Pro feature)
        
        Args:
            issuer_address: Token issuer address
            currency_code: Currency code
            
        Returns:
            List of holder information
        """
        try:
            # Get account lines (trustlines)
            account_lines_request = AccountLines(
                account=issuer_address,
                ledger_index="validated"
            )
            
            response = self.client.request(account_lines_request)
            
            if response.status != "success":
                return []
            
            currency_hex = self._currency_to_hex(currency_code)
            holders = []
            
            for line in response.result.get('lines', []):
                if line.get('currency') == currency_hex:
                    holders.append({
                        'account': line.get('account'),
                        'balance': float(line.get('balance', 0)),
                        'limit': float(line.get('limit', 0)),
                        'quality_in': line.get('quality_in', 0),
                        'quality_out': line.get('quality_out', 0)
                    })
            
            return holders
            
        except Exception as e:
            print(f"Error getting token holders: {e}")
            return []
    
    def freeze_trustline(
        self,
        issuer_wallet: Wallet,
        holder_address: str,
        currency_code: str,
        freeze: bool = True
    ) -> Dict[str, Any]:
        """
        Freeze or unfreeze a trustline (Pro feature - issuer control)
        
        Args:
            issuer_wallet: Issuer's wallet
            holder_address: Holder's address
            currency_code: Currency code
            freeze: True to freeze, False to unfreeze
            
        Returns:
            Transaction result
        """
        try:
            # Create TrustSet transaction with freeze flag
            flags = 0x00010000 if freeze else 0x00020000  # SetFreeze or ClearFreeze
            
            trust_set_tx = TrustSet(
                account=issuer_wallet.classic_address,
                flags=flags,
                limit_amount=IssuedCurrencyAmount(
                    currency=self._currency_to_hex(currency_code),
                    issuer=holder_address,  # From issuer's perspective
                    value="0"
                )
            )
            
            signed_tx = safe_sign_and_autofill_transaction(trust_set_tx, issuer_wallet, self.client)
            response = send_reliable_submission(signed_tx, self.client)
            
            result_code = response.result.get('meta', {}).get('TransactionResult', 'UNKNOWN')
            
            return {
                'success': result_code == 'tesSUCCESS',
                'action': 'freeze' if freeze else 'unfreeze',
                'transaction_hash': response.result.get('hash'),
                'result_code': result_code
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def authorize_trustline(
        self,
        issuer_wallet: Wallet,
        holder_address: str,
        currency_code: str,
        authorize: bool = True
    ) -> Dict[str, Any]:
        """
        Authorize or revoke authorization for a trustline (Pro feature)
        
        Requires asfRequireAuth to be enabled on issuer account.
        
        Args:
            issuer_wallet: Issuer's wallet
            holder_address: Holder's address
            currency_code: Currency code
            authorize: True to authorize, False to revoke
            
        Returns:
            Transaction result
        """
        try:
            # TrustSet with authorization flags
            flags = 0x00010000 if authorize else 0x00020000
            
            trust_set_tx = TrustSet(
                account=issuer_wallet.classic_address,
                flags=flags,
                limit_amount=IssuedCurrencyAmount(
                    currency=self._currency_to_hex(currency_code),
                    issuer=holder_address,
                    value="0"
                )
            )
            
            signed_tx = safe_sign_and_autofill_transaction(trust_set_tx, issuer_wallet, self.client)
            response = send_reliable_submission(signed_tx, self.client)
            
            result_code = response.result.get('meta', {}).get('TransactionResult', 'UNKNOWN')
            
            return {
                'success': result_code == 'tesSUCCESS',
                'action': 'authorize' if authorize else 'revoke',
                'transaction_hash': response.result.get('hash'),
                'result_code': result_code
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def batch_issue_tokens(
        self,
        issuer_wallet: Wallet,
        recipients: List[Dict[str, Any]],
        currency_code: str
    ) -> Dict[str, Any]:
        """
        Issue tokens to multiple recipients in batch (Pro feature)
        
        Args:
            issuer_wallet: Issuer's wallet
            recipients: List of {'address': ..., 'amount': ...}
            currency_code: Currency code
            
        Returns:
            Batch operation results
        """
        results = []
        successful = 0
        failed = 0
        
        for recipient in recipients:
            result = self.issue_tokens_to_holder(
                issuer_wallet,
                recipient['address'],
                currency_code,
                recipient['amount']
            )
            
            results.append({
                'recipient': recipient['address'],
                'amount': recipient['amount'],
                **result
            })
            
            if result.get('success'):
                successful += 1
            else:
                failed += 1
        
        return {
            'total': len(recipients),
            'successful': successful,
            'failed': failed,
            'results': results
        }
    
    def get_issuer_statistics(
        self,
        issuer_address: str,
        currency_code: str
    ) -> Dict[str, Any]:
        """
        Get statistics for issued token (Pro feature)
        
        Args:
            issuer_address: Issuer address
            currency_code: Currency code
            
        Returns:
            Token statistics
        """
        try:
            holders = self.get_token_holders(issuer_address, currency_code)
            
            total_issued = sum(holder['balance'] for holder in holders)
            active_holders = len([h for h in holders if h['balance'] > 0])
            
            return {
                'currency_code': currency_code,
                'issuer_address': issuer_address,
                'total_holders': len(holders),
                'active_holders': active_holders,
                'total_issued': total_issued,
                'holders': holders
            }
            
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def _currency_to_hex(self, currency_code: str) -> str:
        """Convert currency code to hex format"""
        if len(currency_code) == 3:
            # Standard 3-letter code
            hex_code = currency_code.encode('ASCII').hex().upper()
            # Pad to 40 characters
            return hex_code + '0' * (40 - len(hex_code))
        elif len(currency_code) == 40:
            # Already hex format
            return currency_code.upper()
        else:
            # Convert any string to hex and pad
            hex_code = currency_code.encode('ASCII').hex().upper()
            if len(hex_code) > 40:
                hex_code = hex_code[:40]
            else:
                hex_code = hex_code + '0' * (40 - len(hex_code))
            return hex_code
    
    def _hex_to_currency(self, hex_code: str) -> str:
        """Convert hex currency code to readable format"""
        try:
            # Remove trailing zeros
            hex_code = hex_code.rstrip('0')
            if len(hex_code) % 2 != 0:
                hex_code += '0'
            
            # Convert to ASCII
            currency = bytes.fromhex(hex_code).decode('ASCII', errors='ignore')
            return currency.strip('\x00')
        except:
            return hex_code


# Export
__all__ = ['ProIssuerManager']
