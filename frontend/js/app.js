const API_URL = 'http://localhost:8000';
let animalActual = null;
let favoritosLocales = [];
let rachaActual = 0;
let estadoPerfil = { puntos: 0, racha_maxima: 0, badge_oro: false, badge_diversidad: false, rango_titulo: "Observador" };

const ENCICLOPEDIA_INFO = {
    "Mammalia": "Mamíferos: Sangre caliente, pelo y alimentan crías con leche.",
    "Aves": "Aves: Plumas, huesos huecos y reproducción ovípara.",
    "Reptilia": "Reptiles: Sangre fría, piel escamosa y respiración pulmonar.",
    "Amphibia": "Anfibios: Ciclo de vida doble entre agua y tierra.",
    "Actinopterygii": "Peces: Respiración por branquias y vida acuática permanente."
};

const RANGOS = [
    { min: 0, t: "Observador de Jardín", i: "🌱" },
    { min: 5, t: "Explorador de Bosques", i: "🌲" },
    { min: 15, t: "Naturalista de Campo", i: "🦁" },
    { min: 30, t: "Maestro de la Biodiversidad", i: "🌍" }
];

const santuarioObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) document.body.classList.add('modo-santuario');
        else document.body.classList.remove('modo-santuario');
    });
}, { threshold: 0.3 });

async function cargarPerfil() {
    try {
        const res = await fetch(`${API_URL}/perfil`);
        estadoPerfil = await res.json();
        if (estadoPerfil.badge_oro) document.getElementById('badgeOro').classList.add('unlocked');
        if (estadoPerfil.badge_diversidad) document.getElementById('badgeDiversidad').classList.add('unlocked');
        actualizarUI();
    } catch (e) { console.error(e); }
}

function actualizarUI() {
    document.getElementById('tituloRango').textContent = estadoPerfil.rango_titulo;
    const r = RANGOS.find(x => x.t === estadoPerfil.rango_titulo) || RANGOS[0];
    document.getElementById('iconoRango').textContent = r.i;
    const prox = RANGOS[RANGOS.indexOf(r) + 1] || { min: 50 };
    document.getElementById('progresoRango').style.width = `${(estadoPerfil.puntos / prox.min) * 100}%`;
    document.getElementById('statsExplorador').textContent = `Especies: ${favoritosLocales.length} | Clases: ${new Set(favoritosLocales.map(a=>a.clase)).size}`;
}

async function sincronizar() {
    await fetch(`${API_URL}/perfil/progreso`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(estadoPerfil) });
}

const animalInput = document.getElementById('animalInput');
const suggestionsBox = document.getElementById('suggestions');

animalInput.addEventListener('input', async (e) => {
    const q = e.target.value.trim();
    if (q.length < 2) return suggestionsBox.classList.add('hidden');
    const res = await fetch(`${API_URL}/buscar-sugerencias?q=${q}`);
    const data = await res.json();
    suggestionsBox.innerHTML = data.map(n => `<div class="suggestion-item" onclick="seleccionar('${n}')">${n}</div>`).join('');
    suggestionsBox.classList.remove('hidden');
});

window.seleccionar = n => { animalInput.value = n; suggestionsBox.classList.add('hidden'); buscarAnimal(); };

async function buscarAnimal() {
    const n = animalInput.value.trim();
    if (!n) return;
    const [infoR, imgR] = await Promise.all([fetch(`${API_URL}/wildinfo/${n}`), fetch(`${API_URL}/api/animal-imagen/${n}`)]);
    const info = await infoR.json();
    const img = await imgR.json();
    const wikiR = await fetch(`${API_URL}/info-wikipedia/${n}`);
    const wiki = wikiR.ok ? await wikiR.json() : null;

    animalActual = { ...info, url_imagen: img.url_imagen, resumen: wiki?.resumen, enlace: wiki?.enlace_articulo };
    mostrarResultado(animalActual);
}

function mostrarResultado(a) {
    document.getElementById('animalNombre').textContent = a.nombre;
    document.getElementById('animalClase').textContent = a.clase;
    document.getElementById('animalImagen').src = a.url_imagen;
    document.getElementById('resultado').classList.remove('hidden');
}

async function guardar() {
    if (!animalActual) return;
    const res = await fetch(`${API_URL}/animales`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(animalActual) });
    if (res.ok) cargarFavoritos();
}

