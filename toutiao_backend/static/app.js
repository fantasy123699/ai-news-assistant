const text = {
  allNews: "\u5168\u90e8\u65b0\u95fb",
  unknownCategory: "\u672a\u5206\u7c7b",
  unknownAuthor: "\u672a\u77e5\u4f5c\u8005",
  noDesc: "\u6682\u65e0\u7b80\u4ecb",
  noRelated: "\u6682\u65e0\u76f8\u5173\u63a8\u8350",
  views: "\u6b21\u6d4f\u89c8",
  loginFirst: "\u8bf7\u5148\u767b\u5f55",
  loginSuccess: "\u767b\u5f55\u6210\u529f",
  registerSuccess: "\u6ce8\u518c\u6210\u529f\uff0c\u5df2\u81ea\u52a8\u767b\u5f55",
  logoutSuccess: "\u5df2\u9000\u51fa\u767b\u5f55",
  favoriteSuccess: "\u6536\u85cf\u6210\u529f",
  removeFavoriteSuccess: "\u53d6\u6d88\u6536\u85cf\u6210\u529f",
  clearSuccess: "\u6e05\u7a7a\u6210\u529f",
  saveSuccess: "\u4fdd\u5b58\u6210\u529f",
  aiWorking: "AI \u6b63\u5728\u601d\u8003...",
  aiSummary: "\u751f\u6210 AI \u6458\u8981",
  aiAsk: "\u53d1\u9001\u95ee\u9898",
  aiQuestionPlaceholder: "\u4f8b\u5982\uff1a\u8fd9\u7bc7\u65b0\u95fb\u7684\u6838\u5fc3\u7ed3\u8bba\u662f\u4ec0\u4e48\uff1f",
  aiQuestionRequired: "\u8bf7\u5148\u8f93\u5165\u4e00\u4e2a\u5173\u4e8e\u672c\u6587\u7684\u95ee\u9898\u3002",
  aiLoginRequired: "\u767b\u5f55\u540e\u5373\u53ef\u751f\u6210\u6458\u8981\u5e76\u9488\u5bf9\u672c\u6587\u8ffd\u95ee\u3002",
  aiAnswerPlaceholder: "\u6458\u8981\u6216\u56de\u7b54\u4f1a\u663e\u793a\u5728\u8fd9\u91cc\u3002",
  aiSummaryWorking: "\u6b63\u5728\u63d0\u70bc\u672c\u6587\u8981\u70b9...",
  aiAnswerWorking: "\u6b63\u5728\u6839\u636e\u672c\u6587\u7ec4\u7ec7\u56de\u7b54...",
  aiRequestFailed: "AI \u670d\u52a1\u6682\u65f6\u4e0d\u53ef\u7528\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002",
  aiSiteWelcome: "\u4f60\u53ef\u4ee5\u95ee\u6211\u65b0\u95fb\u5e93\u91cc\u7684\u5185\u5bb9\uff0c\u4f8b\u5982\uff1a\u6211\u60f3\u77e5\u9053\u6700\u8fd1\u7684\u8d22\u7ecf\u65b0\u95fb",
  loadFail: "\u52a0\u8f7d\u5931\u8d25\uff0c\u8bf7\u786e\u8ba4\u540e\u7aef\u548c MySQL \u5df2\u542f\u52a8",
  notLoggedIn: "\u672a\u767b\u5f55",
  loggedIn: "\u5df2\u767b\u5f55",
  emptyFavorite: "\u6682\u65e0\u6536\u85cf",
  emptyHistory: "\u6682\u65e0\u5386\u53f2",
  loadingNews: "\u6b63\u5728\u66f4\u65b0\u65b0\u95fb...",
  emptyNews: "\u6ca1\u6709\u627e\u5230\u5339\u914d\u7684\u65b0\u95fb",
  emptyNewsHint: "\u8bd5\u8bd5\u66f4\u6362\u5173\u952e\u8bcd\u6216\u91cd\u7f6e\u7b5b\u9009\u6761\u4ef6",
  openNews: "\u67e5\u770b\u65b0\u95fb"
};

