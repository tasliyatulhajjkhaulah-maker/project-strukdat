import os
from frontend.ui import jalankan
 
BASE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(BASE, "data", "pesanan.csv")
 
if __name__ == "__main__":
    jalankan(CSV)