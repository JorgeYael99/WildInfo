const API_URL = 'http://localhost:8000';
let animalActual = null;

const animalInput = document.getElementById('animalInput');
const suggestionsBox = document.getElementById('suggestions');
const buscarBtn = document.getElementById('buscarBtn');
const resultado = document.getElementById('resultado');
const statusBadge = document.getElementById('statusBadge');
const listaFavoritos = document.getElementById('listaFavoritos');

animalInput.addEventListener('input', async (e) => {
    const query = e.target.value.trim();
    if (query.length < 2) {
        suggestionsBox.classList.add('hidden');
        return;
    }

    try {
        const res = await fetch(`${API_URL}/buscar-sugerencias?q=${query}`);
        const data = await res.json();
        
        if (data && data.length > 0) {
            suggestionsBox.innerHTML = data.map(nombre => `
                <div class="suggestion-item" onclick="seleccionarEspecie('${nombre}')">${nombre}</div>
            `).join('');
            suggestionsBox.classList.remove('hidden');
        } else {
            suggestionsBox.classList.add('hidden');
        }
    } catch (err) {
        console.error("Error en sugerencias");
    }
});

window.seleccionarEspecie = (nombre) => {
    animalInput.value = nombre;
    suggestionsBox.classList.add('hidden');
    buscarAnimal();
};

async function buscarAnimal() {
    const nombre = animalInput.value.trim();
    if (!nombre) return;
    suggestionsBox.classList.add('hidden');

    try {
        const [infoRes, imagenRes] = await Promise.all([
            fetch(`${API_URL}/wildinfo/${nombre}`),
            fetch(`${API_URL}/api/animal-imagen/${nombre}`)
        ]);

        if (!infoRes.ok) {
            alert('No se encontró la información');
            return;
        }

        const info = await infoRes.json();
        const imagen = await imagenRes.json();
        
        const wikiRes = await fetch(`${API_URL}/info-wikipedia/${encodeURIComponent(info.nombre)}`);
        const wiki = wikiRes.ok ? await wikiRes.json() : null;

        animalActual = {
            nombre: info.nombre,
            reino: info.reino,
            clase: info.clase,
            familia: info.familia,
            url_imagen: imagen.url_imagen || '',
            resumen: wiki ? wiki.resumen : '',
            enlace_wikipedia: wiki ? wiki.enlace_articulo : '',
            en_peligro: info.en_peligro
        };

        mostrarResultado(animalActual);
    } catch (error) {
        console.error(error);
    }
}

function mostrarResultado(animal) {
    document.getElementById('animalNombre').textContent = animal.nombre;
    document.getElementById('animalReino').textContent = animal.reino;
    document.getElementById('animalClase').textContent = animal.clase;
    document.getElementById('animalFamilia').textContent = animal.familia;
    document.getElementById('animalImagen').src = animal.url_imagen;
    
    if (animal.en_peligro) {
        statusBadge.textContent = "ESPECIE PROTEGIDA / RIESGO";
        statusBadge.classList.remove('hidden');
        statusBadge.className = "badge danger";
    } else {
        statusBadge.classList.add('hidden');
    }

    if (animal.resumen) {
        document.getElementById('resumenWikipedia').textContent = animal.resumen;
        document.getElementById('enlaceWikipedia').href = animal.enlace_wikipedia;
        document.getElementById('wikipedia').classList.remove('hidden');
    } else {
        document.getElementById('wikipedia').classList.add('hidden');
    }

    resultado.classList.remove('hidden');
}

async function guardarAnimal() {
    if (!animalActual) return;
    try {
        const res = await fetch(`${API_URL}/animales`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(animalActual)
        });
        if (res.ok) {
            cargarFavoritos();
        } else {
            const err = await res.json();
            alert(err.detail);
        }
    } catch (error) {
        console.error(error);
    }
}

// Nueva función para borrar de la BD
async function eliminarFavorito(event, nombre) {
    event.stopPropagation(); // Evita que se abra la ficha al hacer clic en borrar
    if (!confirm(`¿Eliminar ${nombre} de tus favoritos?`)) return;

    try {
        const res = await fetch(`${API_URL}/animales/${encodeURIComponent(nombre)}`, {
            method: 'DELETE'
        });

        if (res.ok) {
            cargarFavoritos();
        } else {
            alert("No se pudo eliminar");
        }
    } catch (error) {
        console.error("Error al eliminar:", error);
    }
}

// Actualización de la lista para incluir el botón de borrar
async function cargarFavoritos() {
    try {
        const res = await fetch(`${API_URL}/animales`);
        const animales = await res.json();
        
        if (!animales.length) {
            listaFavoritos.innerHTML = '<p class="tarjeta-vacia">Aún no tienes favoritos</p>';
            return;
        }

        listaFavoritos.innerHTML = animales.map(a => `
            <div class="tarjeta-animal" onclick="seleccionarEspecie('${a.nombre}')">
                <button class="btn-eliminar" onclick="eliminarFavorito(event, '${a.nombre}')">×</button>
                <img src="${a.url_imagen || 'https://via.placeholder.com/150'}" alt="${a.nombre}">
                <div class="info">
                    <h3>${a.nombre}</h3>
                    <p>${a.clase || 'Especie'}</p>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

buscarBtn.addEventListener('click', buscarAnimal);
document.getElementById('guardarBtn').addEventListener('click', guardarAnimal);
document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-wrapper')) suggestionsBox.classList.add('hidden');
});

cargarFavoritos();