// 🔹 Obtener los datos desde los scripts JSON en HTML
const cantidadData = JSON.parse(document.getElementById('cantidadData').textContent);
const promedioData = JSON.parse(document.getElementById('promedioData').textContent);

// Labels y valores
const categorias = Object.keys(cantidadData);
const cantidades = Object.values(cantidadData);
const promedios = Object.values(promedioData);

// Gráfico de barras - Cantidad por categoría
new Chart(document.getElementById('cantidadChart'), {
    type: 'bar',
    data: {
        labels: categorias,
        datasets: [{
            label: 'Cantidad de productos',
            data: cantidades,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    precision: 0, 
                    stepSize: 1   
                }
            }
        }
    }
});


// Gráfico de barras - Precio promedio por categoría
new Chart(document.getElementById('promedioChart'), {
    type: 'bar',
    data: {
        labels: categorias,
        datasets: [{
            label: 'Precio promedio ($)',
            data: promedios,
            backgroundColor: 'rgba(255, 159, 64, 0.6)',
            borderColor: 'rgba(255, 159, 64, 1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: { beginAtZero: true }
        }
    }
});
