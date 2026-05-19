/* --- CONFIGURACIÓN INICIAL --- */
const API_URL = 'http://localhost:8000';
const API_SECRET_KEY = 'Cisco_Net_2026_ClaveSegura';

function getAuthHeaders() {
    const userData = JSON.parse(localStorage.getItem('usuario_wildinfo') || '{}');
    if (!userData.token || !userData.user_id) return {};
    return {
        'Authorization': `Bearer ${userData.token}`,
        'X-User-Id': userData.user_id,
        'X-Username': userData.username || ''
    };
}

function getSecureHeaders() {
    return {
        ...getAuthHeaders(),
        'X-API-KEY': API_SECRET_KEY
    };
}

let animalActual = null;
let favoritosLocales = [];
// Estado inicial del perfil
let estadoPerfil = { 
    puntos: 0, 
    racha_maxima: 0, 
    badge_oro: false, 
    badge_diversidad: false, 
    rango_titulo: "Observador" 
};

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

/* --- LÓGICA DE PERFIL Y PROGRESO --- */
async function cargarPerfil() {
    const headers = getAuthHeaders();
    if (!headers['Authorization']) {
        window.location.href = 'login.html';
        return;
    }
    
    try {
        const res = await fetch(`${API_URL}/perfil/`, { headers });
        if (res.ok) {
            estadoPerfil = await res.json();
            if (estadoPerfil.badge_oro) document.getElementById('badgeOro').classList.add('unlocked');
            if (estadoPerfil.badge_diversidad) document.getElementById('badgeDiversidad').classList.add('unlocked');
            actualizarUI();
        } else if (res.status === 401) {
            localStorage.removeItem('usuario_wildinfo');
            window.location.href = 'login.html';
        }
    } catch (e) { 
        console.error("Error al cargar perfil:", e);
    }
}

function actualizarUI() {
    document.getElementById('tituloRango').textContent = estadoPerfil.rango_titulo;
    const r = RANGOS.find(x => x.t === estadoPerfil.rango_titulo) || RANGOS[0];
    document.getElementById('iconoRango').textContent = r.i;
    
    const indexActual = RANGOS.indexOf(r);
    const prox = RANGOS[indexActual + 1] || { min: 50 };
    
    const porcentaje = Math.min((estadoPerfil.puntos / prox.min) * 100, 100);
    document.getElementById('progresoRango').style.width = `${porcentaje}%`;
    
    const numClases = new Set(favoritosLocales.map(a => a.clase)).size;
    document.getElementById('statsExplorador').textContent = `Especies: ${favoritosLocales.length} | Clases: ${numClases}`;
}

async function sincronizar() {
    const headers = getSecureHeaders();
    if (!headers['Authorization']) return;
    
    try {
        await fetch(`${API_URL}/perfil/progreso`, { 
            method: 'PUT', 
            headers: { ...headers, 'Content-Type': 'application/json' }, 
            body: JSON.stringify(estadoPerfil) 
        });
    } catch (e) { 
        console.error("Error al sincronizar:", e);
    }
}

/* --- BUSCADOR Y RESULTADOS --- */
const animalInput = document.getElementById('animalInput');
const suggestionsBox = document.getElementById('suggestions');

animalInput.addEventListener('input', async (e) => {
    const q = e.target.value.trim();
    if (q.length < 2) return suggestionsBox.classList.add('hidden');
    
    try {
        const res = await fetch(`${API_URL}/animales/buscar-sugerencias?q=${q}`);
        const data = await res.json();
        suggestionsBox.innerHTML = data.map(n => `<div class="suggestion-item" onclick="seleccionar('${n}')">${n}</div>`).join('');
        suggestionsBox.classList.remove('hidden');
    } catch (e) { console.error(e); }
});

window.seleccionar = n => { 
    animalInput.value = n; 
    suggestionsBox.classList.add('hidden'); 
    buscarAnimal(); 
};

