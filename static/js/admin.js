document.querySelectorAll('.btn-edit').forEach(btn => {
  btn.addEventListener('click', () => {
    const id = btn.dataset.id;
    const name = JSON.parse(btn.dataset.name);           // 🔹 Parse JSON
    const description = JSON.parse(btn.dataset.description); // 🔹 Parse JSON
    const price = btn.dataset.price;
    const categoryId = btn.dataset.category;
    const imageBase64 = btn.dataset.image;

    openEditForm(id, name, description, price, categoryId, imageBase64);
  });
});



// ========================
// Preview de imagen al agregar producto
// ========================
const productImageInput = document.getElementById("productImage");
const imagePreview = document.getElementById("imagePreview");

productImageInput.addEventListener("change", function () {
  const file = this.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      imagePreview.src = e.target.result;
      imagePreview.style.display = "block";
    }
    reader.readAsDataURL(file);
  } else {
    imagePreview.src = "";
    imagePreview.style.display = "none";
  }
});

// ========================
// Función para eliminar producto
// ========================
function deleteProduct(id) {
  if (confirm("¿Deseas eliminar este producto?")) {
    fetch(`/delete_product/${id}`, { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          location.reload();
        } else {
          alert("Error al eliminar: " + data.error);
        }
      })
      .catch(err => alert("Error al conectar con el servidor: " + err));
  }
}

// ========================
// Modal de edición de producto
// ========================
let currentEditId = null;

function openEditForm(id, name, description, price, categoryId, imageBase64) {
  currentEditId = id;

  document.getElementById("editName").value = name;
  document.getElementById("editDescription").value = description;
  document.getElementById("editPrice").value = price;
  document.getElementById("editCategory").value = categoryId;

  const editImagePreview = document.getElementById("editImagePreview");
  editImagePreview.src = "data:image/jpeg;base64," + imageBase64;
  editImagePreview.style.display = "block";

  const form = document.getElementById("editProductForm");
  form.action = `/update_product/${id}`;

  document.getElementById("editModal").style.display = "block";
}

function closeEditForm() {
  document.getElementById("editModal").style.display = "none";
}

// Preview de imagen en el modal de edición
const editImageInput = document.getElementById("editImage");
const editImagePreview = document.getElementById("editImagePreview");

editImageInput.addEventListener("change", function () {
  const file = this.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      editImagePreview.src = e.target.result;
      editImagePreview.style.display = "block";
    }
    reader.readAsDataURL(file);
  }
});

// ========================
// Reiniciar formulario después de agregar o editar
// ========================
document.getElementById("productForm").addEventListener("reset", () => {
  currentEditId = null;
  const form = document.getElementById("productForm");
  form.action = "/add_product";
  form.querySelector("button[type='submit']").textContent = "Agregar Producto";
});

// Filtrar productos por categoría
const filterCategory = document.getElementById("filterCategory");
const adminProducts = document.getElementById("adminProducts");

filterCategory.addEventListener("change", () => {
    const selectedCategory = filterCategory.value; // puede ser "all" o idCategoria
    document.querySelectorAll(".admin-product-item").forEach(item => {
        if (selectedCategory === "all" || item.dataset.category === selectedCategory) {
            item.style.display = "flex"; // o "block", según tu diseño
        } else {
            item.style.display = "none";
        }
    });
});


// ========================
// Logout
// ========================
function logout() {
  window.location.href = "/logout";
}
