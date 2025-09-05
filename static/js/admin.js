let currentEditId = null;
let products = JSON.parse(localStorage.getItem("products")) || [
  { id: 1, name: "Americano", category: "cafe", description: "Café espresso con agua caliente, intenso y aromático", price: 3.5, image: "/americano-coffee-cup.jpg" },
  { id: 2, name: "Cappuccino", category: "cafe", description: "Espresso con leche vaporizada y espuma cremosa", price: 4.25, image: "/cappuccino-coffee-with-foam-art.jpg" },
  { id: 3, name: "Frappé de Vainilla", category: "bebidas", description: "Bebida helada con café, leche y sirope de vainilla", price: 5.75, image: "/vanilla-frappe-iced-coffee.jpg" },
  { id: 4, name: "Cheesecake de Fresa", category: "postres", description: "Delicioso cheesecake con mermelada de fresa fresca", price: 4.5, image: "/strawberry-cheesecake-slice.png" },
  { id: 5, name: "Croissant de Almendra", category: "snacks", description: "Croissant artesanal relleno de crema de almendra", price: 3.25, image: "/almond-croissant.png" },
  { id: 6, name: "Latte Macchiato", category: "cafe", description: "Leche vaporizada con espresso y un toque de caramelo", price: 4.75, image: "/latte-macchiato-coffee-layers.jpg" }
];

document.addEventListener("DOMContentLoaded", loadAdminProducts);
document.getElementById("productForm").addEventListener("submit", handleProductSubmit);

function loadAdminProducts() {
  const adminProducts = document.getElementById("adminProducts");
  adminProducts.innerHTML = products.map(product => `
    <div class="admin-product-item">
      <img src="${product.image}" alt="${product.name}" class="admin-product-image">
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
  localStorage.setItem("products", JSON.stringify(products));
}

function getCategoryName(category) {
  return { cafe: "Café", bebidas: "Bebidas", postres: "Postres", snacks: "Snacks" }[category] || category;
}

function handleProductSubmit(e) {
  e.preventDefault();
  const fileInput = document.getElementById("productImage");
  const file = fileInput.files[0];

  if (!file) {
    alert("Debes seleccionar una imagen");
    return;
  }

  const reader = new FileReader();
  reader.onload = function(event) {
    const formData = {
      name: document.getElementById("productName").value,
      category: document.getElementById("productCategory").value,
      description: document.getElementById("productDescription").value,
      price: parseFloat(document.getElementById("productPrice").value),
      image: event.target.result // base64 de la imagen
    };

    if (currentEditId) {
      const index = products.findIndex(p => p.id === currentEditId);
      products[index] = { ...products[index], ...formData };
      currentEditId = null;
      document.getElementById("cancelEdit").style.display = "none";
    } else {
      products.push({ id: Date.now(), ...formData });
    }

    document.getElementById("productForm").reset();
    loadAdminProducts();
    alert("Producto guardado exitosamente");
  };

  reader.readAsDataURL(file);
}

function editProduct(id) {
  const product = products.find(p => p.id === id);
  if (!product) return;
  currentEditId = id;
  document.getElementById("productName").value = product.name;
  document.getElementById("productCategory").value = product.category;
  document.getElementById("productDescription").value = product.description;
  document.getElementById("productPrice").value = product.price;
  document.getElementById("productImage").value = product.image;
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
  }
}

function logout() {
  window.location.href = "/logout";
}