async function buscarAnimal() {
    const n = animalInput.value.trim();
    if (!n) return;

    // Limpieza absoluta preventiva de la interfaz
    document.getElementById('animalNombre').textContent = "Buscando...";
    document.getElementById('animalReino').textContent = "Reino: ---";
    document.getElementById('animalClase').textContent = "Clase: ---";
    document.getElementById('animalFamilia').textContent = "Familia: ---";
    document.getElementById('animalHabitat').textContent = "Hábitat: ---";
    document.getElementById('animalDieta').textContent = "Dieta: ---";
    document.getElementById('animalLongevidad').textContent = "Longevidad: ---";
    document.getElementById('animalPeso').textContent = "Peso: ---";
    document.getElementById('animalVelocidad').textContent = "Velocidad: ---";
    document.getElementById('resumenWikipedia').textContent = "Consultando base de datos enciclopédica...";
    document.getElementById('statusBadge').classList.add('hidden');
    document.getElementById('enlaceWikipedia').style.display = 'none';

    try {
        // 1. Petición base de información científica
        const infoR = await fetch(`${API_URL}/animales/info/${encodeURIComponent(n)}`);

        if (!infoR.ok) {
            const errData = await infoR.json();
            alert(`WildInfo: ${errData.detail || "No se encontraron datos."}`);
            document.getElementById('animalNombre').textContent = "No disponible";
            document.getElementById('resumenWikipedia').textContent = "La búsqueda no arrojó un animal válido.";
            return;
        }

        const info = await infoR.json();

        // 2. CORRECCIÓN DEFINITIVA DE LAS RUTAS SECUNDARIAS (Evita el error 404 de concatenación)
        const URL_IMAGEN = API_URL + '/animales/imagen/' + encodeURIComponent(info.nombre);
        const URL_WIKIPEDIA = API_URL + '/animales/wikipedia/' + encodeURIComponent(info.nombre);

        const [imgR, wikiR] = await Promise.all([
            fetch(URL_IMAGEN),
            fetch(URL_WIKIPEDIA)
        ]);

        const img = await imgR.json();
        const wiki = wikiR.ok ? await wikiR.json() : null;

        animalActual = { 
            ...info, 
            url_imagen: img.url_imagen || '', 
            resumen: wiki?.resumen || 'Sin resumen enciclopédico disponible para esta especie.', 
            enlace: wiki?.enlace_articulo || '#' 
        };
        
        mostrarResultado(animalActual);
    } catch (e) { 
        console.error("Error al buscar animal:", e);
        alert("Ocurrió un error al procesar la búsqueda.");
    }
}

function mostrarResultado(a) {
    try {
        document.getElementById('animalNombre').textContent = a.nombre || 'Especie';
        document.getElementById('animalClase').textContent = a.clase || 'Desconocida';
        document.getElementById('animalFamilia').textContent = a.familia || 'N/A';
        document.getElementById('animalReino').textContent = a.reino || 'Animalia';
        
        document.getElementById('animalHabitat').textContent = `Hábitat: ${a.habitat || 'No disponible'}`;
        document.getElementById('animalDieta').textContent = `Dieta: ${a.dieta || 'No disponible'}`;
        document.getElementById('animalLongevidad').textContent = `Longevidad: ${a.longevidad || 'No disponible'}`;
        document.getElementById('animalPeso').textContent = `Peso: ${a.peso || 'No disponible'}`;
        document.getElementById('animalVelocidad').textContent = `Velocidad: ${a.velocidad || 'No disponible'}`;
        
        document.getElementById('animalImagen').src = a.url_imagen || '';
        document.getElementById('animalImagen').alt = `Fotografía de un ${a.nombre}`;
        
        document.getElementById('resumenWikipedia').textContent = a.resumen || 'Sin información disponible.';
        
        if (a.enlace && a.enlace !== '#') {
            document.getElementById('enlaceWikipedia').href = a.enlace;
            document.getElementById('enlaceWikipedia').style.display = 'inline-block';
        } else {
            document.getElementById('enlaceWikipedia').style.display = 'none';
        }
        
        // Control del letrero de peligro de extinción
        const statusBadge = document.getElementById('statusBadge');
        if (a.en_peligro === true || a.en_peligro === 'true') {
            statusBadge.textContent = '⚠️ EN PELIGRO DE EXTINCIÓN';
            statusBadge.classList.remove('hidden');
            statusBadge.style.display = 'block';
        } else {
            statusBadge.classList.add('hidden');
            statusBadge.style.display = 'none';
        }
        
        document.getElementById('resultado').classList.remove('hidden');
        
    } catch (error) {
        console.error("Error crítico actualizando el DOM:", error);
    }
}

