import { defineStore } from 'pinia';

interface LayerItem {
  id?: number;
  name: string;
  data: any;
  visible: boolean;
//   type?: 'Point' | 'LineString' | 'Polygon'; // Tambahkan tipe ini
}

export const useLayerStore = defineStore('layers', {
  state: () => ({
    // Menyimpan daftar layer GeoJSON yang sudah dimuat
    loadedLayers: [] as LayerItem[],
    groups: {
      Point: { visible: false, features: [] },
      LineString: { visible: false, features: [] },
      Polygon: { visible: false, features: [] }
    } as Record<string, { visible: boolean, features: any[] }>,
    activeLeafletLayers: new Map<string, L.Layer>(),
  }),
  actions: {

    addLayer(layerData: { name: string, data: any }) {
      this.loadedLayers.push({
        id: Date.now(),
        ...layerData,
        visible: false
      });
    },

    addDigitizedFeature(type: string, geoJsonData: any) {
      if (this.groups[type]) {
        // this.groups[type].features.push(geoJsonData);
        this.groups[type].features = [...this.groups[type].features, geoJsonData];
      }
    },

    setActiveLayer(key: string, layer: L.Layer) {
      this.activeLeafletLayers.set(key, layer);
    },

    removeActiveLayer(key: string) {
      this.activeLeafletLayers.delete(key);
    },

    clearAll() {
      // 1. Reset array/object ke kondisi awal
      this.loadedLayers = [];
      Object.keys(this.groups).forEach(key => {
        this.groups[key].features = [];
        this.groups[key].visible = false;
      });
      
      // 2. Bersihkan referensi layer
      this.activeLeafletLayers.clear();
      
      console.log("Store telah dibersihkan.");
    },

    getAllDigitizedFeatures() {
    let allFeatures: any[] = [];
    Object.values(this.groups).forEach(group => {
      allFeatures = [...allFeatures, ...group.features];
    });
    
    return {
      type: "FeatureCollection",
      features: allFeatures
    };
  }

  }
});