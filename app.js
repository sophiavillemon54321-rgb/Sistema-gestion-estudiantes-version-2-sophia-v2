
const API = "http://localhost:5000/api";

let token = localStorage.getItem("token");
let usuario = JSON.parse(localStorage.getItem("usuario") || "null");
let paginaActual = 1;
let temporizadorBusqueda;

const $ = id => document.getElementById(id);

function notificar(mensaje, error = false) {
    const toast = $("toast");
    toast.textContent = mensaje;
    toast.className = error ? "error" : "";
    toast.style.display = "block";

    setTimeout(() => {
        toast.style.display = "none";
    }, 3500);
}

function mostrarPanel() {
    const conectado = Boolean(token && usuario);

    $("autenticacion").hidden = conectado;
    $("dashboard").hidden = !conectado;

    if (conectado) {
        $("bienvenida").textContent =
            `Bienvenido, ${usuario.username} (${usuario.rol})`;
        cargarEstudiantes();
        cargarEstadisticas();
    }
}

async function peticion(ruta, metodo = "GET", datos = null) {
    const headers = {};

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    if (datos !== null) {
        headers["Content-Type"] = "application/json";
    }

    let respuesta;

    try {
        respuesta = await fetch(API + ruta, {
            method: metodo,
            headers,
            body: datos === null ? null : JSON.stringify(datos)
        });
    } catch {
        throw new Error(
            "No se pudo conectar con el servidor Flask"
        );
    }

    const resultado = await respuesta.json();

    if (!respuesta.ok) {
        if (respuesta.status === 401 && token) {
            cerrarSesionLocal();
        }

        let mensaje = resultado.error || "Ocurrió un error";

        if (resultado.campos) {
            mensaje += ": " +
                Object.values(resultado.campos).join(", ");
        }

        throw new Error(mensaje);
    }

    return resultado;
}

// AUTENTICACIÓN

$("loginForm").addEventListener("submit", async e => {
    e.preventDefault();

    const datos = {
        username: $("username").value.trim(),
        password: $("password").value
    };

    try {
        const resultado = await peticion(
            "/auth/login", "POST", datos
        );

        token = resultado.token;
        usuario = resultado.usuario;

        localStorage.setItem("token", token);
        localStorage.setItem(
            "usuario", JSON.stringify(usuario)
        );

        $("loginForm").reset();
        mostrarPanel();
        notificar("Inicio de sesión exitoso");
    } catch (error) {
        notificar(error.message, true);
    }
});

// REGISTRO

$("registroForm").addEventListener("submit", async e => {
    e.preventDefault();

    const datos = {
        username: $("regUsername").value.trim(),
        email: $("regEmail").value.trim(),
        password: $("regPassword").value
    };

    try {
        await peticion("/auth/registro", "POST", datos);

        $("registroForm").reset();
        notificar(
            "Usuario registrado. Ahora inicia sesión."
        );
    } catch (error) {
        notificar(error.message, true);
    }
});

// CERRAR SESIÓN

function cerrarSesionLocal() {
    token = null;
    usuario = null;

    localStorage.removeItem("token");
    localStorage.removeItem("usuario");

    $("dashboard").hidden = true;
    $("autenticacion").hidden = false;
}

$("logoutBtn").addEventListener("click", async () => {
    try {
        await peticion("/auth/logout", "POST");
    } catch (error) {
        console.error(error);
    }

    cerrarSesionLocal();
    notificar("Sesión cerrada");
});

// LISTAR ESTUDIANTES

async function cargarEstudiantes() {
    const parametros = new URLSearchParams({
        page: paginaActual,
        per_page: 5,
        search: $("busqueda").value.trim(),
        orden: $("orden").value,
        direccion: $("direccion").value
    });

    try {
        const datos = await peticion(
            "/estudiantes?" + parametros
        );

        const tabla = $("tablaEstudiantes");
        tabla.replaceChildren();

        if (datos.estudiantes.length === 0) {
            const fila = tabla.insertRow();
            const celda = fila.insertCell();
            celda.colSpan = 7;
            celda.textContent = "No hay estudiantes";
        }

        datos.estudiantes.forEach(est => {
            const fila = tabla.insertRow();

            [
                est.id,
                est.nombre,
                est.apellido,
                est.edad,
                est.carrera,
                est.email
            ].forEach(valor => {
                const celda = fila.insertCell();
                celda.textContent = valor ?? "";
            });

            const acciones = fila.insertCell();

            const editar = document.createElement("button");
            editar.textContent = "Editar";
            editar.addEventListener(
                "click", () => editarEstudiante(est.id)
            );
            acciones.appendChild(editar);

            if (usuario && usuario.rol === "admin") {
                const eliminar = document.createElement("button");
                eliminar.textContent = "Eliminar";
                eliminar.className = "btn-eliminar";
                eliminar.addEventListener(
                    "click", () => eliminarEstudiante(est.id)
                );
                acciones.appendChild(eliminar);
            }
        });

        mostrarPaginacion(datos.paginacion);
    } catch (error) {
        notificar(error.message, true);
    }
}