async function guardar() {
    if (!animalActual) return;
    const headers = getSecureHeaders();
    if (!headers['Authorization']) return;
    
    try {
        const res = await fetch(`${API_URL}/animales/`, { 
            method: 'POST', 
            headers: { ...headers, 'Content-Type': 'application/json' }, 
            body: JSON.stringify(animalActual) 
        });
        if (res.ok) {
            cargarFavoritos();
            document.getElementById('resultado').classList.add('hidden');
            animalInput.value = '';
        } else {
            const data = await res.json();
            alert(data.detail || "Este animal ya está en tu colección.");
        }
    } catch (e) { 
        console.error(e); 
    }
}

/* --- BIBLIOTECA Y SANTUARIO --- */
const santuarioObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) document.body.classList.add('modo-santuario');
        else document.body.classList.remove('modo-santuario');
    });
}, { threshold: 0.3 });

async function cargarFavoritos() {
    const headers = getAuthHeaders();
    if (!headers['Authorization']) {
        window.location.href = 'login.html';
        return;
    }
    
    try {
        const res = await fetch(`${API_URL}/animales/`, { headers });
        if (res.status === 401) {
            localStorage.removeItem('usuario_wildinfo');
            window.location.href = 'login.html';
            return;
        }
        favoritosLocales = await res.json();
        
        const sRiesgo = document.getElementById('santuarioRiesgo');
        const listaPeligro = document.getElementById('listaPeligro');
        const contenedorNormal = document.getElementById('contenedorCarpetas');

        const enPeligro = favoritosLocales.filter(a => a.en_peligro);
        const seguros = favoritosLocales.filter(a => !a.en_peligro);

        // Manejo del Santuario
        if (enPeligro.length > 0) {
            sRiesgo.classList.remove('hidden');
            listaPeligro.innerHTML = enPeligro.map(a => generarHTML(a, true)).join('');
            santuarioObserver.observe(sRiesgo);
        } else { 
            sRiesgo.classList.add('hidden'); 
            document.body.classList.remove('modo-santuario');
        }

        // Manejo de Carpetas por Clase
        const grupos = seguros.reduce((acc, a) => { 
            (acc[a.clase] = acc[a.clase] || []).push(a); 
            return acc; 
        }, {});

        contenedorNormal.innerHTML = Object.keys(grupos).map(c => `
            <div class="grupo-especie">
                <h3>📂 ${c} (${grupos[c].length})</h3>
                <div class="descripcion-clase">${ENCICLOPEDIA_INFO[c] || "Información taxonómica."}</div>
                <div class="grid-especie">${grupos[c].map(a => generarHTML(a, false)).join('')}</div>
            </div>
        `).join('');

        // Actualizar Puntos y Logros
        const clasesUnicas = new Set(favoritosLocales.map(a => a.clase)).size;
        estadoPerfil.puntos = favoritosLocales.length + (clasesUnicas * 3);
        
        if (clasesUnicas >= 5) { 
            estadoPerfil.badge_diversidad = true; 
            document.getElementById('badgeDiversidad').classList.add('unlocked'); 
        }
        
        const nuevoR = [...RANGOS].reverse().find(r => estadoPerfil.puntos >= r.min);
        estadoPerfil.rango_titulo = nuevoR.t;
        
        actualizarUI();
        sincronizar();
    } catch (e) { console.error("Error al cargar favoritos:", e); }
    
    if (favoritosLocales.length === 0) {
        document.getElementById('contenedorCarpetas').innerHTML = `
            <div class="empty-state">
                <p style="text-align:center;color:#94a3b8;padding:2rem;">
                    Aún no has añadido especies a tu enciclopeda.
                    Busca un animal y presiona "Añadir a mi Enciclopedia".
                </p>
            </div>`;
    }
}

