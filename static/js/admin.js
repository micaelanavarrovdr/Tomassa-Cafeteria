let currentEditId = null;
let products = JSON.parse(localStorage.getItem("products")) || [];

document.addEventListener("DOMContentLoaded", loadAdminProducts);
// COMENTADO: Esta línea evita que el formulario se envíe al servidor
// document.getElementById("productForm").addEventListener("submit", handleProductSubmit);

function loadAdminProducts() {
  // Esta función puede quedarse para mostrar productos existentes
  // pero debería cargar desde el servidor, no desde localStorage
  const adminProducts = document.getElementById("adminProducts");
  adminProducts.innerHTML = products.map(product => `
    <div class="admin-product-item">
      <img src="data:image/jpeg;base64,${product.image}" alt="${product.name}" class="admin-product-image">
      <div class="admin-product-info">
        <h4>${product.name}</h4>
        <p>${product.description}</p>
        <p><strong>Categoría:</strong> ${getCategoryName(product.category)}</p>
        <div class="admin-product-price">$${product.price.toFixed(2)}</div>
      </div>
      <div class="admin-product-actions">
        <button class="btn-edit" onclick="editProduct(${product.id})">Editar</button>
        <button class="btn-delete" onclick="deleteProduct(${product.id})">Eliminar</button>
      </div>
    </div>
  `).join("");
}

function getCategoryName(category) {
  return { cafe: "Café", bebidas: "Bebidas", postres: "Postres", snacks: "Snacks" }[category] || category;
}

// COMENTADO: Esta función impide el envío al servidor
/*
function handleProductSubmit(e) {
  e.preventDefault(); // ¡ESTO IMPIDE QUE SE ENVÍE AL SERVIDOR!
  // ... resto del código que solo guarda en localStorage
}
*/

function editProduct(id) {
  const product = products.find(p => p.id === id);
  if (!product) return;
  currentEditId = id;
  document.getElementById("productName").value = product.name;
  document.getElementById("productCategory").value = product.category;
  document.getElementById("productDescription").value = product.description;
  document.getElementById("productPrice").value = product.price;
  // Nota: No puedes restaurar el archivo de imagen en un input file
  document.getElementById("cancelEdit").style.display = "inline-block";
}

function cancelEdit() {
  currentEditId = null;
  document.getElementById("productForm").reset();
  document.getElementById("cancelEdit").style.display = "none";
}

function deleteProduct(id) {
  if (confirm("¿Deseas eliminar este producto?")) {
    products = products.filter(p => p.id !== id);
    loadAdminProducts();
    // Aquí deberías hacer una petición al servidor para eliminar de la BD
  }
}

// Preview de imagen antes de subir
const productImageInput = document.getElementById("productImage");
const imagePreview = document.getElementById("imagePreview");

productImageInput.addEventListener("change", function () {
  const file = this.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      imagePreview.src = e.target.result; // Mostrar la imagen
      imagePreview.style.display = "block"; // Hacer visible la imagen
    }
    reader.readAsDataURL(file);
  } else {
    imagePreview.src = "";
    imagePreview.style.display = "none";
  }
});


function logout() {
  window.location.href = "/logout";
}