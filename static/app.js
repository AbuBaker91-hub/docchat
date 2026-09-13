/* DocChat UI: documents + upload on the left, chat with verified-citation
   chips on the right. Vanilla JS, no build step. */

const docsEl = document.getElementById("docs");
const chatEl = document.getElementById("chat");
const fileEl = document.getElementById("file");
const uploadStatusEl = document.getElementById("upload-status");
const formEl = document.getElementById("ask");
const questionEl = document.getElementById("question");
const sendEl = document.getElementById("send");

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined) node.textContent = text;
  return node;
}

/* ---------- documents ---------- */

async function loadDocuments() {
  const res = await fetch("/documents");
  if (!res.ok) return;
  const docs = await res.json();
  docsEl.replaceChildren();
  if (!docs.length) {
    docsEl.append(el("div", "sys", "No documents yet - upload a PDF to start."));
    return;
  }
  for (const d of docs) {
    const row = el("div", "doc");
    row.append(el("span", "name", d.filename));
    const meta = el("span", "meta", `${d.pages} p `);
    const badge = el("span", `badge ${d.status}`, d.status);
    meta.append(badge);
    row.append(meta);
    docsEl.append(row);
  }
}

fileEl.addEventListener("change", async () => {
  const file = fileEl.files[0];
  if (!file) return;
  uploadStatusEl.textContent = `Uploading ${file.name}...`;
  const body = new FormData();
  body.append("file", file);
  try {
    const res = await fetch("/documents", { method: "POST", body });
    const data = await res.json();
    if (!res.ok) {
      uploadStatusEl.textContent = data.detail || "Upload failed.";
    } else {
      uploadStatusEl.textContent =
        data.status === "ready" ? `Ready: ${data.pages} pages.` : "Ingest failed.";
      await loadDocuments();
    }
  } catch {
    uploadStatusEl.textContent = "Upload failed.";
  }
  fileEl.value = "";
});

/* ---------- chat ---------- */

function confidenceBadge(conf) {
  const pct = Math.round((conf || 0) * 100);
  const cls = conf >= 0.7 ? "high" : conf >= 0.4 ? "mid" : "low";
  const wrap = el("div", "conf");
  wrap.append("confidence ");
  wrap.append(el("span", `badge ${cls}`, `${pct}%`));
  return wrap;
}

function citationChips(citations) {
  const chips = el("div", "chips");
  for (const c of citations) {
    const chip = el("button", "chip", `${c.doc} - p.${c.page}`);
    chip.type = "button";
    const quote = el("div", "quote");
    quote.append(el("div", "", `"${c.quote}"`));
    quote.append(el("div", "src", `${c.doc}, page ${c.page} - verified against the source text`));
    chip.addEventListener("click", () => quote.classList.toggle("open"));
    chips.append(chip);
    chips.append(quote);
  }
  return chips;
}

function renderAnswer(data) {
  if (data.status === "answered") {
    const msg = el("div", "msg bot");
    msg.append(el("div", "", data.answer));
    msg.append(confidenceBadge(data.confidence));
    msg.append(citationChips(data.citations));
    return msg;
  }
  if (data.status === "not_found") {
    const msg = el("div", "msg bot notfound");
    msg.append(el("div", "", "Not found in your documents. Closest passages:"));
    const passages = el("div", "passages");
    for (const p of data.closest_passages || []) {
      const box = el("div", "passage");
      box.append(el("div", "src", `${p.doc}, page ${p.page}${p.section ? " - " + p.section : ""}`));
      box.append(el("div", "", p.text.length > 320 ? p.text.slice(0, 320) + "..." : p.text));
      passages.append(box);
    }
    msg.append(passages);
    return msg;
  }
  return el("div", "msg bot", data.detail || "Something went wrong, please try again.");
}

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = questionEl.value.trim();
  if (!question) return;
  chatEl.append(el("div", "msg user", question));
  questionEl.value = "";
  sendEl.disabled = true;
  const thinking = el("div", "sys", "Retrieving and verifying...");
  chatEl.append(thinking);
  chatEl.scrollTop = chatEl.scrollHeight;
  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    thinking.remove();
    if (res.status === 429) {
      chatEl.append(el("div", "sys", "Rate limit reached - please wait a minute and try again."));
    } else {
      const data = await res.json();
      chatEl.append(res.ok ? renderAnswer(data) : el("div", "sys", data.detail || "Request failed."));
    }
  } catch {
    thinking.remove();
    chatEl.append(el("div", "sys", "Network error - is the server running?"));
  }
  sendEl.disabled = false;
  chatEl.scrollTop = chatEl.scrollHeight;
});

/* ---------- history ---------- */

async function loadHistory() {
  const res = await fetch("/questions");
  if (!res.ok) return;
  for (const q of await res.json()) {
    chatEl.append(el("div", "msg user", q.question));
    if (q.result) chatEl.append(renderAnswer(q.result));
  }
  chatEl.scrollTop = chatEl.scrollHeight;
}

loadDocuments();
loadHistory();