function generarHTML(a, esPeligro) {
    return `
    <div class="tarjeta-animal ${esPeligro ? 'tarjeta-peligro' : ''}" onclick="seleccionar('${a.nombre}')">
        <div class="tarjeta-imagen-container"><img src="${a.url_imagen}" alt="${a.nombre}"></div>
        <div class="info-compacta">
            <h4>${a.nombre}</h4>
            <p>${esPeligro ? '⚠️ RIESGO CRÍTICO' : (a.familia || 'Especie')}</p>
        </div>
        <button class="btn-eliminar" onclick="eliminar(event, '${a.nombre}')">×</button>
    </div>`;
}

async function eliminar(e, n) {
    e.stopPropagation();
    if (!confirm(`¿Eliminar a ${n} de tu colección?`)) return;
    const headers = getSecureHeaders();
    if (!headers['Authorization']) return;
    
    try {
        await fetch(`${API_URL}/animales/${encodeURIComponent(n)}`, { method: 'DELETE', headers });
        cargarFavoritos();
    } catch (e) { 
        console.error(e);
    }
}

/* --- SISTEMA DE QUIZ MEJORADO --- */

let quizActivo = null;

document.getElementById('btnQuiz').onclick = iniciarQuiz;

function iniciarQuiz() {
    if (favoritosLocales.length < 3) {
        return alert("Necesitas al menos 3 animales en tu enciclopedia para jugar.");
    }

    const cola = [];
    const TIPOS = ['clase', 'familia', 'reino', 'peligro'];

    for (let i = 0; i < 10; i++) {
        const a = favoritosLocales[Math.floor(Math.random() * favoritosLocales.length)];
        const tipo = TIPOS[i % TIPOS.length];
        const p = crearPregunta(tipo, a);
        if (p) cola.push(p);
    }

    cola.sort(() => Math.random() - 0.5);

    quizActivo = {
        cola,
        actual: 0,
        aciertos: 0,
        fallos: 0,
        racha_max: 0,
        racha_act: 0,
        respondida: false,
        timerSegundos: 15,
        timerId: null,
    };

    document.getElementById('quizModal').classList.remove('hidden');
    document.getElementById('quizResultados').classList.add('hidden');
    document.getElementById('quizJuego').classList.remove('hidden');
    mostrarPregunta();
}

function crearPregunta(tipo, animal) {
    const todos = favoritosLocales;

    switch (tipo) {
        case 'clase': {
            const correcta = animal.clase;
            if (!correcta) return null;
            const clases = [...new Set(todos.map(x => x.clase).filter(c => c && c !== correcta))];
            if (clases.length < 3) return null;
            const distractores = clases.sort(() => Math.random() - 0.5).slice(0, 3);
            const opciones = [correcta, ...distractores].sort(() => Math.random() - 0.5);
            return { tipo, animal, pregunta: `¿A qué clase pertenece ${animal.nombre}?`, correcta, opciones };
        }
        case 'familia': {
            const correcta = animal.familia || animal.clase;
            const familias = [...new Set(todos.map(x => x.familia).filter(f => f && f !== correcta))];
            if (familias.length < 3) return crearPregunta('clase', animal);
            const distractores = familias.sort(() => Math.random() - 0.5).slice(0, 3);
            const opciones = [correcta, ...distractores].sort(() => Math.random() - 0.5);
            return { tipo, animal, pregunta: `¿De qué familia es ${animal.nombre}?`, correcta, opciones };
        }
        case 'reino': {
            const opciones = ['Animalia', 'Plantae', 'Fungi', 'Protista'].sort(() => Math.random() - 0.5);
            return { tipo, animal, pregunta: `¿A qué reino pertenece ${animal.nombre}?`, correcta: 'Animalia', opciones };
        }
        case 'peligro': {
            const opciones = ['Sí', 'No'];
            return {
                tipo, animal,
                pregunta: `¿Está ${animal.nombre} en peligro de extinción?`,
                correcta: animal.en_peligro ? 'Sí' : 'No',
                opciones,
            };
        }
        default: return null;
    }
}

