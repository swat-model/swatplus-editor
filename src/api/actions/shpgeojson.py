
import geopandas as gpd
import sys
import os
import json
import warnings
import traceback

warnings.filterwarnings("ignore", category=UserWarning, module='pyogrio')

# Tambahkan ini

# Pastikan path helper benar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    # print("DEBUG: Skrip Python berhasil dimulai!")
    from helpers.executable_api import ExecutableApi
    
    # Debug argumen yang diterima
    # print(f"DEBUG: Argumen yang diterima: {sys.argv}")
    sys.stdout.flush()

    # ... sisa logika skrip Anda ...

except Exception:
    # Jika ada error, cetak detailnya ke terminal Electron
    # print("DEBUG: TERJADI ERROR PADA SKRIP!")
    traceback.print_exc()
    sys.stdout.flush()

class BulkConverter(ExecutableApi):
    def run(self, shapes_dir, output_dir):
        files = [f for f in os.listdir(shapes_dir) if f.lower().endswith('.shp')]
        total_files = len(files)
        
        if total_files == 0:
            return "Info: Tidak ada file SHP ditemukan."

        os.makedirs(output_dir, exist_ok=True)

        for index, filename in enumerate(files):
            # Hitung progress persentase
            percent = int(((index) / total_files) * 100)
            self.emit_progress(percent, f"Mengonversi {filename} ({index + 1}/{total_files})...")
            
            # Logika konversi Anda
            try:
                shp_path = os.path.join(shapes_dir, filename)
                json_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.geojson')
                os.environ["SHAPE_RESTORE_SHX"] = "YES"
                
                gdf = gpd.read_file(shp_path, engine='pyogrio')
                if gdf.crs is None:
                    print(f"Info: {filename} tidak memiliki CRS. Menyimpan tanpa konversi.")
                    # gdf.set_crs(epsg=4326, inplace=True)
                else:
                    if gdf.crs != "EPSG:4326":
                        gdf = gdf.to_crs(epsg=4326)
                gdf.to_file(json_path, driver='GeoJSON', engine='pyogrio')
            except Exception as e:
                print(f"Gagal memproses {filename}: {str(e)}")

        self.emit_progress(100, "Konversi selesai!")
        return "Selesai"

def sync_geojson(shapefile_path, geojson_path):
    """
    Logika sinkronisasi file SHP ke GeoJSON.
    
    """
    # target_dir = os.path.dirname(geojson_path)
    
    # if not os.path.exists(target_dir):
    #     # print(f"DEBUG: Folder belum ada, mencoba membuat: {target_dir}")
    #     try:
    #         os.makedirs(target_dir) # Membuat folder secara otomatis
    #         # print(f"Folder berhasil dibuat: {target_dir}")
    #     except Exception as e:
    #         print(f"Gagal membuat folder: {e}")
    #         return
        
    # if not os.path.exists(shapefile_path):
    #     print(f"Error: File {shapefile_path} tidak ditemukan.")
    #     return
    
    try:
        # Memastikan direktori target ada
        os.makedirs(os.path.dirname(geojson_path), exist_ok=True)
        
        # Baca SHP
        gdf = gpd.read_file(shapefile_path, engine='pyogrio')
        
        # Cek apakah sistem koordinat (CRS) tersedia
        if gdf.crs is None:
            print(f"Warning: File {shapefile_path} tidak memiliki informasi CRS. Asumsi WGS84.")
        else:
            # Jika CRS tidak sama dengan EPSG:4326, lakukan konversi (reproject)
            if gdf.crs != "EPSG:4326":
                print(f"Konversi koordinat dari {gdf.crs} ke EPSG:4326...")
                gdf = gdf.to_crs(epsg=4326)
        
        # Tulis ke GeoJSON
        gdf.to_file(geojson_path, driver='GeoJSON', engine='pyogrio')
        
        return f"Berhasil: {geojson_path} diperbarui."
    except Exception as e:
        return f"Error saat sinkronisasi: {str(e)}"
    
def bulk_sync_geojson(shapes_dir, output_dir):
    converter = BulkConverter()
    return converter.run(shapes_dir, output_dir)

def emit_progress(self, percent, message):
    data = {"percent": percent, "message": message}
    # Tambahkan '\n' agar Electron bisa membedakan setiap pesan JSON
    print(json.dumps(data)) 
    sys.stdout.flush()

# Tambahkan ini di baris paling akhir file shpgeojson.py
if __name__ == "__main__":
    if len(sys.argv) > 3:
        action = sys.argv[1]
        shapes_dir = sys.argv[2].split('=')[1]
        output_dir = sys.argv[3].split('=')[1]
        
        if action == 'bulk_sync_geojson':
            # print(f"DEBUG: Menjalankan bulk_sync_geojson dengan dir: {shapes_dir}")
            sys.stdout.flush()
            
            result = bulk_sync_geojson(shapes_dir, output_dir)
            
            # print(f"DEBUG: Hasil eksekusi: {result}")
            sys.stdout.flush()
    else:
        # print("DEBUG: Argumen kurang lengkap!")
        sys.stdout.flush()