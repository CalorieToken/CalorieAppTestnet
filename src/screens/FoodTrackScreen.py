from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock

from src.utils.foodrepo_client import FoodRepoClient

# CalorieDB prototype deferred behind feature flag
from src.core.feature_flags import ENABLE_CALORIE_DB
try:  # Safe guarded import of deferred module
    if ENABLE_CALORIE_DB:
        from src._deferred.caloriedb import record_scan  # type: ignore
    else:
        record_scan = None  # type: ignore
except Exception:
    record_scan = None  # type: ignore

try:
    from kivy_garden.zbarcam import ZBarCam
    HAS_CAMERA = True
except Exception:
    ZBarCam = None
    HAS_CAMERA = False


class FoodTrackScreen(Screen):
    current_tab = StringProperty("manual")
    result_text = StringProperty("No product selected")
    product_found = BooleanProperty(False)
    product = ObjectProperty(allownone=True)
    last_barcode = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.foodrepo_client = FoodRepoClient()

    def on_pre_enter(self, *args):
        """Reset screen state when entering"""
        self.clear_results()
        self.switch_tab("manual")

    def switch_tab(self, tab_name: str):
        """Switch between manual, barcode, and camera tabs"""
        self.current_tab = tab_name
        
        # Initialize camera if switching to camera tab
        if tab_name == "camera" and HAS_CAMERA:
            Clock.schedule_once(self._init_camera, 0.1)

    def _init_camera(self, dt):
        """Initialize camera for barcode scanning"""
        container = self.ids.get("camera_container")
        if not container:
            return
            
        container.clear_widgets()
        
        if ZBarCam is None:
            self.result_text = "Camera scanner unavailable. Install zbarcam package."
            return
            
        try:
            cam = ZBarCam()
            cam.bind(symbols=self._on_camera_symbols)
            container.add_widget(cam)
            self.result_text = "Camera ready. Point at a barcode."
        except Exception as e:
            self.result_text = f"Camera init failed: {str(e)}"

    def _on_camera_symbols(self, instance, symbols):
        """Handle barcode detection from camera"""
        if not symbols:
            return
            
        try:
            data = symbols[0].data.decode("utf-8")
        except Exception:
            data = str(symbols[0].data)
            
        if data and data != self.last_barcode:
            self.last_barcode = data
            self._lookup_and_display(data)

    def on_search_text(self, text: str):
        """Handle manual food search (debounced)"""
        # TODO: Implement food database search
        if len(text) >= 3:
            self.result_text = f"Searching for '{text}'... (Feature coming soon)"
        else:
            self.result_text = "Type at least 3 characters to search"

    def lookup_barcode(self):
        """Lookup product by barcode"""
        field = self.ids.get("barcode_input")
        if not field:
            return
            
        barcode = field.text.strip()
        if not barcode:
            self.result_text = "Enter a barcode to lookup"
            self.product_found = False
            return
            
        self.last_barcode = barcode
        self._lookup_and_display(barcode)

    def _lookup_and_display(self, barcode: str):
        """Perform barcode lookup and display results"""
        prod = self.foodrepo_client.get_by_barcode(barcode)
        self.product = prod
        
        if prod:
            self.product_found = True
            name = prod.get("name") or prod.get("product_name") or "Unknown"
            brand = prod.get("brand") or prod.get("brands") or ""
            
            # Build result text
            result = f"✓ Found: {name}"
            if brand:
                result += f"\nBrand: {brand}"
            result += f"\nBarcode: {barcode}"
            
            self.result_text = result
            
            # Display nutrition info if available
            nutrition_label = self.ids.get("nutrition_info")
            if nutrition_label:
                nutrition = self._format_nutrition(prod)
                nutrition_label.text = nutrition
        else:
            self.product_found = False
            self.result_text = f"✗ No product found for barcode: {barcode}"
            nutrition_label = self.ids.get("nutrition_info")
            if nutrition_label:
                nutrition_label.text = ""

    def _format_nutrition(self, product: dict) -> str:
        """Format nutrition information for display"""
        lines = []
        
        # Look for common nutrition keys
        calories = (product.get("calories") or 
                   product.get("energy_kcal_100g") or 
                   product.get("energy-kcal_100g"))
        if calories:
            lines.append(f"Calories: {calories} kcal")
        
        protein = product.get("proteins_100g") or product.get("protein")
        if protein:
            lines.append(f"Protein: {protein}g")
        
        carbs = product.get("carbohydrates_100g") or product.get("carbs")
        if carbs:
            lines.append(f"Carbs: {carbs}g")
        
        fat = product.get("fat_100g") or product.get("fat")
        if fat:
            lines.append(f"Fat: {fat}g")
        
        return "\n".join(lines) if lines else "Nutrition info not available"

    def record_to_caloriedb(self):
        """Attempt to record food scan to CalorieDB if feature enabled."""
        if not ENABLE_CALORIE_DB or record_scan is None:
            self.result_text = "CalorieDB feature deferred (disabled)."
            return
        if not self.product or not self.last_barcode:
            self.result_text = "Lookup a product first"
            return
        try:
            entry = record_scan(self.product, self.last_barcode)  # type: ignore[arg-type]
            cid = entry.get("ipfs_cid")
            tx = entry.get("bigchaindb_tx_id")
            self.result_text = f"✓ Recorded to CalorieDB\nCID: {cid or 'n/a'}\nTX: {tx or 'n/a'}"
        except Exception as e:
            self.result_text = f"✗ Failed to record: {str(e)}"

    def clear_results(self):
        """Clear all results and reset form"""
        self.result_text = "No product selected"
        self.product_found = False
        self.product = None
        self.last_barcode = ""
        
        # Clear input fields
        barcode_input = self.ids.get("barcode_input")
        if barcode_input:
            barcode_input.text = ""
            
        search_input = self.ids.get("food_search_input")
        if search_input:
            search_input.text = ""
            
        nutrition_label = self.ids.get("nutrition_info")
        if nutrition_label:
            nutrition_label.text = ""