function mostrarPregunta() {
    if (!quizActivo || quizActivo.actual >= quizActivo.cola.length) {
        finalizarQuiz();
        return;
    }

    const p = quizActivo.cola[quizActivo.actual];
    quizActivo.respondida = false;
    quizActivo.timerSegundos = 15;

    document.getElementById('preguntaTexto').textContent = p.pregunta;
    document.getElementById('quizImagen').src = p.animal.url_imagen || '';
    document.getElementById('quizImagen').alt = p.animal.nombre;

    document.getElementById('quizContador').textContent = `Pregunta ${quizActivo.actual + 1} / 10`;
    document.getElementById('quizProgresoFill').style.width = `${(quizActivo.actual / 10) * 100}%`;
    document.getElementById('quizRacha').textContent = `🔥 ${quizActivo.racha_act}`;

    document.getElementById('opcionesContainer').innerHTML = p.opciones.map(o =>
        `<button class="opcion-btn" data-valor="${o}">${o}</button>`
    ).join('');

    document.getElementById('opcionesContainer').onclick = (e) => {
        const btn = e.target.closest('.opcion-btn');
        if (btn) responderPregunta(btn);
    };

    document.getElementById('quizFeedback').classList.add('hidden');
    iniciarTimer();
}

function iniciarTimer() {
    detenerTimer();
    actualizarTimerDisplay();
    quizActivo.timerId = setInterval(() => {
        quizActivo.timerSegundos--;
        actualizarTimerDisplay();
        if (quizActivo.timerSegundos <= 0) {
            detenerTimer();
            tiempoAgotado();
        }
    }, 1000);
}

function detenerTimer() {
    if (quizActivo.timerId) {
        clearInterval(quizActivo.timerId);
        quizActivo.timerId = null;
    }
}

function actualizarTimerDisplay() {
    const t = quizActivo.timerSegundos;
    document.getElementById('quizTimer').textContent = `⏱️ ${t}s`;
    const bar = document.getElementById('quizTimerBar');
    bar.style.width = `${(t / 15) * 100}%`;
    bar.style.background = t > 5 ? '#4ade80' : t > 3 ? '#fbbf24' : '#ef4444';
}

function tiempoAgotado() {
    if (quizActivo.respondida) return;
    quizActivo.respondida = true;
    quizActivo.fallos++;
    quizActivo.racha_act = 0;
    bloquearBotones();
    mostrarFeedback(false, '⏰ ¡Se acabó el tiempo!');
    setTimeout(avanzarPregunta, 1500);
}

function responderPregunta(btn) {
    if (quizActivo.respondida) return;
    quizActivo.respondida = true;
    detenerTimer();

    const p = quizActivo.cola[quizActivo.actual];
    const seleccion = btn.dataset.valor;
    const correcto = seleccion === p.correcta;

    bloquearBotones();
    btn.classList.add(correcto ? 'correcto' : 'incorrecto');

    if (!correcto) {
        document.querySelectorAll('.opcion-btn').forEach(b => {
            if (b.dataset.valor === p.correcta) b.classList.add('correcto');
        });
    }

    if (correcto) {
        quizActivo.aciertos++;
        quizActivo.racha_act++;
        if (quizActivo.racha_act > quizActivo.racha_max) {
            quizActivo.racha_max = quizActivo.racha_act;
        }
        mostrarFeedback(true, '✅ ¡Correcto!');
    } else {
        quizActivo.fallos++;
        quizActivo.racha_act = 0;
        mostrarFeedback(false, `❌ ${p.correcta}`);
    }

    setTimeout(avanzarPregunta, 1500);
}

