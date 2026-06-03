const STORAGE_KEY = "gideao-ai-memories";

const AUTOMATIONS = [
  {
    title: "Abrir app favorito",
    description: "Simula abrir WhatsApp, navegador ou bloco de notas pelo comando do usuário.",
    safe: true,
    result: "App favorito localizado. No Android, isso usaria Intent/launcher com confirmação visual.",
  },
  {
    title: "Organizar arquivos",
    description: "Agrupa downloads por imagens, PDFs, documentos e instaladores.",
    safe: true,
    result: "Arquivos classificados em categorias. Antes de mover ou excluir algo importante, eu pediria confirmação.",
  },
  {
    title: "Preencher formulário",
    description: "Detecta nome, email, telefone, CPF e endereço.",
    safe: false,
    result: "Campos detectados. Dados sensíveis só seguem depois da sua confirmação explícita.",
  },
  {
    title: "Enviar senha",
    description: "Exemplo bloqueado por segurança.",
    safe: false,
    blocked: true,
    result: "Bloqueado: nunca envio senha automaticamente sem confirmação explícita.",
  },
];

const DEFAULT_PROFILE = {
  name: "Usuário Gideão",
  email: "usuario@email.com",
  phone: "(11) 90000-0000",
  cpf: "000.000.000-00",
  address: "Rua Exemplo, 123 - Centro",
};

const state = {
  memories: [],
  recognition: null,
  listening: false,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

function loadMemories() {
  try {
    state.memories = JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    state.memories = [];
  }
}

function persistMemories() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.memories));
}

function speak(text) {
  if (!("speechSynthesis" in window)) {
    return;
  }

  speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "pt-BR";
  utterance.rate = 1;
  utterance.pitch = 1;
  speechSynthesis.speak(utterance);
}

function setResponse(text, intent = "Resposta") {
  $("#assistant-response").textContent = text;
  $("#intent-pill").textContent = intent;
  addLog(intent, text);
  speak(text);
}

function addLog(label, text) {
  const item = document.createElement("div");
  item.className = "log-item";
  item.innerHTML = `<strong>${label}</strong><span>${text}</span>`;
  $("#conversation-log").prepend(item);
}

