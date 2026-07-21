document.addEventListener("DOMContentLoaded", () => {
    // 1. Inisialisasi Peta
    const mapElement = document.getElementById('peta-desa');
    const poiLog = document.getElementById('poi-log');
    
    if (!mapElement) return;

    // Ambil data POI dari backend API Flask
    fetch('/api/poi')
        .then(response => response.json())
        .then(data => {
            // Setup peta Leaflet berdasarkan data desa
            const map = L.map('peta-desa').setView(
                [data.pusat.lat, data.pusat.lng], 
                data.pusat.zoom
            );

            // Gunakan CartoDB Dark Matter tile layer agar estetik dan cocok dengan tema gelap
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
                subdomains: 'abcd',
                maxZoom: 20
            }).addTo(map);

            // CEGAH ERROR: Hanya ubah tulisan jika elemennya ada
            if (poiLog) {
                poiLog.innerHTML = ''; 
            }

            // 2. Bangun Legenda Kategori
            const legenda = document.getElementById('legenda-kategori');
            if (legenda) {
                const kategoriUnik = [...new Map(
                    data.titik.map(poi => [poi.kategori, poi.warna])
                ).entries()];

                legenda.innerHTML = kategoriUnik
                    .map(([kategori, warna]) => `
                        <li class="legend-item">
                            <span class="legend-dot" style="background-color: ${warna};"></span>
                            <span class="legend-label">${kategori}</span>
                        </li>
                    `)
                    .join('');
            }

            // 3. Render Marker & Daftar Log POI
            data.titik.forEach(poi => {
                // Buat Marker HTML Custom 
                const customIcon = L.divIcon({
                    className: 'custom-pin',
                    html: `<div style="background-color: ${poi.warna}; width: 15px; height: 15px; border-radius: 50%; border: 2px solid #e8e2cd; box-shadow: 0 0 10px rgba(0,0,0,0.5);"></div>`,
                    iconSize: [15, 15],
                    iconAnchor: [7.5, 7.5]
                });

                L.marker([poi.lat, poi.lng], { icon: customIcon })
                    .addTo(map)
                    .bindPopup(`<strong>${poi.nama}</strong><br><small>${poi.kategori}</small>`);

                // 3. Tambahkan ke HTML Listing HANYA JIKA ADA
                if (poiLog) {
                    const poiHTML = `
                        <div class="poi-row">
                            <div class="poi-header">
                                <span class="poi-tag" style="background-color: ${poi.warna}20; color: ${poi.warna}; border: 1px solid ${poi.warna}">${poi.kategori}</span>
                                <h3>${poi.nama}</h3>
                            </div>
                            <p style="color: var(--muted-sage);">${poi.deskripsi}</p>
                            <div class="mono" style="font-size: 0.8rem; margin-top: 0.5rem;">[ ${poi.lat}, ${poi.lng} ]</div>
                        </div>
                    `;
                    poiLog.innerHTML += poiHTML;
                }
            });
        })
        .catch(error => {
            console.error('Error memuat data peta:', error);
            if (poiLog) {
                poiLog.innerHTML = '<p>Gagal memuat data dari server.</p>';
            }
        });
});