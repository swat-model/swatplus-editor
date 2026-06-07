<template>
  <v-layout class="fill-height">
    <v-navigation-drawer v-model="drawer" location="right" permanent width="375">
      <v-list-item title="Layer Control"></v-list-item>
      <v-divider></v-divider>
      <v-list density="compact" nav>
        <v-list-item v-for="item in layerStore.loadedLayers" :key="item.id">
          <v-checkbox v-model="item.visible" :label="item.name" @update:model-value="toggleAny(item, false)"></v-checkbox>
        </v-list-item>
        <v-divider></v-divider>

        <v-list-item v-for="(group, type) in layerStore.groups" :key="type">
          <v-checkbox 
            v-model="group.visible" 
            :label="type + ' (' + group.features.length + ')'"
            @update:model-value="toggleAny(type, true)"
          ></v-checkbox>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main class="pa-0">
      <div class="map-wrapper">
        <div ref="mapContainer" class="map-container"></div>
        
        <v-btn class="load-btn" color="primary" @click="loadAllGeoJsons" :disabled="!currentProject.projectPath || isDataLoaded">
          Load GeoJSON
        </v-btn>
        <v-btn class="load-btn2" color="primary" @click="loadAllGeoJsons" :disabled="!currentProject.projectPath || isDataLoaded">
          Load Result
        </v-btn>
        <v-btn class="save-btn" color="success"  @click="saveDigitizedData" :disabled="!currentProject.projectPath">
          Save Digitasi
        </v-btn>
      </div>
    </v-main>
  </v-layout>
</template>