function normalize(text) {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

function extractMemory(command) {
  const patterns = ["lembre que", "memorize que", "guarde que", "salve que"];
  const normalized = normalize(command);
  const pattern = patterns.find((item) => normalized.includes(item));

  if (!pattern) {
    return "";
  }

  const index = normalized.indexOf(pattern) + pattern.length;
  return command.slice(index).trim().replace(/^[,.:;-]+/, "").trim();
}

function detectIntent(command) {
  const normalized = normalize(command);

  if (["senha", "transferencia", "compra", "excluir arquivo", "apagar arquivo"].some((word) => normalized.includes(word))) {
    return "seguranca";
  }

  if (["lembre", "memorize", "guarde", "salve"].some((word) => normalized.includes(word))) {
    return "memoria";
  }

  if (["estudo", "concurso", "cronograma", "simulado", "resumo", "questao"].some((word) => normalized.includes(word))) {
    return "estudos";
  }

  if (["pesquise", "pesquisar", "compare", "gratuito", "custo-beneficio"].some((word) => normalized.includes(word))) {
    return "pesquisa";
  }

  if (["preencher", "cadastro", "cpf", "email", "telefone", "formulario"].some((word) => normalized.includes(word))) {
    return "autofill";
  }

  if (["abrir", "organizar", "copiar", "automatizar", "app"].some((word) => normalized.includes(word))) {
    return "automacao";
  }

  return "geral";
}

function runCommand() {
  const command = $("#command-input").value.trim();
  if (!command) {
    setResponse("Mande um comando primeiro. Pode ser informal, do jeito que você falaria comigo.", "Aguardando");
    return;
  }

  addLog("Você", command);
  const intent = detectIntent(command);

  if (intent === "seguranca") {
    requestConfirmation(
      "Ação sensível detectada",
      "Transferências, compras, exclusão de arquivos importantes e envio de senhas exigem confirmação explícita. Deseja apenas registrar essa intenção como tarefa pendente?",
    ).then((confirmed) => {
      const response = confirmed
        ? "Registrado como tarefa pendente. Não executei a ação sensível."
        : "Perfeito. A ação foi bloqueada e nada foi executado.";
      setResponse(response, "Segurança");
    });
    return;
  }

  if (intent === "memoria") {
    const memory = extractMemory(command) || command;
    saveMemory("preferencias", memory, true);
    setResponse(`Memória salva: ${memory}. Vou usar isso para personalizar respostas futuras.`, "Memória");
    return;
  }

  if (intent === "estudos") {
    const topic = command.replace(/gideão|gideao|monte|crie|um|uma|cronograma|plano|de|estudos/gi, "").trim();
    if (topic.length > 6) {
      $("#study-topic").value = topic;
    }
    buildStudyPlan();
    setResponse("Montei um cronograma adaptado com explicação, prática, simulado curto e revisão ativa.", "Estudos");
    document.querySelector("#estudos").scrollIntoView({ behavior: "smooth" });
    return;
  }

  if (intent === "pesquisa") {
    $("#research-topic").value = command.replace(/pesquise|pesquisar|compare/gi, "").trim() || $("#research-topic").value;
    runResearch();
    setResponse("Comparei opções começando pelas gratuitas e depois listei uma alternativa custo-benefício.", "Pesquisa");
    document.querySelector("#seguranca").scrollIntoView({ behavior: "smooth" });
    return;
  }

  if (intent === "autofill") {
    detectFields();
    setResponse("Detectei campos de cadastro. Nome, email, telefone e endereço podem ser sugeridos; CPF exige confirmação antes de envio.", "Autofill");
    document.querySelector("#automacao").scrollIntoView({ behavior: "smooth" });
    return;
  }

  if (intent === "automacao") {
    setResponse("Posso abrir apps, organizar arquivos, ler a tela e repetir tarefas. Para ações destrutivas, eu paro e peço confirmação.", "Automação");
    document.querySelector("#automacao").scrollIntoView({ behavior: "smooth" });
    return;
  }

  const memoryHint = state.memories[0] ? ` Lembro também que ${state.memories[0].value}.` : "";
  setResponse(`Entendi. Vou ser objetivo: divida isso em uma próxima ação pequena, execute agora e me peça para acompanhar.${memoryHint}`, "Geral");
}

function saveMemory(type, value, important) {
  if (!value.trim()) {
    return;
  }

  state.memories.unshift({
    id: crypto.randomUUID ? crypto.randomUUID() : String(Date.now()),
    type,
    value: value.trim(),
    important,
    createdAt: new Date().toLocaleString("pt-BR"),
  });
  persistMemories();
  renderMemories();
}

function renderMemories() {
  const container = $("#memory-list");
  container.innerHTML = "";
  $("#memory-count").textContent = `${state.memories.length} memória${state.memories.length === 1 ? "" : "s"}`;

  if (!state.memories.length) {
    container.innerHTML = `<p class="empty-state">Nenhuma memória salva ainda. Adicione preferências ou use um comando começando com "lembre que".</p>`;
    return;
  }

  state.memories.forEach((memory) => {
    const item = document.createElement("article");
    item.className = "memory-item";
    item.innerHTML = `
      <div>
        <span>${memory.type}</span>
        <p>${memory.value}</p>
        <small>${memory.important ? "Importante" : "Normal"} • ${memory.createdAt}</small>
      </div>
    `;

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "ghost-button small";
    removeButton.textContent = "Remover";
    removeButton.addEventListener("click", () => removeMemory(memory.id));
    item.append(removeButton);
    container.append(item);
  });
}

async function removeMemory(id) {
  const memory = state.memories.find((item) => item.id === id);
  if (!memory) {
    return;
  }

  if (memory.important) {
    const confirmed = await requestConfirmation("Apagar memória importante?", `"${memory.value}" parece relevante. Confirme para remover.`);
    if (!confirmed) {
      setResponse("Memória preservada. Não apaguei nada.", "Memória");
      return;
    }
  }

  state.memories = state.memories.filter((item) => item.id !== id);
  persistMemories();
  renderMemories();
  setResponse("Memória removida com segurança.", "Memória");
}

function buildStudyPlan() {
  const topic = $("#study-topic").value.trim() || "conteúdo principal";
  const level = $("#study-level").value;
  const minutes = Number($("#study-minutes").value);
  const blocks = [
    { pct: 0.18, title: "Aquecimento", text: `Releia conceitos base de ${topic} e anote 3 dúvidas.` },
    { pct: 0.28, title: "Aula guiada", text: `Estude passo a passo no nível ${level}, com exemplos resolvidos.` },
    { pct: 0.3, title: "Questões", text: "Resolva questões curtas, marque erros e explique o raciocínio em voz alta." },
    { pct: 0.14, title: "Resumo ativo", text: "Crie um resumo de 5 linhas sem copiar material." },
    { pct: 0.1, title: "Revisão", text: "Agende revisão para amanhã e transforme erros em cartões." },
  ];

  $("#study-plan").innerHTML = blocks
    .map((block) => {
      const blockMinutes = Math.max(3, Math.round(minutes * block.pct));
      return `<li><strong>${blockMinutes} min • ${block.title}</strong><span>${block.text}</span></li>`;
    })
    .join("");
}

function renderAutomations() {
  const container = $("#automation-actions");
  container.innerHTML = "";

  AUTOMATIONS.forEach((automation) => {
    const button = document.createElement("button");
    button.type = "button";
    button.innerHTML = `<strong>${automation.title}</strong><span>${automation.description}</span>`;
    button.addEventListener("click", () => runAutomation(automation));
    container.append(button);
  });
}

async function runAutomation(automation) {
  if (!automation.safe) {
    const confirmed = await requestConfirmation("Confirmar automação sensível", `${automation.description} Confirma que deseja simular essa etapa?`);
    if (!confirmed) {
      $("#automation-feedback").textContent = "Automação cancelada. Nenhum dado sensível foi enviado.";
      $("#automation-feedback").className = "feedback success";
      return;
    }
  }

  $("#automation-feedback").textContent = automation.result;
  $("#automation-feedback").className = automation.blocked ? "feedback error" : "feedback success";
}

async function detectFields() {
  const form = $("#autofill-form");
  form.elements.name.value = DEFAULT_PROFILE.name;
  form.elements.email.value = DEFAULT_PROFILE.email;
  form.elements.phone.value = DEFAULT_PROFILE.phone;
  form.elements.address.value = DEFAULT_PROFILE.address;

  const confirmed = await requestConfirmation("Preencher CPF?", "CPF é dado sensível. Confirme para inserir no campo de demonstração.");
  form.elements.cpf.value = confirmed ? DEFAULT_PROFILE.cpf : "";
  $("#autofill-feedback").textContent = confirmed
    ? "Campos preenchidos com CPF confirmado. Antes de enviar, vou pedir confirmação novamente."
    : "Campos comuns preenchidos. CPF ficou vazio porque não houve confirmação.";
  $("#autofill-feedback").className = "feedback success";
}

async function submitAutofill(event) {
  event.preventDefault();
  const confirmed = await requestConfirmation("Enviar cadastro de exemplo?", "Este formulário contém dados pessoais. Confirme explicitamente para simular o envio.");
  $("#autofill-feedback").textContent = confirmed
    ? "Envio simulado com confirmação explícita. Nenhuma informação saiu do navegador."
    : "Envio cancelado. Os dados não foram enviados.";
  $("#autofill-feedback").className = confirmed ? "feedback success" : "feedback error";
}

function analyzeScreen() {
  const findings = [
    "Botão principal encontrado: Entrar.",
    "Botão alternativo encontrado: Continuar com Google.",
    "Campo sensível encontrado: CPF. Requer confirmação antes de preencher.",
    "Sugestão: conferir se o site é confiável antes de inserir dados pessoais.",
  ];

  $("#screen-findings").innerHTML = findings.map((finding) => `<li>${finding}</li>`).join("");
  setResponse("Analisei a tela simulada e identifiquei botões, opção de login e campo sensível de CPF.", "Visão de tela");
}

function runResearch() {
  const topic = $("#research-topic").value.trim() || "solução solicitada";
  const results = [
    {
      title: "Opção gratuita",
      badge: "Prioridade",
      text: `Comece com ferramentas grátis para ${topic}. Vantagem: custo zero. Desvantagem: pode exigir configuração manual.`,
    },
    {
      title: "Opção custo-benefício",
      badge: "Equilíbrio",
      text: "Escolha um app pago barato só se economizar tempo real ou integrar melhor com Android e PC.",
    },
    {
      title: "Critério do Gideão",
      badge: "Decisão",
      text: "Compare privacidade, exportação de dados, notificações, uso offline e suporte a automação.",
    },
  ];

  $("#research-results").innerHTML = results
    .map(
      (result) => `
        <div class="comparison-item">
          <span>${result.badge}</span>
          <strong>${result.title}</strong>
          <p>${result.text}</p>
        </div>
      `,
    )
    .join("");
}

function requestConfirmation(title, message) {
  const dialog = $("#confirm-dialog");
  $("#confirm-title").textContent = title;
  $("#confirm-message").textContent = message;

  if (!dialog.showModal) {
    return Promise.resolve(window.confirm(`${title}\n\n${message}`));
  }

  dialog.showModal();
  return new Promise((resolve) => {
    const handleClose = () => {
      dialog.removeEventListener("close", handleClose);
      resolve(dialog.returnValue === "confirm");
    };
    dialog.addEventListener("close", handleClose);
  });
}

function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    $("#voice-toggle").disabled = true;
    $("#voice-toggle").textContent = "Voz indisponível";
    $("#voice-status").textContent = "Seu navegador não expôs reconhecimento de voz. Use comandos por texto.";
    return;
  }

  state.recognition = new SpeechRecognition();
  state.recognition.lang = "pt-BR";
  state.recognition.continuous = true;
  state.recognition.interimResults = false;

  state.recognition.addEventListener("result", (event) => {
    const transcript = event.results[event.results.length - 1][0].transcript;
    $("#command-input").value = transcript;
    $("#voice-status").textContent = `Ouvi: "${transcript}"`;
    runCommand();
  });

  state.recognition.addEventListener("end", () => {
    if (state.listening) {
      state.recognition.start();
    }
  });
}