let state = {
  categoryId: "",
  keyword: "",
  page: 1,
  pageSize: 10,
  total: 0,
  selectedNewsId: "",
  token: localStorage.getItem("token") || "",
  currentUser: null
};

const $ = (id) => document.getElementById(id);

function headers(extra = {}) {
  const base = { ...extra };
  if (state.token) base.Authorization = state.token;
  return base;
}

async function request(url, options = {}) {
  const res = await fetch(url, { ...options, headers: headers(options.headers || {}) });
  if (!res.ok) throw new Error(formatError(await res.text()));
  return res.json();
}

function formatError(rawText) {
  try {
    const data = JSON.parse(rawText);
    return data.detail || rawText;
  } catch (err) {
    return rawText;
  }
}

async function requestJson(url, method, data) {
  return request(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
}

function getImage(url) {
  return url || "https://picsum.photos/seed/news/300/200";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderDetailAiAnswer(label, content, tone = "") {
  const answer = $("aiAnswer");
  if (!answer) return;
  answer.className = `ai-answer${tone ? ` ${tone}` : ""}`;
  answer.setAttribute("role", tone === "error" ? "alert" : "status");
  answer.innerHTML = `
    <span class="ai-answer-label">${escapeHtml(label)}</span>
    <p>${escapeHtml(content)}</p>
  `;
}

function renderDetailAiLogin() {
  const answer = $("aiAnswer");
  answer.className = "ai-answer notice";
  answer.innerHTML = `
    <span class="ai-answer-label">\u767b\u5f55\u540e\u53ef\u7528</span>
    <p>${text.aiLoginRequired}</p>
    <button id="detailLogin" type="button">\u53bb\u767b\u5f55</button>
  `;
}

function syncDetailAiAccess() {
  const badge = $("detailAiAccess");
  if (!badge) return;
  badge.innerText = state.token ? "\u5df2\u5c31\u7eea" : "\u767b\u5f55\u540e\u53ef\u7528";
  badge.classList.toggle("ready", Boolean(state.token));
}

async function runDetailAi(button, pendingLabel, resultLabel, requestTask, pickResult) {
  const buttons = document.querySelectorAll("#detailAi button");
  const newsId = String(button.dataset.id);
  const originalLabel = button.innerText;
  buttons.forEach(item => { item.disabled = true; });
  button.innerText = pendingLabel;
  renderDetailAiAnswer("AI \u6b63\u5728\u601d\u8003", pendingLabel, "working");
  try {
    const data = await requestTask();
    if (state.selectedNewsId !== newsId || !$("detailAi")?.contains(button)) return;
    renderDetailAiAnswer(resultLabel, pickResult(data));
  } catch (err) {
    if (state.selectedNewsId !== newsId || !$("detailAi")?.contains(button)) return;
    renderDetailAiAnswer("\u8bf7\u6c42\u5931\u8d25", err.message || text.aiRequestFailed, "error");
  } finally {
    buttons.forEach(item => { item.disabled = false; });
    button.innerText = originalLabel;
  }
}

function showView(viewName) {
  document.querySelectorAll(".view").forEach(item => item.classList.add("hidden"));
  document.querySelectorAll(".nav-btn").forEach(item => {
    item.classList.remove("active");
    item.removeAttribute("aria-current");
  });
  $(`${viewName}View`).classList.remove("hidden");
  const navButton = document.querySelector(`.nav-btn[data-view="${viewName}"]`);
  if (navButton) {
    navButton.classList.add("active");
    navButton.setAttribute("aria-current", "page");
  }
  if (viewName === "favorites") loadFavorites();
  if (viewName === "history") loadHistory();
  if (viewName === "profile") refreshUserPanel();
}

function renderLoginStatus() {
  $("loginStatus").innerText = state.currentUser
    ? `${text.loggedIn}: ${state.currentUser.nickname || state.currentUser.username}`
    : text.notLoggedIn;
  $("logout").classList.toggle("hidden", !state.token);
  syncDetailAiAccess();
}

function appendSiteAiMessage(role, content, references = []) {
  const box = $("siteAiMessages");
  const refs = references.length
    ? `<div class="ai-refs">${references.map(item => `
        <div class="ai-ref" data-id="${item.id}">
          <strong>${item.title}</strong>
          <span>${item.category_name || text.unknownCategory} · ${item.views || 0} ${text.views}</span>
        </div>
      `).join("")}</div>`
    : "";

  box.innerHTML += `<div class="ai-msg ${role}">${content}${refs}</div>`;
  box.scrollTop = box.scrollHeight;
}

async function loadCurrentUser() {
  if (!state.token) {
    state.currentUser = null;
    renderLoginStatus();
    return;
  }
  try {
    state.currentUser = await request("/user/info");
  } catch (err) {
    state.token = "";
    state.currentUser = null;
    localStorage.removeItem("token");
  }
  renderLoginStatus();
}

function renderUserInfo() {
  if (!state.currentUser) {
    $("authPanel").classList.remove("hidden");
    $("userPanel").classList.add("hidden");
    return;
  }
  $("authPanel").classList.add("hidden");
  $("userPanel").classList.remove("hidden");
  const displayName = state.currentUser.nickname || state.currentUser.username || "";
  const firstLetter = displayName ? displayName.slice(0, 1).toUpperCase() : "U";
  const avatar = state.currentUser.avatar
    ? `<img src="${state.currentUser.avatar}" alt="${displayName}">`
    : firstLetter;
  $("userInfo").innerHTML = `
    <div class="profile-card">
      <div class="avatar">${avatar}</div>
      <div>
        <h2 class="profile-name">${displayName}</h2>
        <p class="profile-meta">@${state.currentUser.username || ""} · ID ${state.currentUser.id}</p>
        <p class="profile-bio">${state.currentUser.bio || "\u8fd9\u4e2a\u7528\u6237\u8fd8\u6ca1\u6709\u586b\u5199\u4e2a\u4eba\u7b80\u4ecb"}</p>
      </div>
    </div>
    <div class="info-grid">
      <div class="info-cell"><span class="info-label">\u6635\u79f0</span><span class="info-value">${state.currentUser.nickname || "\u672a\u8bbe\u7f6e"}</span></div>
      <div class="info-cell"><span class="info-label">\u624b\u673a\u53f7</span><span class="info-value">${state.currentUser.phone || "\u672a\u586b\u5199"}</span></div>
      <div class="info-cell"><span class="info-label">\u6027\u522b</span><span class="info-value">${state.currentUser.gender || "unknown"}</span></div>
      <div class="info-cell"><span class="info-label">\u521b\u5efa\u65f6\u95f4</span><span class="info-value">${state.currentUser.created_at || ""}</span></div>
    </div>
  `;
}

async function refreshUserPanel() {
  await loadCurrentUser();
  renderUserInfo();
}

async function loadCategories() {
  const data = await request("/news/categories");
  $("categories").innerHTML = data.map(item => `<button class="cat" data-id="${item.id}" aria-pressed="false">${item.name}</button>`).join("");
}

async function loadList() {
  const list = $("list");
  const listStatus = $("listStatus");
  list.setAttribute("aria-busy", "true");
  listStatus.classList.remove("error");
  listStatus.innerText = text.loadingNews;
  $("search").disabled = true;

  const params = new URLSearchParams({ page: String(state.page), page_size: String(state.pageSize) });
  if (state.categoryId) params.set("category_id", state.categoryId);
  if (state.keyword) params.set("keyword", state.keyword);
  try {
    const data = await request(`/news/list?${params.toString()}`);
    state.total = data.total;
    $("meta").innerText = `\u5171 ${data.total} \u6761\u65b0\u95fb`;
    $("page").innerText = `\u7b2c ${state.page} \u9875`;
    list.innerHTML = data.list.length
      ? data.list.map(item => `
          <article class="item${String(item.id) === state.selectedNewsId ? " selected" : ""}" data-id="${item.id}" tabindex="0" role="button" aria-label="${text.openNews}\uff1a${item.title}">
            <img src="${getImage(item.image)}" alt="${item.title}" loading="lazy">
            <div>
              <div class="item-meta"><span>${item.category_name || text.unknownCategory}</span><span>${item.views || 0} ${text.views}</span></div>
              <h3>${item.title}</h3>
              <p>${item.description || text.noDesc}</p>
            </div>
          </article>
        `).join("")
      : `<div class="empty-state"><strong>${text.emptyNews}</strong><span>${text.emptyNewsHint}</span></div>`;
    listStatus.innerText = "";
  } catch (err) {
    state.total = 0;
    list.innerHTML = "";
    listStatus.innerText = text.loadFail;
    listStatus.classList.add("error");
    throw err;
  } finally {
    list.setAttribute("aria-busy", "false");
    $("search").disabled = false;
    $("prev").disabled = state.page <= 1;
    $("next").disabled = state.page * state.pageSize >= state.total;
  }
}

async function addHistory(newsId) {
  if (!state.token) return;
  try {
    await requestJson("/history/add", "POST", { news_id: Number(newsId) });
  } catch (err) {
    console.warn(err);
  }
}

async function checkFavorite(newsId) {
  if (!state.token) return false;
  try {
    const data = await request(`/favorite/check?news_id=${newsId}`);
    return data.is_favorite;
  } catch (err) {
    return false;
  }
}

async function loadDetail(id) {
  const data = await request(`/news/detail/${id}`);
  state.selectedNewsId = String(id);
  document.querySelectorAll(".item").forEach(item => {
    item.classList.toggle("selected", item.dataset.id === state.selectedNewsId);
  });
  await addHistory(id);
  const isFavorite = await checkFavorite(id);
  const title = escapeHtml(data.title);
  const category = escapeHtml(data.category_name || text.unknownCategory);
  const author = escapeHtml(data.author || text.unknownAuthor);
  $("detail").innerHTML = `
    <img class="detail-img" src="${escapeHtml(getImage(data.image))}" alt="${title}">
    <div class="detail-heading">
      <span class="section-kicker">ARTICLE BRIEF</span>
      <h2>${title}</h2>
      <div class="detail-meta"><span>${category}</span><span>${author}</span><span>${data.views || 0} ${text.views}</span></div>
    </div>
    <div class="action-row">
      <button id="favoriteAction" data-id="${data.id}" data-favorite="${isFavorite ? "1" : "0"}">
        ${isFavorite ? "\u53d6\u6d88\u6536\u85cf" : "\u6536\u85cf"}
      </button>
    </div>
    <section id="detailAi" class="ai-box" aria-labelledby="detailAiTitle">
      <div class="ai-box-heading">
        <div>
          <span class="section-kicker">ARTICLE COPILOT</span>
          <h3 id="detailAiTitle">AI \u9605\u8bfb\u52a9\u624b</h3>
          <p>\u5148\u5feb\u901f\u603b\u7ed3\uff0c\u4e5f\u53ef\u4ee5\u56f4\u7ed5\u672c\u6587\u7ee7\u7eed\u8ffd\u95ee\u3002\u56de\u7b54\u4ec5\u57fa\u4e8e\u5f53\u524d\u65b0\u95fb\u5185\u5bb9\u3002</p>
        </div>
        <span id="detailAiAccess" class="ai-access"></span>
      </div>
      <div class="ai-summary-action">
        <button id="aiSummary" data-id="${data.id}">${text.aiSummary}</button>
        <span>\u7ea6 120 \u5b57\u4ee5\u5185</span>
      </div>
      <div class="ai-prompt-list" aria-label="\u5feb\u6377\u95ee\u9898">
        <button class="ai-prompt" type="button" data-question="\u8fd9\u7bc7\u65b0\u95fb\u7684\u6838\u5fc3\u7ed3\u8bba\u662f\u4ec0\u4e48\uff1f">\u6838\u5fc3\u7ed3\u8bba</button>
        <button class="ai-prompt" type="button" data-question="\u6587\u4e2d\u6709\u54ea\u4e9b\u5173\u952e\u4e8b\u5b9e\uff1f">\u5173\u952e\u4e8b\u5b9e</button>
      </div>
      <label for="aiQuestion">\u9488\u5bf9\u672c\u6587\u63d0\u95ee</label>
      <textarea id="aiQuestion" maxlength="1000" aria-describedby="aiQuestionError" placeholder="${text.aiQuestionPlaceholder}"></textarea>
      <p id="aiQuestionError" class="form-error" role="alert"></p>
      <button id="aiAsk" data-id="${data.id}">${text.aiAsk}</button>
      <div id="aiAnswer" class="ai-answer empty" role="status" aria-live="polite">
        <span class="ai-answer-label">AI \u751f\u6210\u5185\u5bb9</span>
        <p>${text.aiAnswerPlaceholder}</p>
      </div>
    </section>
    <p class="detail-lead">${escapeHtml(data.description || "")}</p>
    <div class="body">${escapeHtml(data.content || "")}</div>
    <h3>\u76f8\u5173\u63a8\u8350</h3>
    ${(data.related_news || []).map(item => `
      <button class="related" data-id="${item.id}">
        <strong>${escapeHtml(item.title)}</strong>
        <span>${escapeHtml(item.category_name || text.unknownCategory)} · ${item.views || 0} ${text.views}</span>
      </button>
    `).join("") || `<p>${text.noRelated}</p>`}
  `;
  syncDetailAiAccess();
  if (window.matchMedia("(max-width: 980px)").matches) {
    $("detail").scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

async function loadFavorites() {
  if (!state.token) {
    $("favoritesList").innerHTML = `<p>${text.loginFirst}</p>`;
    return;
  }
  const data = await request("/favorite/list?page=1&page_size=50");
  $("favoritesList").innerHTML = data.list.length
    ? data.list.map(item => renderSavedItem(item, "favorite")).join("")
    : `<p>${text.emptyFavorite}</p>`;
}

async function loadHistory() {
  if (!state.token) {
    $("historyList").innerHTML = `<p>${text.loginFirst}</p>`;
    return;
  }
  const data = await request("/history/list?page=1&page_size=50");
  $("historyList").innerHTML = data.list.length
    ? data.list.map(item => renderSavedItem(item, "history")).join("")
    : `<p>${text.emptyHistory}</p>`;
}

function renderSavedItem(item, type) {
  const action = type === "favorite"
    ? `<button class="remove-favorite" data-id="${item.id}">\u53d6\u6d88\u6536\u85cf</button>`
    : `<button class="delete-history" data-id="${item.history_id}">\u5220\u9664\u8bb0\u5f55</button>`;
  return `
    <article class="item" data-id="${item.id}">
      <img src="${getImage(item.image)}" alt="${item.title}">
      <div>
        <h3>${item.title}</h3>
        <p>${item.description || text.noDesc}</p>
        <p>${item.category_name || text.unknownCategory} · ${item.views || 0} ${text.views}</p>
        <div class="action-row">${action}</div>
      </div>
    </article>
  `;
}

document.addEventListener("click", async (event) => {
  const nav = event.target.closest(".nav-btn");
  if (nav) showView(nav.dataset.view);

  const cat = event.target.closest(".cat");
  if (cat) {
    showView("news");
    document.querySelectorAll(".cat").forEach(btn => {
      btn.classList.remove("active");
      btn.setAttribute("aria-pressed", "false");
    });
    cat.classList.add("active");
    cat.setAttribute("aria-pressed", "true");
    state.categoryId = cat.dataset.id;
    state.page = 1;
    $("title").innerText = cat.innerText;
    await loadList();
  }

  const item = event.target.closest(".item");
  if (item && !event.target.closest("button")) {
    showView("news");
    await loadDetail(item.dataset.id);
  }

  const related = event.target.closest(".related");
  if (related) await loadDetail(related.dataset.id);

  const aiRef = event.target.closest(".ai-ref");
  if (aiRef) {
    showView("news");
    await loadDetail(aiRef.dataset.id);
  }

  const favoriteAction = event.target.closest("#favoriteAction");
  if (favoriteAction) {
    if (!state.token) {
      alert(text.loginFirst);
      showView("profile");
      return;
    }
    const newsId = Number(favoriteAction.dataset.id);
    const isFavorite = favoriteAction.dataset.favorite === "1";
    if (isFavorite) {
      await request(`/favorite/remove?news_id=${newsId}`, { method: "DELETE" });
      alert(text.removeFavoriteSuccess);
    } else {
      await requestJson("/favorite/add", "POST", { news_id: newsId });
      alert(text.favoriteSuccess);
    }
    await loadDetail(newsId);
  }

  const aiSummary = event.target.closest("#aiSummary");
  if (aiSummary) {
    if (!state.token) {
      renderDetailAiLogin();
      return;
    }
    await runDetailAi(
      aiSummary,
      text.aiSummaryWorking,
      "AI \u6458\u8981",
      () => requestJson("/ai/news/summary", "POST", { news_id: Number(aiSummary.dataset.id) }),
      data => data.summary || ""
    );
  }

  const aiAsk = event.target.closest("#aiAsk");
  if (aiAsk) {
    if (!state.token) {
      renderDetailAiLogin();
      return;
    }
    const question = $("aiQuestion").value.trim();
    if (!question) {
      $("aiQuestion").setAttribute("aria-invalid", "true");
      $("aiQuestionError").innerText = text.aiQuestionRequired;
      $("aiQuestion").focus();
      return;
    }
    await runDetailAi(
      aiAsk,
      text.aiAnswerWorking,
      "AI \u56de\u7b54",
      () => requestJson("/ai/news/chat", "POST", {
        news_id: Number(aiAsk.dataset.id),
        question
      }),
      data => data.answer || ""
    );
  }

  const aiPrompt = event.target.closest(".ai-prompt");
  if (aiPrompt) {
    $("aiQuestion").value = aiPrompt.dataset.question;
    $("aiQuestion").removeAttribute("aria-invalid");
    $("aiQuestionError").innerText = "";
    $("aiQuestion").focus();
  }

  const detailLogin = event.target.closest("#detailLogin");
  if (detailLogin) showView("profile");

  const removeFavorite = event.target.closest(".remove-favorite");
  if (removeFavorite) {
    await request(`/favorite/remove?news_id=${removeFavorite.dataset.id}`, { method: "DELETE" });
    await loadFavorites();
  }

  const deleteHistory = event.target.closest(".delete-history");
  if (deleteHistory) {
    await request(`/history/delete/${deleteHistory.dataset.id}`, { method: "DELETE" });
    await loadHistory();
  }
});

$("newsSearchForm").onsubmit = async (event) => {
  event.preventDefault();
  state.keyword = $("keyword").value.trim();
  state.page = 1;
  await loadList();
};

$("reset").onclick = async () => {
  state.categoryId = "";
  state.keyword = "";
  state.page = 1;
  $("keyword").value = "";
  $("title").innerText = text.allNews;
  document.querySelectorAll(".cat").forEach(btn => {
    btn.classList.remove("active");
    btn.setAttribute("aria-pressed", "false");
  });
  const allNewsButton = document.querySelector(".cat[data-id='']");
  allNewsButton.classList.add("active");
  allNewsButton.setAttribute("aria-pressed", "true");
  await loadList();
};

$("prev").onclick = async () => {
  if (state.page > 1) {
    state.page--;
    await loadList();
  }
};

$("next").onclick = async () => {
  if (state.page * state.pageSize < state.total) {
    state.page++;
    await loadList();
  }
};

$("list").addEventListener("keydown", async (event) => {
  const item = event.target.closest(".item");
  if (!item || !["Enter", " "].includes(event.key)) return;
  event.preventDefault();
  await loadDetail(item.dataset.id);
});

document.addEventListener("input", (event) => {
  if (event.target.id !== "aiQuestion") return;
  event.target.removeAttribute("aria-invalid");
  $("aiQuestionError").innerText = "";
});

$("loginForm").onsubmit = async (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.target).entries());
  const result = await requestJson("/user/login", "POST", data);
  state.token = result.token;
  localStorage.setItem("token", state.token);
  state.currentUser = result.user;
  renderLoginStatus();
  renderUserInfo();
  showView("profile");
  alert(text.loginSuccess);
};

$("registerForm").onsubmit = async (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.target).entries());
  await requestJson("/user/register", "POST", data);
  const result = await requestJson("/user/login", "POST", { username: data.username, password: data.password });
  state.token = result.token;
  localStorage.setItem("token", state.token);
  state.currentUser = result.user;
  renderLoginStatus();
  renderUserInfo();
  showView("profile");
  alert(text.registerSuccess);
};

