const NOTE_NAMES = ["Dó", "Ré", "Mi", "Fá", "Sol", "Lá", "Si"];
const MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11, 12];
const INTERVALS = [
  { name: "2ª menor", semitones: 1, tip: "Soa apertada e tensa, como notas vizinhas." },
  { name: "2ª maior", semitones: 2, tip: "Pense no começo de uma escala maior: dó-ré." },
  { name: "3ª menor", semitones: 3, tip: "Cor triste, muito comum em blues e rock." },
  { name: "3ª maior", semitones: 4, tip: "Cor aberta e estável, como o arpejo maior." },
  { name: "4ª justa", semitones: 5, tip: "Salto forte, com sensação de chamada." },
  { name: "5ª justa", semitones: 7, tip: "Som amplo e estável, base dos power chords." },
  { name: "6ª maior", semitones: 9, tip: "Salto cantável e melodioso." },
  { name: "8ª justa", semitones: 12, tip: "Mesma nota em outra altura." },
];

const PHRASES = [
  {
    name: "Pergunta e resposta",
    description: "Duas ideias: a primeira fica suspensa e a segunda resolve no grau 1.",
    degrees: [1, 2, 3, 5, 4, 3, 2, 1],
    rhythm: [0.35, 0.35, 0.35, 0.7, 0.35, 0.35, 0.35, 0.9],
  },
  {
    name: "Sequência melódica",
    description: "O mesmo desenho sobe por partes da escala.",
    degrees: [1, 2, 3, 2, 3, 4, 5, 4, 5, 6],
    rhythm: [0.28, 0.28, 0.44, 0.28, 0.28, 0.44, 0.28, 0.28, 0.44, 0.7],
  },
  {
    name: "Pedal point",
    description: "Uma nota fixa retorna entre notas móveis para criar tensão e energia.",
    degrees: [1, 5, 1, 6, 1, 5, 1, 4, 1],
    rhythm: [0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.6],
  },
  {
    name: "Aproximação cromática",
    description: "Uma nota alvo é cercada por vizinhos cromáticos antes de resolver.",
    semitones: [0, 4, 3, 5, 4, 7, 6, 8, 7],
    rhythm: [0.3, 0.3, 0.2, 0.2, 0.48, 0.3, 0.2, 0.2, 0.7],
  },
];

const TECHNIQUES = [
  {
    title: "Pedal point",
    summary: "Mantenha uma nota pedal e alterne com notas da escala para criar tensão no improviso.",
    degrees: [1, 5, 1, 6, 1, 7, 1, 8],
    tab: `e|--8--12--8--13--8--15--8--17--|
B|----------------------------------|
G|----------------------------------|`,
    practice: "Toque lento, acentue sempre a nota pedal e depois mude o pedal para outro grau.",
  },
  {
    title: "Padrão 1-2-3",
    summary: "Sequência simples para conectar regiões da escala sem soar como exercício mecânico.",
    degrees: [1, 2, 3, 2, 3, 4, 3, 4, 5, 4, 5, 6],
    tab: `e|-------------------------5--7--8--|
B|-------------5--6--8--------------|
G|--4--5--7-------------------------|`,
    practice: "Suba em grupos de três e termine cada grupo em uma nota do acorde.",
  },
  {
    title: "Aproximação cromática",
    summary: "Cerque a nota alvo por meio tom abaixo ou acima para soar mais jazz/blues.",
    semitones: [0, 4, 3, 5, 4, 7, 6, 8, 7, 12],
    tab: `e|------------------7--8--|
B|---------7--8--9--------|
G|--5--6------------------|`,
    practice: "Escolha uma nota alvo do acorde e resolva nela com convicção rítmica.",
  },
  {
    title: "Motivo rítmico",
    summary: "Repita a mesma célula rítmica em notas diferentes para criar fraseado memorável.",
    degrees: [1, 3, 2, 1, 4, 6, 5, 4, 5, 7, 6, 5],
    rhythm: [0.2, 0.2, 0.45, 0.55, 0.2, 0.2, 0.45, 0.55, 0.2, 0.2, 0.45, 0.8],
    tab: `e|-------------------5--7--5--|
B|--------5--6--5-------------|
G|--5--7----------------------|`,
    practice: "Mantenha a célula rítmica e varie apenas as notas.",
  },
];

let audioContext;
let activeDrone;