function toggleListening() {
  if (!state.recognition) {
    return;
  }

  state.listening = !state.listening;
  if (state.listening) {
    state.recognition.start();
    $("#voice-toggle").textContent = "Parar escuta";
    $("#voice-status").textContent = "Escutando em português do Brasil.";
  } else {
    state.recognition.stop();
    $("#voice-toggle").textContent = "Ativar escuta";
    $("#voice-status").textContent = "Escuta pausada.";
  }
}

function bindEvents() {
  $("#run-command").addEventListener("click", runCommand);
  $("#voice-toggle").addEventListener("click", toggleListening);
  $("#speak-intro").addEventListener("click", () => {
    speak("Olá, eu sou o Gideão AI. Posso ajudar com estudos, automação, pesquisa, memória e produtividade.");
  });
  $("#save-memory").addEventListener("click", () => {
    saveMemory($("#memory-type").value, $("#memory-value").value, $("#memory-important").checked);
    $("#memory-value").value = "";
    setResponse("Memória salva com sucesso. Vou usar isso para personalizar sua experiência.", "Memória");
  });
  $("#study-minutes").addEventListener("input", (event) => {
    $("#study-minutes-value").textContent = event.target.value;
  });
  $("#build-study-plan").addEventListener("click", buildStudyPlan);
  $("#detect-fields").addEventListener("click", detectFields);
  $("#autofill-form").addEventListener("submit", submitAutofill);
  $("#analyze-screen").addEventListener("click", analyzeScreen);
  $("#run-research").addEventListener("click", runResearch);

  $$("[data-scroll]").forEach((button) => {
    button.addEventListener("click", () => document.querySelector(button.dataset.scroll).scrollIntoView({ behavior: "smooth" }));
  });

  $$(".quick-command-grid button").forEach((button) => {
    button.addEventListener("click", () => {
      $("#command-input").value = button.dataset.command;
      runCommand();
    });
  });
}

function init() {
  loadMemories();
  renderMemories();
  renderAutomations();
  buildStudyPlan();
  runResearch();
  setupSpeechRecognition();
  bindEvents();
}

document.addEventListener("DOMContentLoaded", init);