function bloquearBotones() {
    document.querySelectorAll('.opcion-btn').forEach(b => b.disabled = true);
}

function avanzarPregunta() {
    quizActivo.actual++;
    mostrarPregunta();
}

function mostrarFeedback(esCorrecto, mensaje) {
    const fb = document.getElementById('quizFeedback');
    fb.textContent = mensaje;
    fb.className = 'quiz-feedback';
    fb.classList.add(esCorrecto ? 'feedback-correcto' : 'feedback-incorrecto');
    fb.classList.remove('hidden');
}

function finalizarQuiz() {
    detenerTimer();

    const total = quizActivo.aciertos + quizActivo.fallos;
    const porcentaje = total > 0 ? Math.round((quizActivo.aciertos / total) * 100) : 0;

    document.getElementById('quizJuego').classList.add('hidden');

    let mensaje, emoji;
    if (porcentaje === 100) { mensaje = '¡Perfecto! Eres un verdadero naturalista'; emoji = '🏆'; }
    else if (porcentaje >= 80) { mensaje = '¡Excelente trabajo!'; emoji = '🌟'; }
    else if (porcentaje >= 60) { mensaje = 'Buen conocimiento'; emoji = '👍'; }
    else if (porcentaje >= 40) { mensaje = 'Sigue practicando'; emoji = '📚'; }
    else { mensaje = 'Necesitas explorar más especies'; emoji = '🔍'; }

    document.getElementById('quizResultados').innerHTML = `
        <div class="resultados-quiz">
            <div class="resultado-emoji">${emoji}</div>
            <h2 style="color:#f8fafc;margin-bottom:1rem;">${mensaje}</h2>
            <div class="resultado-stats">
                <div class="stat-item"><span class="stat-num">${quizActivo.aciertos}</span><span class="stat-label">Aciertos</span></div>
                <div class="stat-item"><span class="stat-num">${quizActivo.fallos}</span><span class="stat-label">Fallos</span></div>
                <div class="stat-item"><span class="stat-num">${porcentaje}%</span><span class="stat-label">Precisión</span></div>
                <div class="stat-item"><span class="stat-num">${quizActivo.racha_max}</span><span class="stat-label">Racha máx</span></div>
            </div>
            <button class="btn-guardar" onclick="cerrarQuiz()">Continuar</button>
        </div>
    `;
    document.getElementById('quizResultados').classList.remove('hidden');

    const puntosGanados = quizActivo.aciertos * 3 + (quizActivo.racha_max >= 5 ? 10 : 0);
    estadoPerfil.puntos += puntosGanados;

    if (quizActivo.racha_max > estadoPerfil.racha_maxima) {
        estadoPerfil.racha_maxima = quizActivo.racha_max;
    }

    if (quizActivo.racha_max >= 10) {
        estadoPerfil.badge_oro = true;
        document.getElementById('badgeOro').classList.add('unlocked');
    }

    const nuevasClases = new Set(favoritosLocales.map(a => a.clase)).size;
    if (nuevasClases >= 5) {
        estadoPerfil.badge_diversidad = true;
        document.getElementById('badgeDiversidad').classList.add('unlocked');
    }

    const nuevoR = [...RANGOS].reverse().find(r => estadoPerfil.puntos >= r.min);
    if (nuevoR) estadoPerfil.rango_titulo = nuevoR.t;

    actualizarUI();
    sincronizar();
}

window.cerrarQuiz = () => {
    detenerTimer();
    document.getElementById('quizModal').classList.add('hidden');
    document.getElementById('quizResultados').classList.add('hidden');
    document.getElementById('quizJuego').classList.remove('hidden');
    quizActivo = null;
};

/* --- INICIALIZACIÓN --- */
document.getElementById('buscarBtn').onclick = buscarAnimal;
document.getElementById('guardarBtn').onclick = guardar;
document.querySelector('.close-modal').onclick = cerrarQuiz;

// Cargar datos iniciales
cargarPerfil();
cargarFavoritos();