// Sample products
let products = [
  { id: 1, name: "Americano", category: "cafe", description: "Café espresso con agua caliente, intenso y aromático", price: 3.5, image: "/americano-coffee-cup.jpg" },
  { id: 2, name: "Cappuccino", category: "cafe", description: "Espresso con leche vaporizada y espuma cremosa", price: 4.25, image: "/cappuccino-coffee-with-foam-art.jpg" },
  { id: 3, name: "Frappé de Vainilla", category: "bebidas", description: "Bebida helada con café, leche y sirope de vainilla", price: 5.75, image: "/vanilla-frappe-iced-coffee.jpg" },
  { id: 4, name: "Cheesecake de Fresa", category: "postres", description: "Delicioso cheesecake con mermelada de fresa fresca", price: 4.5, image: "/strawberry-cheesecake-slice.png" },
  { id: 5, name: "Croissant de Almendra", category: "snacks", description: "Croissant artesanal relleno de crema de almendra", price: 3.25, image: "/almond-croissant.png" },
  { id: 6, name: "Latte Macchiato", category: "cafe", description: "Leche vaporizada con espresso y un toque de caramelo", price: 4.75, image: "/latte-macchiato-coffee-layers.jpg" }
];

// Inicialización
document.addEventListener("DOMContentLoaded", () => {
  loadProducts();
  setupEventListeners();
});

function setupEventListeners() {
  document.querySelectorAll(".filter-btn").forEach(btn => {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
      this.classList.add("active");
      loadProducts(this.dataset.category);
    });
  });

  document.getElementById("loginForm").addEventListener("submit", handleLogin);
}

function loadProducts(category = "all") {
  const productsGrid = document.getElementById("productsGrid");
  const filtered = category === "all" ? products : products.filter(p => p.category === category);
  productsGrid.innerHTML = filtered.map(p => `
    <div class="product-card" data-category="${p.category}">
      <img src="${p.image}" alt="${p.name}" class="product-image">
      <div class="product-info">
        <h3 class="product-name">${p.name}</h3>
        <p class="product-description">${p.description}</p>
        <div class="product-price">$${p.price.toFixed(2)}</div>
      </div>
    </div>
  `).join("");
}

function showAdminLogin() { document.getElementById("adminModal").style.display = "block"; }
function closeAdminLogin() { document.getElementById("adminModal").style.display = "none"; }

async function handleLogin(e) {
  e.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  try {
    const response = await fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: new URLSearchParams({ username, password })
    });

    if (response.redirected) {
      // Login correcto, redirige a /admin
      window.location.href = response.url;
    } else {
      const text = await response.text();
      alert("Usuario o contraseña incorrectos");
    }
  } catch (err) {
    console.error("Error en login:", err);
    alert("Ocurrió un error al iniciar sesión");
  }
}

window.onclick = (event) => {
  if (event.target === document.getElementById("adminModal")) closeAdminLogin();
}
