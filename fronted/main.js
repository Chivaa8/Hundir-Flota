// ====== Config ======
const API_BASE = "http://127.0.0.1:8000";
const $ = (id) => document.getElementById(id);

// ====== Puntuación visible (opción A) ======
const SCORE_BASE = {
  facil: 1200,
  normal: 1000,
  dificil: 800,
};

function normalizeScore(rawScore, difficulty) {
  const base = SCORE_BASE[difficulty] ?? 0;
  const n = Number(rawScore ?? 0) - base;
  return Math.max(0, Math.round(n));
}

// ====== Estado ======
let timerInterval = null;
let startTime = null;

const state = {
  gameId: null,
  playerName: "-",
  difficulty: "-",
  board: null,
  ended: false,
};

// ====== API helper ======
async function apiFetch(path, { method = "GET", body } = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try {
    data = await res.json();
  } catch (_) {}

  if (!res.ok) {
    const msg = data?.detail || data?.message || "Error desconocido";
    throw new Error(msg);
  }

  return data;
}

// ====== UI helpers ======
function setStats({ playerName, difficulty, shots, sunk, score }) {
  $("nombreJugadorEstadistica").textContent = playerName ?? "-";
  $("nivelDificultad").textContent = difficulty ?? "-";
  $("totalDisparos").textContent = String(shots ?? 0);
  $("barcosHundidos").textContent = String(sunk ?? 0);
  $("puntuacionActual").textContent = String(score ?? 0);
}

function setGameActive(active) {
  $("reiniciarPartida").disabled = !active;
  $("abandonarPartida").disabled = !active;
}

function mostrarMensaje(texto, tipo = "info") {
  let div = $("mensaje");
  if (!div) {
    div = document.createElement("div");
    div.id = "mensaje";
    document.body.appendChild(div);
  }
  div.className = `${tipo} visible`;
  div.textContent = texto;

  clearTimeout(div._timeout);
  div._timeout = setTimeout(() => div.classList.remove("visible"), 2500);
}

/**
 * Limpia TODO (incluye form). Úsalo cuando abandonas o vuelves a estado inicial.
 */
function limpiarInterfaz() {
  $("zonaTablero").innerHTML = "";
  $("tablero").reset();

  state.gameId = null;
  state.playerName = "-";
  state.difficulty = "-";
  state.board = null;
  state.ended = false;

  setStats({ playerName: "-", difficulty: "-", shots: 0, sunk: 0, score: 0 });
  setGameActive(false);

  stopGameTimer();
  $("tiempoPartida").textContent = "00:00";
}

/**
 * Resetea UI para NUEVA partida sin tocar el formulario.
 */
function resetUIForNewGame() {
  $("zonaTablero").innerHTML = "";
  state.board = null;
  state.ended = false;

  setStats({ playerName: "-", difficulty: "-", shots: 0, sunk: 0, score: 0 });

  stopGameTimer();
  $("tiempoPartida").textContent = "00:00";
  setGameActive(false);
}

// ====== Temporizador ======
function startGameTimer() {
  stopGameTimer();
  startTime = Date.now();

  timerInterval = setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const min = String(Math.floor(elapsed / 60)).padStart(2, "0");
    const sec = String(elapsed % 60).padStart(2, "0");
    $("tiempoPartida").textContent = `${min}:${sec}`;
  }, 1000);
}

function stopGameTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

// ====== Tablero ======
function renderBoard(board) {
  const zona = $("zonaTablero");
  zona.innerHTML = "";

  if (!Array.isArray(board) || !Array.isArray(board[0])) {
    mostrarMensaje("Tablero inválido recibido del servidor.", "error");
    return;
  }

  const grid = document.createElement("div");
  grid.className = "tablero-grid";
  grid.style.gridTemplateColumns = `repeat(${board[0].length}, 1fr)`;

  board.forEach((row, i) => {
    row.forEach((cell, j) => {
      const casilla = document.createElement("div");
      casilla.className = "casilla";

      if (cell.disparado) {
        casilla.classList.add("disparado");

        if (cell.resultado === "agua") {
          casilla.classList.add("agua");
          casilla.textContent = "•";
        } else if (cell.resultado === "tocado") {
          casilla.classList.add("tocado");
          casilla.textContent = "—";
        } else if (cell.resultado === "hundido") {
          casilla.classList.add("hundido");
          casilla.textContent = "X";
        }
      } else {
        if (state.gameId && !state.ended) {
          casilla.addEventListener("click", () => shoot(i, j));
        }
      }

      grid.appendChild(casilla);
    });
  });

  zona.appendChild(grid);
}