$("showRegister").onclick = () => {
  showView("register");
};

$("showLogin").onclick = () => {
  showView("profile");
};

$("updateForm").onsubmit = async (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.target).entries());
  Object.keys(data).forEach(key => { if (data[key] === "") delete data[key]; });
  state.currentUser = await requestJson("/user/update", "PUT", data);
  renderLoginStatus();
  renderUserInfo();
  alert(text.saveSuccess);
};

$("logout").onclick = async () => {
  if (state.token) await request("/user/logout", { method: "POST" });
  state.token = "";
  state.currentUser = null;
  localStorage.removeItem("token");
  renderLoginStatus();
  renderUserInfo();
  alert(text.logoutSuccess);
};

$("clearFavorites").onclick = async () => {
  if (!state.token) return alert(text.loginFirst);
  await request("/favorite/clear", { method: "DELETE" });
  await loadFavorites();
  alert(text.clearSuccess);
};

$("clearHistory").onclick = async () => {
  if (!state.token) return alert(text.loginFirst);
  await request("/history/clear", { method: "DELETE" });
  await loadHistory();
  alert(text.clearSuccess);
};

$("siteAiForm").onsubmit = async (event) => {
  event.preventDefault();
  if (!state.token) {
    alert(text.loginFirst);
    showView("profile");
    return;
  }

  const input = $("siteAiInput");
  const message = input.value.trim();
  if (!message) return;

  appendSiteAiMessage("user", message);
  input.value = "";
  appendSiteAiMessage("assistant", text.aiWorking);

  try {
    const data = await requestJson("/ai/chat", "POST", { message, limit: 6 });
    const messages = document.querySelectorAll(".site-ai-messages .assistant");
    const last = messages[messages.length - 1];
    last.innerHTML = `${data.answer || ""}${(data.references || []).length ? `<div class="ai-refs">${data.references.map(item => `
      <div class="ai-ref" data-id="${item.id}">
        <strong>${item.title}</strong>
        <span>${item.category_name || text.unknownCategory} · ${item.views || 0} ${text.views}</span>
      </div>
    `).join("")}</div>` : ""}`;
  } catch (err) {
    const messages = document.querySelectorAll(".site-ai-messages .assistant");
    const last = messages[messages.length - 1];
    last.innerText = err.message || "\u8bf7\u6c42\u5931\u8d25";
  }
};

$("siteAiTab").onclick = () => {
  const drawer = $("siteAi");
  const isOpen = drawer.classList.toggle("open");
  $("siteAiTab").setAttribute("aria-expanded", String(isOpen));
  if (isOpen) $("siteAiInput").focus();
};

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape" || !$("siteAi").classList.contains("open")) return;
  $("siteAi").classList.remove("open");
  $("siteAiTab").setAttribute("aria-expanded", "false");
  $("siteAiTab").focus();
});

async function init() {
  try {
    await loadCurrentUser();
    renderUserInfo();
    appendSiteAiMessage("assistant", text.aiSiteWelcome);
    await loadCategories();
    await loadList();
  } catch (err) {
    alert(text.loadFail);
    console.error(err);
  }
}

init();