async function cargarFavoritos() {
    const res = await fetch(`${API_URL}/animales`);
    favoritosLocales = await res.json();
    
    const sRiesgo = document.getElementById('santuarioRiesgo');
    const listaPeligro = document.getElementById('listaPeligro');
    const contenedorNormal = document.getElementById('contenedorCarpetas');

    const enPeligro = favoritosLocales.filter(a => a.en_peligro);
    const seguros = favoritosLocales.filter(a => !a.en_peligro);

    if (enPeligro.length > 0) {
        sRiesgo.classList.remove('hidden');
        listaPeligro.innerHTML = enPeligro.map(a => generarHTML(a, true)).join('');
        santuarioObserver.observe(sRiesgo);
    } else { sRiesgo.classList.add('hidden'); }

    const grupos = seguros.reduce((acc, a) => { (acc[a.clase] = acc[a.clase] || []).push(a); return acc; }, {});
    contenedorNormal.innerHTML = Object.keys(grupos).map(c => `
        <div class="grupo-especie">
            <h3>📂 ${c} (${grupos[c].length})</h3>
            <div class="descripcion-clase">${ENCICLOPEDIA_INFO[c] || "Información taxonómica."}</div>
            <div class="grid-especie">${grupos[c].map(a => generarHTML(a, false)).join('')}</div>
        </div>
    `).join('');

    const clasesUnicas = new Set(favoritosLocales.map(a => a.clase)).size;
    estadoPerfil.puntos = favoritosLocales.length + (clasesUnicas * 3);
    if (clasesUnicas >= 5) { estadoPerfil.badge_diversidad = true; document.getElementById('badgeDiversidad').classList.add('unlocked'); }
    
    const nuevoR = [...RANGOS].reverse().find(r => estadoPerfil.puntos >= r.min);
    estadoPerfil.rango_titulo = nuevoR.t;
    actualizarUI();
    sincronizar();
}

function generarHTML(a, esPeligro) {
    return `<div class="tarjeta-animal ${esPeligro ? 'tarjeta-peligro' : ''}" onclick="seleccionar('${a.nombre}')">
        <div class="tarjeta-imagen-container"><img src="${a.url_imagen}"></div>
        <div class="info-compacta"><h4>${a.nombre}</h4><p>${esPeligro ? '⚠️ RIESGO CRÍTICO' : a.familia}</p></div>
        <button class="btn-eliminar" onclick="eliminar(event, '${a.nombre}')">×</button>
    </div>`;
}

async function eliminar(e, n) {
    e.stopPropagation();
    await fetch(`${API_URL}/animales/${n}`, { method: 'DELETE' });
    cargarFavoritos();
}

document.getElementById('btnQuiz').onclick = () => {
    if (favoritosLocales.length < 3) return alert("Faltan animales.");
    document.getElementById('quizModal').classList.remove('hidden');
    generarPregunta();
};

function generarPregunta() {
    const a = favoritosLocales[Math.floor(Math.random() * favoritosLocales.length)];
    const clases = [...new Set(favoritosLocales.map(x => x.clase))];
    let opc = [a.clase, ...clases.filter(c => c !== a.clase).sort(() => 0.5 - Math.random()).slice(0, 3)].sort(() => 0.5 - Math.random());
    document.getElementById('preguntaTexto').textContent = `¿Clase de: ${a.nombre}?`;
    document.getElementById('quizImagen').src = a.url_imagen;
    document.getElementById('opcionesContainer').innerHTML = opc.map(o => `<button class="opcion-btn" onclick="validar(this, '${o}', '${a.clase}')">${o}</button>`).join('');
}

function validar(btn, sel, cor) {
    if (sel === cor) {
        btn.classList.add('correcto');
        rachaActual++;
        
        if (rachaActual === 10) {
            finalizarQuizExitoso();
            return;
        }
    } else {
        btn.classList.add('incorrecto');
        alert(`¡Oh no! Perdiste la racha. Lograste: ${rachaActual}`);
        rachaActual = 0;
        document.getElementById('quizModal').classList.add('hidden');
    }
    
    document.getElementById('quizRacha').textContent = `Racha: ${rachaActual} / 10 🔥`;
    if (rachaActual < 10 && rachaActual > 0) {
        setTimeout(generarPregunta, 1200);
    }
}

async function finalizarQuizExitoso() {
    alert("¡Increíble! Has completado el Reto de 10 preguntas.");
    
    estadoPerfil.puntos += 20; 
    
    if (rachaActual > estadoPerfil.racha_maxima) {
        estadoPerfil.racha_maxima = rachaActual;
    }
    
    estadoPerfil.badge_oro = true;
    document.getElementById('badgeOro').classList.add('unlocked');

    const nuevoR = [...RANGOS].reverse().find(r => estadoPerfil.puntos >= r.min);
    estadoPerfil.rango_titulo = nuevoR.t;

    rachaActual = 0;
    
    actualizarUI();
    await sincronizar();
    
    document.getElementById('quizModal').classList.add('hidden');
}

document.getElementById('buscarBtn').onclick = buscarAnimal;
document.getElementById('guardarBtn').onclick = guardar;
document.querySelector('.close-modal').onclick = () => document.getElementById('quizModal').classList.add('hidden');

cargarPerfil();
cargarFavoritos();