<script setup lang="ts">
  import { useRouter } from 'vue-router';
  import { onUnmounted, onMounted, ref, nextTick, shallowRef, computed } from 'vue';
  import { useHelpers } from '@/helpers';
  import { useLayerStore } from '@/store/layers';

  // Import Leaflet dan plugin yang diperlukan
  import L from 'leaflet';
  import 'leaflet/dist/leaflet.css';
  import 'leaflet-draw';
  import 'leaflet-draw/dist/leaflet.draw.css';

  // bagian deklarasi dan setup
  const router = useRouter();
  const { utilities, currentProject } = useHelpers();

  const layerStore = useLayerStore();
  const drawer = ref(true);
  const mapContainer = ref<HTMLElement | null>(null);
  const map = shallowRef<L.Map | null>(null);
  // const layers = computed(() => layerStore.loadedLayers);

  const activeLeafletLayers = new Map<string, L.GeoJSON>();
  const isDataLoaded = computed(() => {
    return layerStore.loadedLayers.length > 0;
  });

    const toggleAny = (itemOrType: any, isGroup: boolean) => {
    if (isGroup) {
      toggleGroup(itemOrType); // Panggil fungsi digitasi
    } else {
      toggleLayer(itemOrType); // Panggil fungsi load file
    }
  };

  const toggleGroup = (type: string) => {
    const group = layerStore.groups[type];
    
    if (group.visible) {
      // 1. Jika sudah ada di peta, hapus dulu agar tidak duplikat (atau return)
      if (activeLeafletLayers.has(type)) {
        map.value!.removeLayer(activeLeafletLayers.get(type)!);
      }

      // 2. Buat objek layer baru dari kumpulan fitur
      const layer = L.geoJSON(group.features, {
        style: { 
          color: type === 'Polygon' ? '#4CAF50' : type === 'LineString' ? '#F44336' : '#2196F3', 
          weight: 3, 
          fillOpacity: 0.5 
        }
      });

      // 3. Tambahkan ke peta
      layer.addTo(map.value!);
      activeLeafletLayers.set(type, layer);

      // 4. Zoom ke layer digitasi (opsional, agar user tahu gambarnya di mana)
      const bounds = layer.getBounds();
      if (bounds.isValid()) {
        map.value!.fitBounds(bounds, { padding: [50, 50] });
      }
      } else {
        // 5. Hapus dari peta
        const layer = activeLeafletLayers.get(type);
        if (layer) {
          map.value!.removeLayer(layer);
          activeLeafletLayers.delete(type);
        }
      }
  };

  const toggleLayer = async (item: any) => {
    
    if (!map.value) await nextTick();
    if (!map.value) return;

    // 1. Cek apakah layer sudah aktif, jika ya, hentikan agar tidak duplikat
    if (item.visible && activeLeafletLayers.has(item.name)) return;

    if (item.visible) {
      const layer = L.geoJSON(item.data, {
        style: { color: "#1976D2", weight: 3, fillOpacity: 0.5 },
        // Gunakan onEachFeature saja untuk mengikat popup & event
        onEachFeature: (feature, layer) => {
          const props = feature.properties;
          if (props) {
            // Susun HTML Tabel
            const tableRows = Object.entries(props)
              .map(([key, val]) => `<tr><th>${key}</th><td>${val}</td></tr>`)
              .join('');

            const content = `
              <div class="popup-header">Detail Informasi</div>
              <table class="popup-table">
                <tbody>${tableRows}</tbody>
              </table>
            `;

            layer.bindPopup(content, {
              // maxWidth: 300,
              // minWidth: 250,
              className: 'custom-popup'
            });
          }

          // Event Hover
          layer.on('mouseover', () => {
            (layer as L.Path).setStyle({ color: '#FF9800', weight: 4, fillOpacity: 0.7 });
          });
          layer.on('mouseout', () => {
            // Reset style ke default
            (layer as L.Path).setStyle({ color: "#1976D2", weight: 3, fillOpacity: 0.5 });
          });
        }
      });

      // Tambahkan ke peta
      layer.addTo(map.value);
      activeLeafletLayers.set(item.name, layer);

      // Zoom ke data
      await nextTick();
      try {
        const bounds = layer.getBounds();
        if (bounds.isValid()) {
          map.value.fitBounds(bounds, { padding: [50, 50], animate: true });
        }
      } catch (e) {
        console.warn("Bounds tidak valid, skip zoom.");
      }
    } else {
      // Hapus layer
      const layer = activeLeafletLayers.get(item.name);
      if (layer) {
        map.value.removeLayer(layer);
        activeLeafletLayers.delete(item.name);
      }
    }
  };

  const saveDigitizedData = async () => {
    const geojsonData = layerStore.getAllDigitizedFeatures();
    
    if (geojsonData.features.length === 0) {
      console.warn("Save dibatalkan: Data digitasi kosong."); // Log jika data tidak ada
      alert("Tidak ada data digitasi untuk disimpan!");
      return;
    }

    // Gunakan electronApi untuk membuka dialog simpan
    const options = {
      title: 'Simpan Data Digitasi',
      defaultPath: utilities.joinPaths([currentProject.projectPath, 'geojson_data', 'digitasi_hasil.geojson']),
      filters: [{ name: 'GeoJSON', extensions: ['geojson'] }]
    };

    // console.log("Membuka dialog simpan dengan opsi:", options);

    const filePath = await (window.electronApi as any).saveFileDialog(options);
    console.log("Path file yang dipilih:", filePath);

    if (filePath) {
      try {
        // Menggunakan fs (pastikan Anda punya akses atau buat wrapper di preload)
        // console.log("Sedang menulis data ke:", filePath);
        const result = await (window.electronApi as any).saveFile(filePath, JSON.stringify(geojsonData, null, 2));
        // console.log("Hasil simpan:", result);
        alert("Data berhasil disimpan!");
        
      } catch (e) {
        console.error("Gagal menyimpan file:", e);
        alert("Terjadi kesalahan saat menyimpan.");
      }
    }
  };

  onMounted(async() => {
    await nextTick();
    activeLeafletLayers.clear();
    if (mapContainer.value) {
      const mapInstance = L.map(mapContainer.value).setView([-0.95, 100.35], 8);

      const googleSat = L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
      maxZoom: 20,
      subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
      });

      // Tambahkan ke peta
      googleSat.addTo(mapInstance);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        opacity: 0.4
      }).addTo(mapInstance);
      map.value = mapInstance;

      //Panggil fungsi inisialisasi fitur menggambar setelah peta dibuat
      initDrawing(mapInstance);

      // Tambahkan kontrol skala di map
      L.control.scale({
        metric: true,    // Menampilkan satuan meter/km
        imperial: false, // Menyembunyikan satuan miles (opsional)
        position: 'bottomleft', // Posisi skala di pojok kiri bawah
        updateWhenIdle: false
      }).addTo(mapInstance);
    
    }
  }); 



  // Fungsi untuk inisialisasi fitur menggambar
  function initDrawing(map: L.Map) {
    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    const drawControl = new (L as any).Control.Draw({
      edit: { featureGroup: drawnItems },
      draw: { polygon: true, polyline: true, rectangle: false, circle: false, marker: true }
    });
    map.addControl(drawControl);

    // Fungsi pembantu untuk menghitung & memperbarui teks
    const updateTooltip = (layer: any) => {
      let content = "";
      if (layer instanceof L.Polygon || layer instanceof L.Rectangle) {
        const area = (L as any).GeometryUtil.geodesicArea(layer.getLatLngs()[0]);
        content = `Luas: ${(area / 1000000).toFixed(2)} km²`;
      } else if (layer instanceof L.Polyline) {
        const latlngs = layer.getLatLngs() as L.LatLng[];
        let distance = 0;
        for (let i = 0; i < latlngs.length - 1; i++) {
          distance += latlngs[i].distanceTo(latlngs[i + 1]);
        }
        content = `Panjang: ${(distance / 1000).toFixed(2)} km`;
      }
      
      // Update tooltip yang sudah ada atau buat baru
      if (layer.getTooltip()) {
        layer.setTooltipContent(content);
      } else {
        layer.bindTooltip(content, { permanent: false, direction: 'center' });
      }
    };

      // Saat pertama kali dibuat
    map.on((L as any).Draw.Event.CREATED, (e: any) => {
      const layer = e.layer;
      const geoJsonData = layer.toGeoJSON();
      const type = geoJsonData.geometry.type; // 'Point', 'LineString', atau 'Polygon'
      
      // Masukkan ke grup
      layerStore.addDigitizedFeature(type, geoJsonData);
      
      // Update UI peta
      drawnItems.addLayer(layer);
      updateTooltip(layer);
    });

      // Saat diedit
    map.on('draw:edited', (e: any) => {
      e.layers.eachLayer((layer: any) => {
        updateTooltip(layer);
        // Opsional: Di sini Anda bisa menambahkan logika untuk 
        // mengupdate data di store jika layer diubah ukurannya
      });
    });
  }

  // Fungsi untuk memuat semua file GeoJSON dari folder proyek
  async function loadAllGeoJsons() {
    // ... proses read file ...
    if (!currentProject.projectPath) {
      console.error("Path proyek tidak ditemukan!");
      return;
    }
    const geojsonFolder = utilities.joinPaths([currentProject.projectPath, 'geojson_data']);
    
    // 2. Cek apakah folder benar-benar ada
    const folderExists = window.electronApi.pathExists(geojsonFolder);
    if (!folderExists) {
      console.warn("Folder GeoJSON tidak ditemukan di:", geojsonFolder);
      return;
    }

    // 3. Baca isi direktori
    // Catatan: Karena di preload.ts 'readDirectory' tidak ada secara eksplisit, 
    // pastikan Anda menggunakan metode yang benar (saya asumsikan Anda punya akses fs)
    const files = await (window.electronApi as any).readDirectory(geojsonFolder);
    const geojsonFiles = files.filter((f: string) => f.endsWith('.geojson'));

    for (const file of geojsonFiles) {
      const filePath = utilities.joinPaths([geojsonFolder, file]);
      console.log("Mencoba membaca file di:", filePath);
      
      try {
        // 4. Baca isi file (menggunakan metode yang tersedia di preload.ts)
        const content = await (window.electronApi as any).readFile(filePath);
        
        if (!content) {
          console.warn(`File kosong atau gagal dibaca: ${file}`);
          continue;
        }

        const jsonData = JSON.parse(content);
        
        // Simpan ke Store
        layerStore.addLayer({ name: file, data: jsonData });
        console.log(`Berhasil memuat: ${file}`);
        
      } catch (e) {
        console.error(`Gagal parsing file ${file}:`, e);
      }
    }
  }

