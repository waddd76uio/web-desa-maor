(function () {
    "use strict";

    function initImagePreviews() {
        const imageEditors = document.querySelectorAll("[data-image-editor]");

        console.log(
            "Admin image preview aktif:",
            imageEditors.length,
            "form ditemukan"
        );

        imageEditors.forEach(function (editor) {
            const input = editor.querySelector("[data-image-input]");
            const preview = editor.querySelector("[data-image-preview]");
            const placeholder = editor.querySelector(
                "[data-image-placeholder]"
            );
            const removeButton = editor.querySelector(
                "[data-image-remove]"
            );
            const deleteInput = editor.querySelector(
                "[data-image-delete]"
            );

            if (!input || !preview || !placeholder || !removeButton) {
                console.warn(
                    "Komponen preview tidak lengkap:",
                    editor
                );
                return;
            }

            function showPlaceholder() {
                preview.src = "";
                preview.hidden = true;

                placeholder.hidden = false;
                removeButton.hidden = true;
            }

            function showImage(source) {
                preview.src = source;
                preview.hidden = false;

                placeholder.hidden = true;
                removeButton.hidden = false;
            }

            input.addEventListener("change", function () {
                const file = input.files && input.files[0];

                if (!file) {
                    return;
                }

                if (!file.type || !file.type.startsWith("image/")) {
                    alert(
                        "File yang dipilih harus berupa gambar JPG, JPEG, PNG, atau WEBP."
                    );

                    input.value = "";
                    return;
                }

                const reader = new FileReader();

                reader.addEventListener("load", function (event) {
                    const imageSource = event.target.result;

                    showImage(imageSource);

                    // Jika sebelumnya memilih hapus gambar,
                    // pemilihan gambar baru membatalkannya.
                    if (deleteInput) {
                        deleteInput.value = "0";
                    }
                });

                reader.addEventListener("error", function () {
                    alert("Gambar gagal dibaca. Silakan pilih gambar lain.");

                    input.value = "";
                });

                reader.readAsDataURL(file);
            });

            removeButton.addEventListener("click", function () {
                const isEditForm = Boolean(deleteInput);

                if (isEditForm) {
                    const confirmed = confirm(
                        "Gambar akan dihapus setelah tombol Simpan Perubahan ditekan. Lanjutkan?"
                    );

                    if (!confirmed) {
                        return;
                    }
                }

                input.value = "";
                showPlaceholder();

                if (deleteInput) {
                    deleteInput.value = "1";
                }
            });
        });
    }

    // Tetap berjalan baik ketika script menggunakan defer
    // maupun ketika diletakkan di bagian bawah halaman.
    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initImagePreviews
        );
    } else {
        initImagePreviews();
    }
})();