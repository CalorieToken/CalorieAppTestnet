from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty

from src.utils.foodrepo_client import FoodRepoClient
from src.utils.caloriedb import record_scan


class BarcodeScanScreen(Screen):
    product = ObjectProperty(allownone=True)
    result_text = StringProperty("")

    def on_pre_enter(self, *args):
        self.ids.get("barcode_input").text = ""
        self.product = None
        self.result_text = ""

    def lookup_barcode(self):
        field = self.ids.get("barcode_input")
        barcode = field.text.strip() if field else ""
        if not barcode:
            self._set_status("Enter a barcode to lookup.")
            return
        client = FoodRepoClient()
        prod = client.get_by_barcode(barcode)
        self.product = prod
        if prod:
            name = prod.get("name") or prod.get("product_name") or "Unknown"
            brand = prod.get("brand") or prod.get("brands") or ""
            self._set_status(f"Found: {name} {('('+brand+')') if brand else ''}")
        else:
            self._set_status("No product found for this barcode.")

    def record_to_caloriedb(self):
        if not self.product:
            self._set_status("Lookup a product first.")
            return
        barcode = self.ids.get("barcode_input").text.strip()
        entry = record_scan(self.product, barcode)
        cid = entry.get("ipfs_cid")
        tx = entry.get("bigchaindb_tx_id")
        self._set_status(f"Recorded pilot scan. CID={cid or 'n/a'} TX={tx or 'n/a'}")

    def _set_status(self, msg: str):
        self.result_text = msg
        lbl = self.ids.get("result_label")
        if lbl:
            lbl.text = msg