</script>

<style scoped>
  /* Pastikan container router-view kita juga punya tinggi */
  .map-wrapper {
      flex: 1;
      display: flex;
      flex-direction: column;
      width: 100%;
      height: 100%;
      /* margin: 0 !important; */
      /* padding : 0 !important; */
      /* position: relative; */
      overflow: hidden;
  }

  .map-container {
      flex: 1;
      width: 100%;
      /* margin: 0 !important; */
      /* padding : 0 !important; */
      min-height: 1; /* Mencegah overflow */
      z-index: 0; /* Peta harus di bawah tombol */
  }

  .load-btn {
    position: absolute;
    top: 10px; /* Jarak dari atas map-wrapper */
    left: 60px; 
    z-index: 1000; /* Pastikan di atas layer peta */
  }
  .load-btn2 {
    position: absolute;
    top: 10px; /* Jarak dari atas map-wrapper */
    left: 220px; 
    z-index: 1000; /* Pastikan di atas layer peta */
  }
  .save-btn {
    position: absolute;
    top: 10px;
    left: 360px; /* Atur posisi sesuai layout Anda */
    z-index: 1000;
  }

  /* Merapatkan container list */
  .v-list {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
  }

  /* Menghilangkan padding default v-list-item */
  .v-list-item {
    min-height: 30px !important; /* Sesuaikan tinggi item */
    padding-top: 0 !important;
    padding-bottom: 0 !important;
  }

  /* Mengatur margin checkbox agar tidak terlalu banyak ruang */
  .v-list-item .v-checkbox {
    margin: 0 !important;
    padding: 0 !important;
    min-height: 24px !important;
  }

  .v-input__details {
    display: none !important;
  }

  /* 1. Wrapper Utama Popup */
  :deep(.leaflet-popup-content-wrapper) {
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    padding: 0 !important;
    overflow: hidden;
  }

  :deep(.leaflet-popup-content) {
    margin: 0 !important;
    width: 320px !important; /* Lebarkan total popup agar kolom lebih lega */
  }

  /* 2. Judul Popup */
  .popup-header {
    background-color: #1976d2;
    color: white;
    padding: 8px 12px;
    font-weight: bold;
    font-size: 14px;
  }

  /* 3. Pengaturan Tabel dengan Garis */
  .popup-table {
    width: 100%;
    border-collapse: collapse; /* Penting agar garis menyatu */
    table-layout: fixed;       /* Memaksa pembagian lebar kolom */
    font-size: 12px;
  }

  .popup-table th, .popup-table td {
    border: 1px solid #ddd;    /* Memberikan garis di semua sisi */
    padding: 8px;
    text-align: left;
  }

  /* 4. Kolom 1 (Atribut) - Lebarkan di sini */
  .popup-table th {
    width: 45%;                /* Persentase lebar kolom 1 */
    background-color: #f4f4f4;
    color: #333;
    font-weight: 600;
  }

  /* 5. Kolom 2 (Isian) */
  .popup-table td {
    width: 55%;
    color: #555;
    word-wrap: break-word;
  }
</style>