const state = {
  interval: null,
  melody: [],
  melodyAnswer: [],
  phrase: null,
  scores: {
    interval: { right: 0, total: 0 },
    melody: { right: 0, total: 0 },
    phrase: { right: 0, total: 0 },
  },
};

const $ = (selector) => document.querySelector(selector);

function ensureAudio() {
  if (!audioContext) {
    audioContext = new AudioContext();
  }

  if (audioContext.state === "suspended") {
    audioContext.resume();
  }

  $("#audio-status").textContent = "Áudio ativo. Use fones para perceber melhor os detalhes.";
  return audioContext;
}

function frequencyFromSemitone(baseFrequency, semitone) {
  return baseFrequency * 2 ** (semitone / 12);
}

function getSelectedRoot() {
  return Number($("#key-select").value);
}

function getTempoSeconds(multiplier = 1) {
  return (60 / Number($("#tempo-range").value)) * multiplier;
}

function playTone(frequency, startTime, duration, options = {}) {
  const context = ensureAudio();
  const oscillator = context.createOscillator();
  const gain = context.createGain();
  const filter = context.createBiquadFilter();

  oscillator.type = options.type || "triangle";
  oscillator.frequency.setValueAtTime(frequency, startTime);
  filter.type = "lowpass";
  filter.frequency.setValueAtTime(options.filter || 1400, startTime);

  gain.gain.setValueAtTime(0.0001, startTime);
  gain.gain.exponentialRampToValueAtTime(options.volume || 0.22, startTime + 0.025);
  gain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

  oscillator.connect(filter);
  filter.connect(gain);
  gain.connect(context.destination);

  oscillator.start(startTime);
  oscillator.stop(startTime + duration + 0.03);
}

function playSequence(items, options = {}) {
  const context = ensureAudio();
  const root = options.root || getSelectedRoot();
  let time = context.currentTime + 0.05;
  const beat = getTempoSeconds();

  items.forEach((item, index) => {
    const semitone = item.semitone ?? MAJOR_SCALE[item.degree - 1] ?? 0;
    const duration = item.duration ?? beat * 0.72;
    const pause = item.pause ?? beat * 0.08;
    const frequency = frequencyFromSemitone(root, semitone + (item.octave || 0) * 12);
    playTone(frequency, time, duration, { volume: item.volume || options.volume, type: options.type });
    time += duration + pause;

    if (options.metronome && index % 2 === 0) {
      playTone(frequencyFromSemitone(root, -12), time - duration - pause, 0.04, {
        volume: 0.08,
        type: "square",
        filter: 800,
      });
    }
  });
}

function setFeedback(element, message, kind = "") {
  element.textContent = message;
  element.classList.remove("success", "error");
  if (kind) {
    element.classList.add(kind);
  }
}

function randomItem(items) {
  return items[Math.floor(Math.random() * items.length)];
}

function shuffle(items) {
  return [...items].sort(() => Math.random() - 0.5);
}

function updateScore(kind) {
  const score = state.scores[kind];
  $(`#${kind}-score`).textContent = `${score.right}/${score.total}`;
}

function renderIntervalOptions() {
  const container = $("#interval-options");
  container.innerHTML = "";
  INTERVALS.forEach((interval) => {
    const button = document.createElement("button");
    button.className = "option-button";
    button.type = "button";
    button.textContent = interval.name;
    button.addEventListener("click", () => checkInterval(interval, button));
    container.append(button);
  });
}

function newInterval() {
  const rootSemitone = randomItem([0, 2, 4, 5, 7]);
  state.interval = {
    root: frequencyFromSemitone(220, rootSemitone),
    interval: randomItem(INTERVALS),
  };
  playCurrentInterval();
  setFeedback($("#interval-feedback"), "Ouça, cante a segunda nota e escolha o intervalo.");
  document.querySelectorAll("#interval-options .option-button").forEach((button) => {
    button.classList.remove("correct", "wrong");
  });
}

function playCurrentInterval() {
  if (!state.interval) {
    newInterval();
    return;
  }

  const { root, interval } = state.interval;
  const context = ensureAudio();
  playTone(root, context.currentTime + 0.05, 0.55);
  playTone(frequencyFromSemitone(root, interval.semitones), context.currentTime + 0.78, 0.7);
}

