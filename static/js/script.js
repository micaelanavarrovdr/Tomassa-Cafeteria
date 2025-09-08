let products = [];

// Inicialización
document.addEventListener("DOMContentLoaded", async () => {
  await fetchProducts();   // 🔹 primero traemos desde backend
  loadProducts();
  setupEventListeners();
});

async function fetchProducts() {
  try {
    const res = await fetch("/api/productos");
    products = await res.json();
  } catch (err) {
    console.error("Error cargando productos:", err);
  }
}
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
