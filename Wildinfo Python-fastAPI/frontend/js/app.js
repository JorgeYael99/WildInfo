const API_URL = 'http://localhost:8000';

let animalActual = null;

const animalInput = document.getElementById('animalInput');
const buscarBtn = document.getElementById('buscarBtn');
const resultado = document.getElementById('resultado');
const guardarBtn = document.getElementById('guardarBtn');
const listaFavoritos = document.getElementById('listaFavoritos');

const animalNombre = document.getElementById('animalNombre');
const animalReino = document.getElementById('animalReino');
const animalClase = document.getElementById('animalClase');
const animalFamilia = document.getElementById('animalFamilia');
const animalImagen = document.getElementById('animalImagen');
const wikipedia = document.getElementById('wikipedia');
const resumenWikipedia = document.getElementById('resumenWikipedia');
const enlaceWikipedia = document.getElementById('enlaceWikipedia');

buscarBtn.addEventListener('click', buscarAnimal);
animalInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') buscarAnimal();
});
guardarBtn.addEventListener('click', guardarAnimal);

async function buscarAnimal() {
    const nombre = animalInput.value.trim();
    if (!nombre) return;

    try {
        const [infoRes, imagenRes] = await Promise.all([
            fetch(`${API_URL}/wildinfo/${nombre}`),
            fetch(`${API_URL}/api/animal-imagen/${nombre}`)
        ]);

        if (!infoRes.ok) {
            alert('Animal no encontrado');
            return;
        }

        const info = await infoRes.json();
        const imagen = imagenRes.ok ? await imagenRes.json() : { url_imagen: '' };

        const wikiRes = await fetch(`${API_URL}/info-wikipedia/${encodeURIComponent(info.nombre)}`);
        const wiki = wikiRes.ok ? await wikiRes.json() : null;

        animalActual = {
            nombre: info.nombre,
            reino: info.reino,
            clase: info.clase,
            familia: info.familia,
            url_imagen: imagen.url_imagen || '',
            resumen: wiki ? wiki.resumen : '',
            enlace_wikipedia: wiki ? wiki.enlace_articulo : ''
        };

        mostrarResultado(animalActual, wiki);
    } catch (error) {
        console.error('Error:', error);
        alert('Error al conectar con el servidor');
    }
}

function mostrarResultado(animal, wiki) {
    animalNombre.textContent = animal.nombre;
    animalReino.textContent = animal.reino;
    animalClase.textContent = animal.clase;
    animalFamilia.textContent = animal.familia;
    animalImagen.src = animal.url_imagen;
    animalImagen.alt = `Imagen de ${animal.nombre}`;
    
    if (wiki) {
        resumenWikipedia.textContent = wiki.resumen;
        enlaceWikipedia.href = wiki.enlace_articulo;
        wikipedia.classList.remove('hidden');
    } else {
        wikipedia.classList.add('hidden');
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
            alert(`${animalActual.nombre} guardado en favoritos`);
            cargarFavoritos();
        } else {
            const error = await res.json();
            alert(error.detail || 'Error al guardar');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al conectar con el servidor');
    }
}

async function cargarFavoritos() {
    try {
        const res = await fetch(`${API_URL}/animales`);
        const animales = await res.json();

        if (animales.length === 0) {
            listaFavoritos.innerHTML = '<p class="tarjeta-vacia">No hay animales guardados</p>';
            return;
        }

        listaFavoritos.innerHTML = animales.map(animal => `
            <div class="tarjeta-animal">
                <img src="${animal.url_imagen || 'https://via.placeholder.com/300x150?text=Sin+imagen'}" alt="${animal.nombre}">
                <div class="info">
                    <h3>${animal.nombre}</h3>
                    <p><strong>Reino:</strong> ${animal.reino}</p>
                    <p><strong>Clase:</strong> ${animal.clase}</p>
                    <p><strong>Familia:</strong> ${animal.familia}</p>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
        listaFavoritos.innerHTML = '<p class="tarjeta-vacia">Error al cargar favoritos</p>';
    }
}

cargarFavoritos();