function checkInterval(selected, button) {
  if (!state.interval) {
    setFeedback($("#interval-feedback"), "Toque um intervalo antes de responder.", "error");
    return;
  }

  const expected = state.interval.interval;
  const score = state.scores.interval;
  score.total += 1;

  if (selected.name === expected.name) {
    score.right += 1;
    button.classList.add("correct");
    setFeedback($("#interval-feedback"), `Correto: ${expected.name}. ${expected.tip}`, "success");
  } else {
    button.classList.add("wrong");
    setFeedback($("#interval-feedback"), `Ainda não: era ${expected.name}. ${expected.tip}`, "error");
  }

  updateScore("interval");
}

function generateMelody() {
  const start = randomItem([1, 3, 5]);
  const melody = [start];
  while (melody.length < 5) {
    const last = melody[melody.length - 1];
    const step = randomItem([-2, -1, 1, 2]);
    const next = Math.min(7, Math.max(1, last + step));
    melody.push(next);
  }
  return melody;
}

function playMelody(melody = state.melody) {
  if (!melody.length) {
    newMelody();
    return;
  }

  const items = melody.map((degree, index) => ({
    degree,
    duration: getTempoSeconds(index === melody.length - 1 ? 1.15 : 0.62),
  }));
  playSequence(items, { metronome: true });
}

function newMelody() {
  state.melody = generateMelody();
  state.melodyAnswer = [];
  renderMelodyAnswer();
  playMelody();
  setFeedback($("#melody-feedback"), "Monte a sequência usando graus 1 a 7.");
}

function renderDegreePad() {
  const container = $("#degree-pad");
  container.innerHTML = "";
  NOTE_NAMES.forEach((note, index) => {
    const degree = index + 1;
    const button = document.createElement("button");
    button.className = "degree-button";
    button.type = "button";
    button.textContent = `${degree} - ${note}`;
    button.addEventListener("click", () => {
      state.melodyAnswer.push(degree);
      renderMelodyAnswer();
    });
    container.append(button);
  });
}

function renderMelodyAnswer() {
  $("#melody-answer").textContent = state.melodyAnswer.length
    ? state.melodyAnswer.join(" - ")
    : "vazia";
}

function clearMelodyAnswer() {
  state.melodyAnswer = [];
  renderMelodyAnswer();
  setFeedback($("#melody-feedback"), "Resposta limpa. Ouça novamente se precisar.");
}

function checkMelody() {
  if (!state.melody.length) {
    setFeedback($("#melody-feedback"), "Gere uma melodia antes de conferir.", "error");
    return;
  }

  const expected = state.melody.join("-");
  const answer = state.melodyAnswer.join("-");
  const score = state.scores.melody;
  score.total += 1;

  if (answer === expected) {
    score.right += 1;
    setFeedback($("#melody-feedback"), `Correto: ${state.melody.join(" - ")}. Agora toque na guitarra.`, "success");
  } else {
    setFeedback($("#melody-feedback"), `Quase. A resposta era ${state.melody.join(" - ")}. Cante devagar e repita.`, "error");
  }

  updateScore("melody");
}

function phraseToItems(phrase) {
  if (phrase.semitones) {
    return phrase.semitones.map((semitone, index) => ({
      semitone,
      duration: getTempoSeconds(phrase.rhythm[index]),
    }));
  }

  return phrase.degrees.map((degree, index) => ({
    degree,
    duration: getTempoSeconds(phrase.rhythm[index]),
  }));
}

function playPhrase(phrase = state.phrase) {
  if (!phrase) {
    newPhrase();
    return;
  }

  playSequence(phraseToItems(phrase), { root: frequencyFromSemitone(getSelectedRoot(), 12), type: "sawtooth", volume: 0.16 });
}

function newPhrase() {
  state.phrase = randomItem(PHRASES);
  playPhrase();
  setFeedback($("#phrase-feedback"), "Escolha a intenção musical que você ouviu.");
  document.querySelectorAll("#phrase-options .option-button").forEach((button) => {
    button.classList.remove("correct", "wrong");
  });
}

function renderPhraseOptions() {
  const container = $("#phrase-options");
  container.innerHTML = "";
  shuffle(PHRASES).forEach((phrase) => {
    const button = document.createElement("button");
    button.className = "option-button";
    button.type = "button";
    button.textContent = phrase.name;
    button.addEventListener("click", () => checkPhrase(phrase, button));
    container.append(button);
  });
}

