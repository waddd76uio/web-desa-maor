document.addEventListener("DOMContentLoaded", function () {
    if (typeof L === "undefined") {
        return;
    }

    const mapPickers = document.querySelectorAll("[data-map-picker]");

    mapPickers.forEach(function (mapElement) {
        const latSelector = mapElement.dataset.latInput;
        const lngSelector = mapElement.dataset.lngInput;

        const latInput = document.querySelector(latSelector);
        const lngInput = document.querySelector(lngSelector);

        if (!latInput || !lngInput) {
            return;
        }

        const defaultLat =
            Number(mapElement.dataset.defaultLat) || -7.2024;

        const defaultLng =
            Number(mapElement.dataset.defaultLng) || 112.3505;

        const currentLat = Number(latInput.value);
        const currentLng = Number(lngInput.value);

        const hasCurrentCoordinate =
            Number.isFinite(currentLat) &&
            Number.isFinite(currentLng) &&
            latInput.value !== "" &&
            lngInput.value !== "";

        const initialPosition = hasCurrentCoordinate
            ? [currentLat, currentLng]
            : [defaultLat, defaultLng];

        const map = L.map(mapElement, {
            scrollWheelZoom: false,
        }).setView(
            initialPosition,
            hasCurrentCoordinate ? 17 : 15
        );

        L.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                maxZoom: 19,
                attribution:
                    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            }
        ).addTo(map);

        let locationMarker = null;

        function updateInputs(lat, lng) {
            latInput.value = Number(lat).toFixed(7);
            lngInput.value = Number(lng).toFixed(7);

            latInput.dispatchEvent(
                new Event("change", { bubbles: true })
            );

            lngInput.dispatchEvent(
                new Event("change", { bubbles: true })
            );
        }

        function placeMarker(lat, lng, shouldPan) {
            const position = [lat, lng];

            if (!locationMarker) {
                locationMarker = L.marker(position, {
                    draggable: true,
                }).addTo(map);

                locationMarker.bindTooltip(
                    "Geser penanda untuk memperbaiki posisi",
                    {
                        direction: "top",
                        offset: [0, -10],
                    }
                );

                locationMarker.on("dragend", function () {
                    const markerPosition =
                        locationMarker.getLatLng();

                    updateInputs(
                        markerPosition.lat,
                        markerPosition.lng
                    );
                });
            } else {
                locationMarker.setLatLng(position);
            }

            updateInputs(lat, lng);

            if (shouldPan) {
                map.panTo(position);
            }
        }

        map.on("click", function (event) {
            placeMarker(
                event.latlng.lat,
                event.latlng.lng,
                true
            );
        });

        if (hasCurrentCoordinate) {
            placeMarker(currentLat, currentLng, false);
        }

        setTimeout(function () {
            map.invalidateSize();
        }, 150);
    });
});