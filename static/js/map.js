document.addEventListener("DOMContentLoaded", function () {
    const mapElement = document.getElementById("peta-desa");
    const legendElement = document.getElementById("legenda-kategori");
    const resetButton = document.getElementById("map-reset-button");

    if (!mapElement || typeof L === "undefined") {
        return;
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    fetch("/api/poi")
        .then(function (response) {
            if (!response.ok) {
                throw new Error("Data titik peta tidak dapat dimuat.");
            }

            return response.json();
        })
        .then(function (data) {
            const centerLat = Number(data.pusat.lat);
            const centerLng = Number(data.pusat.lng);
            const centerZoom = Number(data.pusat.zoom) || 15;

            const centerPosition = [centerLat, centerLng];

            const map = L.map(mapElement, {
                scrollWheelZoom: false,
                zoomControl: true,
            }).setView(centerPosition, centerZoom);

            /*
             * OpenStreetMap standar digunakan agar jalan,
             * nama wilayah, dan fasilitas lebih mudah dibaca.
             */
            L.tileLayer(
                "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                {
                    maxZoom: 19,
                    attribution:
                        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
                }
            ).addTo(map);

            L.control.scale({
                imperial: false,
                position: "bottomleft",
            }).addTo(map);

            const markers = [];

            data.titik.forEach(function (poi) {
                const lat = Number(poi.lat);
                const lng = Number(poi.lng);

                if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
                    return;
                }

                const markerIcon = L.divIcon({
                    className: "map-pin-wrapper",
                    html: `
                        <span
                            class="map-pin"
                            style="--marker-color: ${escapeHtml(poi.warna)}"
                            aria-hidden="true"
                        ></span>
                    `,
                    iconSize: [26, 26],
                    iconAnchor: [13, 13],
                    popupAnchor: [0, -16],
                });

                const marker = L.marker([lat, lng], {
                    icon: markerIcon,
                    title: poi.nama,
                });

                marker.bindPopup(`
                    <article class="map-popup">
                        <span class="map-popup-category">
                            ${escapeHtml(poi.kategori)}
                        </span>

                        <strong class="map-popup-title">
                            ${escapeHtml(poi.nama)}
                        </strong>

                        <p class="map-popup-description">
                            ${escapeHtml(poi.deskripsi)}
                        </p>
                    </article>
                `);

                marker.addTo(map);
                markers.push(marker);
            });

            /*
             * Menyesuaikan tampilan supaya semua marker terlihat,
             * tetapi tidak melakukan zoom terlalu dekat.
             */
            if (markers.length > 0) {
                const markerGroup = L.featureGroup(markers);

                map.fitBounds(markerGroup.getBounds(), {
                    padding: [45, 45],
                    maxZoom: 16,
                });
            }

            if (legendElement) {
                const uniqueCategories = [
                    ...new Map(
                        data.titik.map(function (poi) {
                            return [poi.kategori, poi.warna];
                        })
                    ).entries(),
                ];

                legendElement.innerHTML = uniqueCategories
                    .map(function ([category, color]) {
                        return `
                            <li class="legend-item">
                                <span
                                    class="legend-dot"
                                    style="background-color: ${escapeHtml(color)}"
                                    aria-hidden="true"
                                ></span>

                                <span class="legend-label">
                                    ${escapeHtml(category)}
                                </span>
                            </li>
                        `;
                    })
                    .join("");
            }

            if (resetButton) {
                resetButton.addEventListener("click", function () {
                    map.setView(centerPosition, centerZoom);
                });
            }

            /*
             * Scroll roda mouse baru aktif setelah peta diklik.
             * Ini mencegah halaman sulit digulir.
             */
            map.on("click", function () {
                map.scrollWheelZoom.enable();
            });

            map.on("mouseout", function () {
                map.scrollWheelZoom.disable();
            });

            setTimeout(function () {
                map.invalidateSize();
            }, 100);
        })
        .catch(function (error) {
            console.error("Error memuat peta:", error);

            mapElement.innerHTML = `
                <div class="map-load-error">
                    Peta tidak dapat dimuat. Silakan muat ulang halaman.
                </div>
            `;
        });
});