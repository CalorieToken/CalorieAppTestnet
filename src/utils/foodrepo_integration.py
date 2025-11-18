"""
FoodRepo API Integration for CalorieDB

Ingests data from The Open Food Repo (https://www.foodrepo.org) and transforms it
into CalorieDB format with BigchainDB + IPFS storage.

API Documentation: https://www.foodrepo.org/api-docs/swaggers/v3
License: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

Features:
- Paginated data fetching (max 200 products per page)
- Product normalization to CalorieDB schema
- BigchainDB asset creation for public records
- IPFS content addressing for product data
- Rate limiting and error handling
"""

import os
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Iterator
from pathlib import Path
from datetime import datetime

try:
    import httpx
except ImportError:
    httpx = None

from .decentralized.ipfs_client import get_ipfs_client
from .decentralized.bigchaindb_client import get_bigchaindb_client


class FoodRepoClient:
    """
    Client for The Open Food Repo API v3
    
    Requires API key from https://www.foodrepo.org
    Set environment variable: FOODREPO_API_KEY
    """
    
    BASE_URL = "https://www.foodrepo.org/api/v3"
    MAX_PAGE_SIZE = 200  # API maximum
    DEFAULT_PAGE_SIZE = 100
    RATE_LIMIT_DELAY = 1.0  # Seconds between requests (be polite)
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("FOODREPO_API_KEY", "")
        if not self.api_key:
            raise ValueError("FOODREPO_API_KEY environment variable not set")
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f'Token token="{self.api_key}"'
        }
        
        if httpx is None:
            raise ImportError("httpx required for FoodRepo integration: pip install httpx")
        
        self.client = httpx.Client(
            timeout=30.0,
            headers=self.headers,
            follow_redirects=True
        )
    
    def get_products_page(
        self,
        page_number: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        excludes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get a single page of products
        
        Args:
            page_number: Page number (1-indexed)
            page_size: Products per page (max 200)
            excludes: Fields to exclude (e.g., ["images", "nutrients"])
            
        Returns:
            API response with data, links, meta
        """
        params = {
            "page[number]": page_number,
            "page[size]": min(page_size, self.MAX_PAGE_SIZE)
        }
        
        if excludes:
            params["excludes"] = ",".join(excludes)
        
        response = self.client.get(f"{self.BASE_URL}/products", params=params)
        response.raise_for_status()
        
        # Rate limiting - be polite
        time.sleep(self.RATE_LIMIT_DELAY)
        
        return response.json()
    
    def iter_all_products(
        self,
        page_size: int = DEFAULT_PAGE_SIZE,
        excludes: Optional[List[str]] = None,
        max_products: Optional[int] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Iterator over all products in FoodRepo database
        
        Uses pagination with links.next for efficient crawling
        
        Args:
            page_size: Products per page
            excludes: Fields to exclude
            max_products: Maximum products to fetch (None = all)
            
        Yields:
            Individual product dictionaries
        """
        page = 1
        total_fetched = 0
        
        while True:
            print(f"Fetching FoodRepo page {page}...")
            
            try:
                result = self.get_products_page(page, page_size, excludes)
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                break
            
            products = result.get("data", [])
            
            if not products:
                break
            
            for product in products:
                yield product
                total_fetched += 1
                
                if max_products and total_fetched >= max_products:
                    return
            
            # Check if there's a next page
            next_url = result.get("links", {}).get("next")
            if not next_url:
                break
            
            page += 1
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get a single product by ID"""
        try:
            response = self.client.get(f"{self.BASE_URL}/products/{product_id}")
            response.raise_for_status()
            time.sleep(self.RATE_LIMIT_DELAY)
            return response.json().get("data")
        except Exception as e:
            print(f"Error fetching product {product_id}: {e}")
            return None
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get product by barcode"""
        try:
            response = self.client.get(
                f"{self.BASE_URL}/products",
                params={"barcodes": barcode}
            )
            response.raise_for_status()
            time.sleep(self.RATE_LIMIT_DELAY)
            
            products = response.json().get("data", [])
            return products[0] if products else None
        except Exception as e:
            print(f"Error fetching barcode {barcode}: {e}")
            return None
    
    def search_products(
        self,
        query: str,
        fields: Optional[List[str]] = None,
        size: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search products using ElasticSearch
        
        Args:
            query: Search query (fuzzy search supported with ~)
            fields: Fields to search in (e.g., ["name_translations.en"])
            size: Number of results
            
        Returns:
            List of matching products
        """
        if not fields:
            fields = ["name_translations.*"]
        
        elastic_query = {
            "_source": {
                "includes": [
                    "name_translations",
                    "barcode",
                    "nutrients",
                    "ingredients_translations"
                ]
            },
            "size": size,
            "query": {
                "query_string": {
                    "fields": fields,
                    "query": query
                }
            }
        }
        
        try:
            response = self.client.post(
                f"{self.BASE_URL}/products/_search",
                json=elastic_query
            )
            response.raise_for_status()
            time.sleep(self.RATE_LIMIT_DELAY)
            
            hits = response.json().get("hits", {}).get("hits", [])
            return [hit["_source"] for hit in hits]
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
    
    def close(self):
        """Close HTTP client"""
        self.client.close()


class FoodRepoToCalorieDBTransformer:
    """
    Transforms FoodRepo data format to CalorieDB schema
    
    Maps FoodRepo fields to standardized CalorieDB structure
    """
    
    @staticmethod
    def transform_product(foodrepo_product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform FoodRepo product to CalorieDB format
        
        Args:
            foodrepo_product: Raw FoodRepo product data
            
        Returns:
            CalorieDB-formatted product
        """
        # Extract basic info
        product_id = foodrepo_product.get("id")
        barcode = foodrepo_product.get("barcode", "")
        
        # Name translations (prefer English, fallback to any available)
        name_translations = foodrepo_product.get("name_translations", {})
        name = (
            name_translations.get("en") or
            name_translations.get("de") or
            name_translations.get("fr") or
            name_translations.get("it") or
            next(iter(name_translations.values()), "Unknown Product")
        )
        
        # Nutrients - normalize to per 100g
        nutrients_raw = foodrepo_product.get("nutrients", {})
        nutrients = FoodRepoToCalorieDBTransformer._normalize_nutrients(nutrients_raw)
        
        # Ingredients
        ingredients_translations = foodrepo_product.get("ingredients_translations", {})
        ingredients = (
            ingredients_translations.get("en") or
            ingredients_translations.get("de") or
            ingredients_translations.get("fr") or
            ""
        )
        
        # Images
        images = foodrepo_product.get("images", [])
        image_urls = [img.get("xlarge") or img.get("large") or img.get("medium") 
                      for img in images if isinstance(img, dict)]
        
        # Allergens
        allergens = foodrepo_product.get("allergens", [])
        
        # Build CalorieDB product
        caloriedb_product = {
            "product_id": f"foodrepo_{product_id}",
            "source": "foodrepo",
            "barcode": barcode,
            "name": name,
            "name_translations": name_translations,
            
            # Nutritional data (per 100g)
            "calories": nutrients.get("energy_kcal", 0),
            "nutrients": {
                "energy_kcal": nutrients.get("energy_kcal", 0),
                "energy_kj": nutrients.get("energy_kj", 0),
                "protein_g": nutrients.get("protein_g", 0),
                "carbohydrates_g": nutrients.get("carbohydrates_g", 0),
                "sugars_g": nutrients.get("sugars_g", 0),
                "fat_g": nutrients.get("fat_g", 0),
                "saturated_fat_g": nutrients.get("saturated_fat_g", 0),
                "fiber_g": nutrients.get("fiber_g", 0),
                "sodium_mg": nutrients.get("sodium_mg", 0),
                "salt_g": nutrients.get("salt_g", 0),
            },
            
            # Ingredients
            "ingredients": ingredients,
            "allergens": allergens,
            
            # Images
            "image_urls": image_urls,
            "primary_image": image_urls[0] if image_urls else None,
            
            # Metadata
            "country": foodrepo_product.get("country", ""),
            "brands": foodrepo_product.get("brands", []),
            "categories": foodrepo_product.get("categories", []),
            
            # Source tracking
            "foodrepo_id": product_id,
            "foodrepo_url": f"https://www.foodrepo.org/products/{product_id}",
            "imported_at": datetime.utcnow().isoformat() + "Z",
            "data_version": "1.0"
        }
        
        return caloriedb_product
    
    @staticmethod
    def _normalize_nutrients(nutrients_raw: Dict[str, Any]) -> Dict[str, float]:
        """
        Normalize nutrients to per 100g values
        
        FoodRepo provides nutrients with per_hundred, per_serving, per_portion
        We extract per_hundred for standardization
        """
        normalized = {}
        
        # Mapping of FoodRepo nutrient names to CalorieDB
        nutrient_map = {
            "energy": "energy_kj",
            "energy_kcal": "energy_kcal",
            "fat": "fat_g",
            "saturated_fatty_acids": "saturated_fat_g",
            "carbohydrates": "carbohydrates_g",
            "sugars": "sugars_g",
            "fiber": "fiber_g",
            "proteins": "protein_g",
            "salt": "salt_g",
            "sodium": "sodium_mg"
        }
        
        for foodrepo_name, caloriedb_name in nutrient_map.items():
            nutrient_data = nutrients_raw.get(foodrepo_name, {})
            
            if isinstance(nutrient_data, dict):
                value = nutrient_data.get("per_hundred", 0)
            else:
                value = 0
            
            normalized[caloriedb_name] = float(value) if value else 0.0
        
        return normalized


class CalorieDBIngestionPipeline:
    """
    Pipeline for ingesting FoodRepo data into CalorieDB
    
    Handles:
    1. Fetch from FoodRepo API
    2. Transform to CalorieDB schema
    3. Store in IPFS (content addressing)
    4. Create BigchainDB assets (immutable records)
    5. Cache locally for fast access
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.foodrepo_client = FoodRepoClient(api_key)
        self.transformer = FoodRepoToCalorieDBTransformer()
        self.ipfs = get_ipfs_client()
        self.bigchain = get_bigchaindb_client()
        
        # Setup cache directory
        self.cache_dir = Path("data/caloriedb_public")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.products_cache = self.cache_dir / "products.json"
        self.index_file = self.cache_dir / "index.json"
        
        # Load existing cache
        self.products: List[Dict[str, Any]] = []
        if self.products_cache.exists():
            try:
                self.products = json.loads(self.products_cache.read_text())
            except Exception:
                self.products = []
    
    def ingest_batch(
        self,
        batch_size: int = 1000,
        skip_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Ingest a batch of products from FoodRepo
        
        Args:
            batch_size: Number of products to ingest
            skip_existing: Skip products already in cache
            
        Returns:
            Ingestion statistics
        """
        stats = {
            "fetched": 0,
            "transformed": 0,
            "ipfs_stored": 0,
            "bigchain_stored": 0,
            "cached": 0,
            "skipped": 0,
            "errors": 0
        }
        
        # Track existing barcodes
        existing_barcodes = {p.get("barcode") for p in self.products if p.get("barcode")}
        
        print(f"Starting ingestion of {batch_size} products from FoodRepo...")
        
        for product_raw in self.foodrepo_client.iter_all_products(
            page_size=100,
            excludes=["images"],  # Exclude images for faster transfer
            max_products=batch_size
        ):
            stats["fetched"] += 1
            
            try:
                # Check if already cached
                barcode = product_raw.get("barcode", "")
                if skip_existing and barcode in existing_barcodes:
                    stats["skipped"] += 1
                    continue
                
                # Transform to CalorieDB format
                product = self.transformer.transform_product(product_raw)
                stats["transformed"] += 1
                
                # Store in IPFS (optional, if available)
                if self.ipfs.available:
                    try:
                        product_json = json.dumps(product, sort_keys=True).encode('utf-8')
                        cid = self.ipfs.add_bytes(product_json)
                        product["ipfs_cid"] = cid
                        stats["ipfs_stored"] += 1
                    except Exception as e:
                        print(f"IPFS storage failed for {barcode}: {e}")
                
                # Create BigchainDB asset (optional, if available)
                if self.bigchain.available:
                    try:
                        metadata = {
                            "type": "caloriedb_product",
                            "barcode": barcode,
                            "name": product.get("name"),
                            "source": "foodrepo",
                            "imported_at": product.get("imported_at")
                        }
                        asset_result = self.bigchain.create_asset(metadata)
                        product["bigchaindb_tx_id"] = asset_result.get("tx_id")
                        stats["bigchain_stored"] += 1
                    except Exception as e:
                        print(f"BigchainDB storage failed for {barcode}: {e}")
                
                # Add to cache
                self.products.append(product)
                existing_barcodes.add(barcode)
                stats["cached"] += 1
                
                # Save cache periodically (every 100 products)
                if stats["cached"] % 100 == 0:
                    self._save_cache()
                    print(f"Progress: {stats['cached']} products cached")
                
            except Exception as e:
                print(f"Error processing product: {e}")
                stats["errors"] += 1
        
        # Final save
        self._save_cache()
        self._update_index(stats)
        
        print(f"\nIngestion complete!")
        print(f"Fetched: {stats['fetched']}")
        print(f"Transformed: {stats['transformed']}")
        print(f"Cached: {stats['cached']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"Errors: {stats['errors']}")
        
        return stats
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get product from cache by barcode"""
        for product in self.products:
            if product.get("barcode") == barcode:
                return product
        return None
    
    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """Search products in cache"""
        query_lower = query.lower()
        results = []
        
        for product in self.products:
            name = product.get("name", "").lower()
            if query_lower in name:
                results.append(product)
        
        return results
    
    def _save_cache(self):
        """Save products cache to disk"""
        try:
            self.products_cache.write_text(
                json.dumps(self.products, ensure_ascii=False, indent=2)
            )
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _update_index(self, stats: Dict[str, Any]):
        """Update index file with metadata"""
        index_data = {
            "version": "1.0",
            "source": "foodrepo",
            "total_products": len(self.products),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "ingestion_stats": stats,
            "ipfs_available": self.ipfs.available,
            "bigchaindb_available": self.bigchain.available
        }
        
        try:
            self.index_file.write_text(
                json.dumps(index_data, ensure_ascii=False, indent=2)
            )
        except Exception as e:
            print(f"Error updating index: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        total = len(self.products)
        
        with_images = sum(1 for p in self.products if p.get("image_urls"))
        with_nutrients = sum(1 for p in self.products 
                           if p.get("nutrients", {}).get("energy_kcal", 0) > 0)
        with_ingredients = sum(1 for p in self.products if p.get("ingredients"))
        
        return {
            "total_products": total,
            "with_images": with_images,
            "with_nutrients": with_nutrients,
            "with_ingredients": with_ingredients,
            "cache_file": str(self.products_cache),
            "cache_size_mb": self.products_cache.stat().st_size / (1024 * 1024) 
                            if self.products_cache.exists() else 0
        }
    
    def close(self):
        """Cleanup resources"""
        self.foodrepo_client.close()


# Convenience functions
def ingest_foodrepo_data(batch_size: int = 1000, api_key: Optional[str] = None):
    """
    Convenience function to ingest FoodRepo data
    
    Usage:
        from src.utils.foodrepo_integration import ingest_foodrepo_data
        stats = ingest_foodrepo_data(batch_size=1000)
    """
    pipeline = CalorieDBIngestionPipeline(api_key)
    try:
        return pipeline.ingest_batch(batch_size)
    finally:
        pipeline.close()


def search_foodrepo_product(query: str, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search for products in local cache
    
    Usage:
        from src.utils.foodrepo_integration import search_foodrepo_product
        results = search_foodrepo_product("chocolate")
    """
    pipeline = CalorieDBIngestionPipeline(api_key)
    try:
        return pipeline.search_products(query)
    finally:
        pipeline.close()


__all__ = [
    "FoodRepoClient",
    "FoodRepoToCalorieDBTransformer",
    "CalorieDBIngestionPipeline",
    "ingest_foodrepo_data",
    "search_foodrepo_product"
]
