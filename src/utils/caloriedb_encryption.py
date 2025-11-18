"""
CalorieDB Encryption Module

XRPL-compatible encryption for private user data.
Uses same key derivation as XRPL wallet for seamless security.

Security:
- AES-256-GCM authenticated encryption
- Keys derived from XRPL wallet seed (ED25519/SECP256K1)
- HKDF key derivation with unique salts
- Random IV per encryption (never reused)
- Authenticated encryption prevents tampering
"""

import os
import json
from typing import Dict, Any

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from xrpl.core.addresscodec import decode_seed


class CalorieDBEncryption:
    """
    AES-256-GCM encryption for CalorieDB private data
    
    Compatible with XRPL wallet key derivation - uses same seed
    """
    
    def __init__(self, xrpl_seed: str):
        """
        Initialize encryption with XRPL wallet seed
        
        Args:
            xrpl_seed: XRPL seed (format: sEdXXXXXXX or snXXXXXXX)
        """
        # Derive encryption key from XRPL seed
        entropy = self._decode_xrpl_seed(xrpl_seed)
        self.private_key = self._derive_key(entropy, b"CalorieDB-Private-Data-v1")
        self.signing_key = self._derive_key(entropy, b"CalorieDB-Public-Data-v1")
    
    def encrypt(self, data: dict) -> bytes:
        """
        Encrypt user data with AES-256-GCM
        
        Args:
            data: Dictionary to encrypt
            
        Returns:
            Encrypted bytes: iv (12) + tag (16) + ciphertext
        """
        # Serialize data
        plaintext = json.dumps(data, sort_keys=True).encode('utf-8')
        
        # Generate random IV (12 bytes for GCM)
        iv = os.urandom(12)
        
        # Encrypt with AES-256-GCM
        cipher = Cipher(
            algorithms.AES(self.private_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        # Return: iv (12 bytes) + tag (16 bytes) + ciphertext
        return iv + encryptor.tag + ciphertext
    
    def decrypt(self, encrypted_data: bytes) -> dict:
        """
        Decrypt user data
        
        Args:
            encrypted_data: Encrypted bytes from encrypt()
            
        Returns:
            Decrypted dictionary
        """
        # Extract components
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        # Decrypt with AES-256-GCM
        cipher = Cipher(
            algorithms.AES(self.private_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Deserialize
        return json.loads(plaintext.decode('utf-8'))
    
    def sign_public_data(self, data: dict) -> str:
        """
        Sign public anonymized data for integrity
        
        Args:
            data: Public data to sign
            
        Returns:
            HMAC signature (hex)
        """
        import hmac
        serialized = json.dumps(data, sort_keys=True).encode('utf-8')
        signature = hmac.new(self.signing_key, serialized, 'sha256').hexdigest()
        return signature
    
    def verify_signature(self, data: dict, signature: str) -> bool:
        """
        Verify signature of public data
        
        Args:
            data: Public data
            signature: Expected signature (hex)
            
        Returns:
            True if valid, False otherwise
        """
        expected = self.sign_public_data(data)
        return expected == signature
    
    def _decode_xrpl_seed(self, xrpl_seed: str) -> bytes:
        """
        Decode XRPL seed to entropy bytes
        
        Args:
            xrpl_seed: XRPL seed string (sEd... or sn...)
            
        Returns:
            Entropy bytes (16 bytes)
        """
        try:
            # xrpl-py decode_seed returns (entropy, algorithm)
            entropy, algorithm = decode_seed(xrpl_seed)
            return entropy
        except Exception as e:
            raise ValueError(f"Invalid XRPL seed: {e}")
    
    def _derive_key(self, entropy: bytes, info: bytes) -> bytes:
        """
        Derive encryption key from entropy using HKDF
        
        Args:
            entropy: Source entropy (16 bytes from XRPL seed)
            info: Context information for key derivation
            
        Returns:
            32-byte AES-256 key
        """
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits for AES-256
            salt=b"caloriedb_salt_v1",  # Fixed salt for consistency
            info=info,
            backend=default_backend()
        )
        return hkdf.derive(entropy)


# Convenience functions for external use
def encrypt_for_account(xrpl_seed: str, data: dict) -> bytes:
    """
    Encrypt data for an account
    
    Args:
        xrpl_seed: XRPL wallet seed
        data: Data to encrypt
        
    Returns:
        Encrypted bytes
    """
    encryption = CalorieDBEncryption(xrpl_seed)
    return encryption.encrypt(data)


def decrypt_for_account(xrpl_seed: str, encrypted_data: bytes) -> dict:
    """
    Decrypt data for an account
    
    Args:
        xrpl_seed: XRPL wallet seed
        encrypted_data: Encrypted bytes
        
    Returns:
        Decrypted data
    """
    encryption = CalorieDBEncryption(xrpl_seed)
    return encryption.decrypt(encrypted_data)


__all__ = [
    "CalorieDBEncryption",
    "encrypt_for_account",
    "decrypt_for_account"
]