function checkPhrase(selected, button) {
  if (!state.phrase) {
    setFeedback($("#phrase-feedback"), "Toque uma frase antes de responder.", "error");
    return;
  }

  const score = state.scores.phrase;
  score.total += 1;

  if (selected.name === state.phrase.name) {
    score.right += 1;
    button.classList.add("correct");
    setFeedback($("#phrase-feedback"), `Correto: ${state.phrase.description}`, "success");
  } else {
    button.classList.add("wrong");
    setFeedback($("#phrase-feedback"), `Não foi dessa vez. Era ${state.phrase.name}: ${state.phrase.description}`, "error");
  }

  updateScore("phrase");
}

function playDrone() {
  const context = ensureAudio();
  if (activeDrone) {
    activeDrone.oscillator.stop();
    activeDrone = null;
    $("#play-drone").textContent = "Tocar drone";
    return;
  }

  const oscillator = context.createOscillator();
  const gain = context.createGain();
  oscillator.type = "sine";
  oscillator.frequency.value = getSelectedRoot();
  gain.gain.setValueAtTime(0.0001, context.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.12, context.currentTime + 0.2);
  oscillator.connect(gain);
  gain.connect(context.destination);
  oscillator.start();
  activeDrone = { oscillator, gain };
  $("#play-drone").textContent = "Parar drone";
}

function playMajorScale() {
  const degrees = [1, 2, 3, 4, 5, 6, 7, 8].map((degree) => ({
    degree,
    duration: getTempoSeconds(0.45),
  }));
  playSequence(degrees);
}

function renderTechniqueCards() {
  const container = $("#technique-grid");
  container.innerHTML = "";

  TECHNIQUES.forEach((technique) => {
    const card = document.createElement("article");
    card.className = "technique-card";
    card.innerHTML = `
      <div>
        <p class="tag">Improviso</p>
        <h3>${technique.title}</h3>
      </div>
      <p>${technique.summary}</p>
      <pre class="tab-box" aria-label="Tablatura de ${technique.title}">${technique.tab}</pre>
      <p><strong>Como praticar:</strong> ${technique.practice}</p>
    `;

    const button = document.createElement("button");
    button.className = "primary-button";
    button.type = "button";
    button.textContent = "Ouvir padrão";
    button.addEventListener("click", () => {
      const rhythm = technique.rhythm || technique.degrees?.map(() => 0.32) || technique.semitones.map(() => 0.32);
      const items = (technique.semitones || technique.degrees).map((value, index) => ({
        [technique.semitones ? "semitone" : "degree"]: value,
        duration: getTempoSeconds(rhythm[index]),
      }));
      playSequence(items, { root: frequencyFromSemitone(getSelectedRoot(), 12), type: "square", volume: 0.13 });
    });

    card.append(button);
    container.append(card);
  });
}

function bindEvents() {
  $("#audio-check").addEventListener("click", ensureAudio);
  document.querySelectorAll("[data-scroll]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelector(button.dataset.scroll).scrollIntoView({ behavior: "smooth" });
    });
  });

  $("#play-interval").addEventListener("click", newInterval);
  $("#repeat-interval").addEventListener("click", playCurrentInterval);
  $("#play-melody").addEventListener("click", newMelody);
  $("#repeat-melody").addEventListener("click", () => playMelody());
  $("#clear-melody").addEventListener("click", clearMelodyAnswer);
  $("#check-melody").addEventListener("click", checkMelody);
  $("#play-phrase").addEventListener("click", newPhrase);
  $("#repeat-phrase").addEventListener("click", () => playPhrase());
  $("#play-drone").addEventListener("click", playDrone);
  $("#play-scale").addEventListener("click", playMajorScale);
  $("#tempo-range").addEventListener("input", (event) => {
    $("#tempo-value").textContent = event.target.value;
  });
  $("#key-select").addEventListener("change", () => {
    if (activeDrone) {
      activeDrone.oscillator.frequency.setValueAtTime(getSelectedRoot(), ensureAudio().currentTime);
    }
  });
}

function init() {
  renderIntervalOptions();
  renderDegreePad();
  renderPhraseOptions();
  renderTechniqueCards();
  bindEvents();
  updateScore("interval");
  updateScore("melody");
  updateScore("phrase");
}

document.addEventListener("DOMContentLoaded", init);