async function fetchBoard() {
  const data = await apiFetch(`/partida/${state.gameId}/tablero`);
  state.board = data.tablero;
  renderBoard(state.board);
}

// ====== Game actions ======
async function createGameFromForm(e) {
  e.preventDefault();

  // evitar arrastre de stats anteriores
  resetUIForNewGame();

  try {
    const filas = +$("fila").value;
    const columnas = +$("columna").value;
    const jugador = ($("nombreJugador").value || "Anónimo").trim();
    const dificultad = $("opciones").value;

    const data = await apiFetch("/partida/nueva", {
      method: "POST",
      body: { filas, columnas, jugador, dificultad },
    });

    state.gameId = data.id_juego;
    state.playerName = data.jugador;
    state.difficulty = dificultad;
    state.ended = false;

    setStats({
      playerName: state.playerName,
      difficulty: state.difficulty,
      shots: 0,
      sunk: 0,
      score: 0, // visible desde 0
    });

    setGameActive(true);
    startGameTimer();

    await fetchBoard();
    mostrarMensaje("Partida creada correctamente", "ok");
  } catch (err) {
    mostrarMensaje(err.message, "error");
  }
}

async function shoot(fila, columna) {
  if (!state.gameId || state.ended) return;

  try {
    const data = await apiFetch(`/partida/${state.gameId}/disparar`, {
      method: "POST",
      body: { fila, columna },
    });

    setStats({
      playerName: state.playerName,
      difficulty: state.difficulty,
      shots: data.total_disparos,
      sunk: data.barcos_hundidos,
      // ✅ puntuación visible (sin base)
      score: normalizeScore(data.puntuacion_parcial, state.difficulty),
    });

    state.board = data.tablero;
    renderBoard(state.board);

    if (data.estado_partida && data.estado_partida !== "en_curso") {
      state.ended = true;
      setGameActive(false);
      stopGameTimer();

      if (data.estado_partida === "ganada") {
        mostrarMensaje("¡Has ganado!", "ok");
      } else {
        mostrarMensaje("La partida ha terminado.", "error");
      }
    } else {
      if (data.resultado === "agua") mostrarMensaje("Agua.", "info");
      if (data.resultado === "tocado") mostrarMensaje("¡Tocado!", "ok");
      if (data.resultado === "hundido") mostrarMensaje("¡Hundido!", "ok");
    }
  } catch (err) {
    mostrarMensaje(err.message, "error");
  }
}

async function restartGame() {
  if (!state.gameId) return;

  try {
    const data = await apiFetch(`/partida/${state.gameId}/reiniciar`, {
      method: "POST",
    });

    state.ended = false;

    setStats({
      playerName: data.jugador,
      difficulty: state.difficulty,
      shots: 0,
      sunk: 0,
      score: 0, // visible desde 0
    });

    stopGameTimer();
    startGameTimer();

    setGameActive(true);
    await fetchBoard();
    mostrarMensaje("Partida reiniciada.", "ok");
  } catch (err) {
    mostrarMensaje(err.message, "error");
  }
}

async function abandonGame() {
  if (!state.gameId) return;

  // parar timer SIEMPRE
  stopGameTimer();

  try {
    await apiFetch(`/partida/${state.gameId}/abandonar`, {
      method: "POST",
      body: { razon: "Abandonada por el usuario" },
    });

    limpiarInterfaz();
    mostrarMensaje("Partida abandonada", "info");
  } catch (err) {
    try {
      await apiFetch(`/partida/${state.gameId}/finalizar`, { method: "POST" });
      limpiarInterfaz();
      mostrarMensaje("Partida finalizada", "info");
    } catch (err2) {
      limpiarInterfaz();
      mostrarMensaje(err2.message || err.message, "error");
    }
  }
}

// ====== Events ======
$("tablero").addEventListener("submit", createGameFromForm);

$("reiniciarPartida").addEventListener("click", () => {
  if (!state.gameId) return alert("No hay partida activa para reiniciar.");
  restartGame();
});

$("abandonarPartida").addEventListener("click", () => {
  if (!state.gameId) return alert("No hay partida activa para abandonar.");
  abandonGame();
});

// Estado inicial
setGameActive(false);
setStats({ playerName: "-", difficulty: "-", shots: 0, sunk: 0, score: 0 });
$("tiempoPartida").textContent = "00:00";
