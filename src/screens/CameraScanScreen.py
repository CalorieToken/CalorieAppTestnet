from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock

from src.utils.foodrepo_client import FoodRepoClient
from src.utils.caloriedb import record_scan

try:
    from kivy_garden.zbarcam import ZBarCam  # type: ignore
    from pyzbar.pyzbar import ZBarSymbol  # optional, depends on distro
    HAS_CAMERA = True
except Exception:
    ZBarCam = None  # type: ignore
    HAS_CAMERA = False


class CameraScanScreen(Screen):
    last_barcode = StringProperty("")
    result_text = StringProperty("")
    product = ObjectProperty(allownone=True)

    def on_pre_enter(self, *args):
        self.result_text = ""
        self.last_barcode = ""
        self.product = None
        container = self.ids.get("camera_container")
        if container:
            container.clear_widgets()
        if HAS_CAMERA and ZBarCam is not None and container:
            try:
                cam = ZBarCam()
                cam.bind(symbols=self._on_symbols)
                container.add_widget(cam)
                self._set_status("Camera ready. Point at a barcode.")
            except Exception:
                self._set_status("Camera init failed. See docs for setup.")
        else:
            self._set_status("Camera scanner unavailable. See FOODREPO_INTEGRATION.md for setup.")

    def _on_symbols(self, instance, symbols):
        if not symbols:
            return
        # Take first detected symbol
        try:
            data = symbols[0].data.decode("utf-8")
        except Exception:
            data = str(symbols[0].data)
        if data and data != self.last_barcode:
            self.last_barcode = data
            self._lookup_and_show(data)

    def _lookup_and_show(self, barcode: str):
        client = FoodRepoClient()
        prod = client.get_by_barcode(barcode)
        self.product = prod
        if prod:
            name = prod.get("name") or prod.get("product_name") or "Unknown"
            brand = prod.get("brand") or prod.get("brands") or ""
            self._set_status(f"Found: {name} {('('+brand+')') if brand else ''} | {barcode}")
        else:
            self._set_status(f"No product for {barcode}")

    def record_to_caloriedb(self):
        if not self.product or not self.last_barcode:
            self._set_status("Scan a product first.")
            return
        entry = record_scan(self.product, self.last_barcode)
        cid = entry.get("ipfs_cid")
        tx = entry.get("bigchaindb_tx_id")
        self._set_status(f"Recorded pilot scan. CID={cid or 'n/a'} TX={tx or 'n/a'}")

    def _set_status(self, msg: str):
        self.result_text = msg
        lbl = self.ids.get("result_label")
        if lbl:
            lbl.text = msg