// PAGINACIÓN

function mostrarPaginacion(info) {
    const contenedor = $("paginacion");
    contenedor.replaceChildren();

    const anterior = document.createElement("button");
    anterior.textContent = "Anterior";
    anterior.disabled = !info.has_prev;

    anterior.onclick = () => {
        paginaActual--;
        cargarEstudiantes();
    };

    const texto = document.createElement("span");
    texto.textContent =
        `Página ${info.page} de ${info.total_pages || 1}`;

    const siguiente = document.createElement("button");
    siguiente.textContent = "Siguiente";
    siguiente.disabled = !info.has_next;

    siguiente.onclick = () => {
        paginaActual++;
        cargarEstudiantes();
    };

    contenedor.append(anterior, texto, siguiente);
}

// CREAR Y ACTUALIZAR

$("estudianteForm").addEventListener("submit", async e => {
    e.preventDefault();

    const id = $("estudianteId").value;

    const datos = {
        nombre: $("nombre").value.trim(),
        apellido: $("apellido").value.trim(),
        edad: Number($("edad").value),
        carrera: $("carrera").value.trim(),
        email: $("email").value.trim(),
        telefono: $("telefono").value.trim()
    };

    try {
        if (id) {
            await peticion(
                `/estudiantes/${id}`, "PUT", datos
            );
            notificar("Estudiante actualizado");
        } else {
            await peticion(
                "/estudiantes", "POST", datos
            );
            notificar("Estudiante registrado");
        }

        limpiarFormulario();
        cargarEstudiantes();
        cargarEstadisticas();
    } catch (error) {
        notificar(error.message, true);
    }
});

// EDITAR

async function editarEstudiante(id) {
    try {
        const est = await peticion(`/estudiantes/${id}`);

        $("estudianteId").value = est.id;
        $("nombre").value = est.nombre;
        $("apellido").value = est.apellido;
        $("edad").value = est.edad;
        $("carrera").value = est.carrera;
        $("email").value = est.email;
        $("telefono").value = est.telefono || "";

        $("estudianteForm").scrollIntoView({
            behavior: "smooth"
        });
    } catch (error) {
        notificar(error.message, true);
    }
}

// ELIMINAR

async function eliminarEstudiante(id) {
    if (!confirm("¿Deseas eliminar este estudiante?")) {
        return;
    }

    try {
        await peticion(`/estudiantes/${id}`, "DELETE");

        notificar("Estudiante eliminado");
        cargarEstudiantes();
        cargarEstadisticas();
    } catch (error) {
        notificar(error.message, true);
    }
}

// LIMPIAR FORMULARIO

function limpiarFormulario() {
    $("estudianteForm").reset();
    $("estudianteId").value = "";
}

$("cancelarBtn").addEventListener(
    "click", limpiarFormulario
);

// BÚSQUEDA CON DEBOUNCE

$("busqueda").addEventListener("input", () => {
    clearTimeout(temporizadorBusqueda);

    temporizadorBusqueda = setTimeout(() => {
        paginaActual = 1;
        cargarEstudiantes();
    }, 400);
});

// ORDENAMIENTO

$("orden").addEventListener("change", () => {
    paginaActual = 1;
    cargarEstudiantes();
});

$("direccion").addEventListener("change", () => {
    paginaActual = 1;
    cargarEstudiantes();
});

// ESTADÍSTICAS

async function cargarEstadisticas() {
    try {
        const datos = await peticion(
            "/estudiantes/stats/general"
        );

        const contenedor = $("estadisticas");
        contenedor.replaceChildren();

        const indicadores = [
            ["Total estudiantes", datos.total_estudiantes],
            ["Promedio de edad", datos.promedio_edad ?? 0],
            ["Edad mínima", datos.edad_minima ?? 0],
            ["Edad máxima", datos.edad_maxima ?? 0]
        ];

        indicadores.forEach(([titulo, valor]) => {
            const tarjeta = document.createElement("div");
            tarjeta.className = "stat-card";

            const etiqueta = document.createElement("span");
            etiqueta.textContent = titulo;

            const numero = document.createElement("strong");
            numero.textContent = valor;

            tarjeta.append(etiqueta, numero);
            contenedor.appendChild(tarjeta);
        });

        datos.estudiantes_por_carrera.forEach(carrera => {
            const tarjeta = document.createElement("div");
            tarjeta.className = "stat-card";

            const etiqueta = document.createElement("span");
            etiqueta.textContent = carrera.carrera;

            const numero = document.createElement("strong");
            numero.textContent = carrera.cantidad;

            tarjeta.append(etiqueta, numero);
            contenedor.appendChild(tarjeta);
        });
    } catch (error) {
        notificar(error.message, true);
    }
}

// INICIAR APLICACIÓN

mostrarPanel();
