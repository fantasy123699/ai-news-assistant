const text = {
  allNews: "\u5168\u90e8\u65b0\u95fb",
  unknownCategory: "\u672a\u5206\u7c7b",
  unknownAuthor: "\u672a\u77e5\u4f5c\u8005",
  noDesc: "\u6682\u65e0\u7b80\u4ecb",
  noRelated: "\u6682\u65e0\u76f8\u5173\u63a8\u8350",
  views: "\u6b21\u6d4f\u89c8",
  loginFirst: "\u8bf7\u5148\u767b\u5f55",
  favoriteSuccess: "\u6536\u85cf\u6210\u529f",
  removeFavoriteSuccess: "\u53d6\u6d88\u6536\u85cf\u6210\u529f",
  usernameRequired: "\u8bf7\u8f93\u5165\u7528\u6237\u540d\u3002",
  usernameLength: "\u7528\u6237\u540d\u9700\u8981 3\u201350 \u4e2a\u5b57\u7b26\u3002",
  passwordRequired: "\u8bf7\u8f93\u5165\u5bc6\u7801\u3002",
  passwordLength: "\u5bc6\u7801\u81f3\u5c11\u9700\u8981 8 \u4e2a\u5b57\u7b26\u3002",
  passwordBytes: "\u5bc6\u7801\u4e0d\u80fd\u8d85\u8fc7 72 \u4e2a UTF-8 \u5b57\u8282\u3002",
  loginWorking: "\u6b63\u5728\u9a8c\u8bc1\u8d26\u53f7...",
  registerWorking: "\u6b63\u5728\u521b\u5efa\u8d26\u53f7...",
  profileWorking: "\u6b63\u5728\u4fdd\u5b58...",
  noProfileChanges: "\u8d44\u6599\u6ca1\u6709\u53d8\u66f4\uff0c\u65e0\u9700\u4fdd\u5b58\u3002",
  sessionExpired: "\u767b\u5f55\u72b6\u6001\u5df2\u5931\u6548\uff0c\u8bf7\u91cd\u65b0\u767b\u5f55\u3002",
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
  currentUser: null,
  authFeedback: ""
};

const $ = (id) => document.getElementById(id);

function headers(extra = {}) {
  const base = { ...extra };
  if (state.token) base.Authorization = state.token;
  return base;
}

async function request(url, options = {}) {
  const res = await fetch(url, { ...options, headers: headers(options.headers || {}) });
  if (!res.ok) {
    const error = new Error(formatError(await res.text()));
    error.status = res.status;
    throw error;
  }
  return res.json();
}

function formatError(rawText) {
  try {
    const data = JSON.parse(rawText);
    if (Array.isArray(data.detail)) {
      return data.detail.map(item => item.msg || String(item)).join("\uff1b");
    }
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

const savedViewConfig = {
  favorite: {
    endpoint: "/favorite/list?page=1&page_size=50",
    listId: "favoritesList",
    countId: "favoritesCount",
    clearId: "clearFavorites",
    confirmId: "favoritesClearConfirm",
    feedbackId: "favoritesFeedback",
    emptyTitle: "还没有收藏",
    emptyHint: "在新闻详情中点击“收藏”，值得回看的内容会出现在这里。",
    itemLabel: "篇收藏"
  },
  history: {
    endpoint: "/history/list?page=1&page_size=50",
    listId: "historyList",
    countId: "historyCount",
    clearId: "clearHistory",
    confirmId: "historyClearConfirm",
    feedbackId: "historyFeedback",
    emptyTitle: "还没有浏览记录",
    emptyHint: "打开一篇新闻后，最近阅读的内容会自动保留在这里。",
    itemLabel: "条记录"
  }
};

function setSavedFeedback(type, message = "", tone = "") {
  const feedback = $(savedViewConfig[type].feedbackId);
  feedback.className = `list-status${tone ? ` ${tone}` : ""}`;
  feedback.setAttribute("role", tone === "error" ? "alert" : "status");
  feedback.innerText = message;
}

function setClearPrompt(type, open) {
  const config = savedViewConfig[type];
  $(config.confirmId).classList.toggle("hidden", !open);
  $(config.clearId).setAttribute("aria-expanded", String(open));
}

function renderSavedState(type, title, hint, action = "browse") {
  const actionButton = action === "login"
    ? `<button type="button" class="primary-btn saved-login">去登录</button>`
    : action === "retry"
      ? `<button type="button" class="secondary-btn retry-saved" data-type="${type}">重新加载</button>`
      : `<button type="button" class="primary-btn saved-browse">浏览新闻</button>`;
  return `
    <div class="empty-state saved-state">
      <strong>${escapeHtml(title)}</strong>
      <span>${escapeHtml(hint)}</span>
      <div class="action-row">${actionButton}</div>
    </div>
  `;
}

function renderSavedSkeleton() {
  return [1, 2].map(() => `
    <div class="item saved-skeleton" aria-hidden="true">
      <div class="skeleton-block"></div>
      <div class="skeleton-copy">
        <span class="skeleton-block skeleton-line"></span>
        <span class="skeleton-block skeleton-line short"></span>
      </div>
    </div>
  `).join("");
}

function formatSavedTime(value, prefix) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const formatted = new Intl.DateTimeFormat("zh-CN", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
  return `${prefix}${formatted}`;
}

function setFormFeedback(id, message = "", tone = "") {
  const feedback = $(id);
  if (!feedback) return;
  feedback.className = `form-feedback${tone ? ` ${tone}` : ""}`;
  feedback.setAttribute("role", tone === "error" ? "alert" : "status");
  feedback.innerText = message;
}

function setFieldError(inputId, errorId, message = "") {
  const input = $(inputId);
  const error = $(errorId);
  if (!input || !error) return;
  input.toggleAttribute("aria-invalid", Boolean(message));
  error.innerText = message;
}

function setFormBusy(form, busy, pendingLabel) {
  const submit = form.querySelector('button[type="submit"]');
  if (!submit) return;
  if (busy) submit.dataset.idleLabel = submit.innerText;
  form.setAttribute("aria-busy", String(busy));
  form.querySelectorAll("input, select, textarea, button").forEach(item => {
    item.disabled = busy;
  });
  submit.innerText = busy ? pendingLabel : submit.dataset.idleLabel;
}

function friendlyAuthError(error, fallback) {
  const message = String(error?.message || "");
  if (message.includes("Wrong username or password")) return "\u7528\u6237\u540d\u6216\u5bc6\u7801\u4e0d\u6b63\u786e\uff0c\u8bf7\u91cd\u65b0\u8f93\u5165\u3002";
  if (message.includes("Username already exists")) return "\u8be5\u7528\u6237\u540d\u5df2\u88ab\u4f7f\u7528\uff0c\u8bf7\u66f4\u6362\u4e00\u4e2a\u3002";
  if (message.includes("Phone already exists")) return "\u8be5\u624b\u673a\u53f7\u5df2\u7ed1\u5b9a\u5176\u4ed6\u8d26\u53f7\u3002";
  return fallback;
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
  const navViewName = viewName === "register" ? "profile" : viewName;
  const navButton = document.querySelector(`.nav-btn[data-view="${navViewName}"]`);
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
  $("loginStatus").classList.toggle("signed-in", Boolean(state.currentUser));
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
    state.authFeedback = text.sessionExpired;
  }
  renderLoginStatus();
}

function formatGender(value) {
  return { male: "\u7537", female: "\u5973", unknown: "\u672a\u8bf4\u660e" }[value] || "\u672a\u8bf4\u660e";
}

function formatProfileDate(value) {
  if (!value) return "\u672a\u77e5";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString("zh-CN");
}

function syncProfileForm() {
  const form = $("updateForm");
  if (!form || !state.currentUser) return;
  ["nickname", "avatar", "phone", "bio"].forEach(name => {
    const field = form.elements.namedItem(name);
    const value = state.currentUser[name] || "";
    field.value = value;
    field.defaultValue = value;
  });
  form.elements.namedItem("gender").value = state.currentUser.gender || "unknown";
}

function renderUserInfo() {
  if (!state.currentUser) {
    $("authPanel").classList.remove("hidden");
    $("userPanel").classList.add("hidden");
    if (state.authFeedback) {
      setFormFeedback("loginFeedback", state.authFeedback, "error");
      state.authFeedback = "";
    }
    return;
  }
  $("authPanel").classList.add("hidden");
  $("userPanel").classList.remove("hidden");
  const displayName = escapeHtml(state.currentUser.nickname || state.currentUser.username || "");
  const firstLetter = displayName ? displayName.slice(0, 1).toUpperCase() : "U";
  const avatar = state.currentUser.avatar
    ? `<img src="${escapeHtml(state.currentUser.avatar)}" alt="${displayName}">`
    : firstLetter;
  $("userInfo").innerHTML = `
    <div class="profile-card">
      <div class="avatar">${avatar}</div>
      <div>
        <h2 class="profile-name">${displayName}</h2>
        <p class="profile-meta">@${escapeHtml(state.currentUser.username || "")} · ID ${state.currentUser.id}</p>
        <p class="profile-bio">${escapeHtml(state.currentUser.bio || "\u8fd9\u4e2a\u7528\u6237\u8fd8\u6ca1\u6709\u586b\u5199\u4e2a\u4eba\u7b80\u4ecb")}</p>
      </div>
    </div>
    <div class="info-grid">
      <div class="info-cell"><span class="info-label">\u6635\u79f0</span><span class="info-value">${escapeHtml(state.currentUser.nickname || "\u672a\u8bbe\u7f6e")}</span></div>
      <div class="info-cell"><span class="info-label">\u624b\u673a\u53f7</span><span class="info-value">${escapeHtml(state.currentUser.phone || "\u672a\u586b\u5199")}</span></div>
      <div class="info-cell"><span class="info-label">\u6027\u522b</span><span class="info-value">${formatGender(state.currentUser.gender)}</span></div>
      <div class="info-cell"><span class="info-label">\u521b\u5efa\u65f6\u95f4</span><span class="info-value">${escapeHtml(formatProfileDate(state.currentUser.created_at))}</span></div>
    </div>
  `;
  syncProfileForm();
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
  return loadSavedItems("favorite");
}

async function loadHistory() {
  return loadSavedItems("history");
}

async function loadSavedItems(type) {
  const config = savedViewConfig[type];
  const list = $(config.listId);
  setClearPrompt(type, false);
  setSavedFeedback(type);
  $(config.clearId).disabled = true;
  if (!state.token) {
    $(config.countId).innerText = "登录后可用";
    list.innerHTML = renderSavedState(type, "登录后查看个人记录", "登录后即可在不同阅读任务之间保存收藏和浏览历史。", "login");
    list.setAttribute("aria-busy", "false");
    return false;
  }

  $(config.countId).innerText = "正在加载";
  list.setAttribute("aria-busy", "true");
  list.innerHTML = renderSavedSkeleton();
  try {
    const data = await request(config.endpoint);
    const items = Array.isArray(data.list) ? data.list : [];
    $(config.countId).innerText = `${data.total ?? items.length} ${config.itemLabel}`;
    $(config.clearId).disabled = items.length === 0;
    list.innerHTML = items.length
      ? items.map(item => renderSavedItem(item, type)).join("")
      : renderSavedState(type, config.emptyTitle, config.emptyHint);
    return true;
  } catch (err) {
    $(config.countId).innerText = "加载失败";
    list.innerHTML = renderSavedState(type, "暂时无法加载", "请检查网络或服务状态，然后重新尝试。", "retry");
    setSavedFeedback(type, err.message || "个人记录加载失败，请稍后重试。", "error");
    return false;
  } finally {
    list.setAttribute("aria-busy", "false");
  }
}

function renderSavedItem(item, type) {
  const action = type === "favorite"
    ? `<button type="button" class="remove-favorite" data-id="${item.id}" aria-label="取消收藏：${escapeHtml(item.title)}">取消收藏</button>`
    : `<button type="button" class="delete-history" data-id="${item.history_id}" aria-label="删除历史记录：${escapeHtml(item.title)}">删除记录</button>`;
  const savedTime = type === "favorite"
    ? formatSavedTime(item.favorite_time, "收藏于 ")
    : formatSavedTime(item.view_time, "浏览于 ");
  return `
    <article class="item saved-item" data-id="${item.id}">
      <img src="${escapeHtml(getImage(item.image))}" alt="${escapeHtml(item.title)}">
      <div class="saved-item-content">
        <h3><button type="button" class="saved-open" data-id="${item.id}">${escapeHtml(item.title)}</button></h3>
        <p>${escapeHtml(item.description || text.noDesc)}</p>
        <div class="item-meta">
          <span>${escapeHtml(item.category_name || text.unknownCategory)}</span>
          <span>${Number(item.views) || 0} ${text.views}</span>
          ${savedTime ? `<span>${escapeHtml(savedTime)}</span>` : ""}
        </div>
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
  if (item && !item.classList.contains("saved-skeleton") && !event.target.closest("button")) {
    showView("news");
    await loadDetail(item.dataset.id);
  }

  const savedOpen = event.target.closest(".saved-open");
  if (savedOpen) {
    showView("news");
    await loadDetail(savedOpen.dataset.id);
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
    const idleLabel = removeFavorite.innerText;
    removeFavorite.disabled = true;
    removeFavorite.innerText = "正在取消...";
    try {
      await request(`/favorite/remove?news_id=${removeFavorite.dataset.id}`, { method: "DELETE" });
      if (await loadFavorites()) setSavedFeedback("favorite", "已取消收藏。", "success");
    } catch (err) {
      removeFavorite.disabled = false;
      removeFavorite.innerText = idleLabel;
      setSavedFeedback("favorite", err.message || "取消收藏失败，请重试。", "error");
    }
  }

  const deleteHistory = event.target.closest(".delete-history");
  if (deleteHistory) {
    const idleLabel = deleteHistory.innerText;
    deleteHistory.disabled = true;
    deleteHistory.innerText = "正在删除...";
    try {
      await request(`/history/delete/${deleteHistory.dataset.id}`, { method: "DELETE" });
      if (await loadHistory()) setSavedFeedback("history", "已删除这条浏览记录。", "success");
    } catch (err) {
      deleteHistory.disabled = false;
      deleteHistory.innerText = idleLabel;
      setSavedFeedback("history", err.message || "删除记录失败，请重试。", "error");
    }
  }

  const savedBrowse = event.target.closest(".saved-browse");
  if (savedBrowse) showView("news");

  const savedLogin = event.target.closest(".saved-login");
  if (savedLogin) showView("profile");

  const retrySaved = event.target.closest(".retry-saved");
  if (retrySaved) await loadSavedItems(retrySaved.dataset.type);
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
  if (event.target.id === "aiQuestion") {
    event.target.removeAttribute("aria-invalid");
    $("aiQuestionError").innerText = "";
  }
  const fieldErrors = {
    loginUsername: "loginUsernameError",
    loginPassword: "loginPasswordError",
    registerUsername: "registerUsernameError",
    registerPassword: "registerPasswordError"
  };
  if (fieldErrors[event.target.id]) {
    setFieldError(event.target.id, fieldErrors[event.target.id]);
  }
});

$("loginForm").onsubmit = async (event) => {
  event.preventDefault();
  const form = event.target;
  const data = Object.fromEntries(new FormData(form).entries());
  data.username = data.username.trim();
  setFormFeedback("loginFeedback");
  setFieldError("loginUsername", "loginUsernameError");
  setFieldError("loginPassword", "loginPasswordError");
  if (!data.username) {
    setFieldError("loginUsername", "loginUsernameError", text.usernameRequired);
    $("loginUsername").focus();
    return;
  }
  if (!data.password) {
    setFieldError("loginPassword", "loginPasswordError", text.passwordRequired);
    $("loginPassword").focus();
    return;
  }
  setFormBusy(form, true, text.loginWorking);
  try {
    const result = await requestJson("/user/login", "POST", data);
    state.token = result.token;
    localStorage.setItem("token", state.token);
    state.currentUser = result.user;
    form.reset();
    renderLoginStatus();
    renderUserInfo();
    showView("profile");
    setFormFeedback("profileFeedback", "\u767b\u5f55\u6210\u529f\uff0cAI \u6458\u8981\u3001\u8ffd\u95ee\u548c\u6536\u85cf\u529f\u80fd\u5df2\u89e3\u9501\u3002", "success");
  } catch (err) {
    setFormFeedback("loginFeedback", friendlyAuthError(err, "\u6682\u65f6\u65e0\u6cd5\u767b\u5f55\uff0c\u8bf7\u68c0\u67e5\u8f93\u5165\u540e\u91cd\u8bd5\u3002"), "error");
    $("loginFeedback").focus();
  } finally {
    setFormBusy(form, false, "");
  }
};

$("registerForm").onsubmit = async (event) => {
  event.preventDefault();
  const form = event.target;
  const data = Object.fromEntries(new FormData(form).entries());
  data.username = data.username.trim();
  data.nickname = data.nickname.trim();
  data.phone = data.phone.trim();
  setFormFeedback("registerFeedback");
  setFieldError("registerUsername", "registerUsernameError");
  setFieldError("registerPassword", "registerPasswordError");
  if (data.username.length < 3 || data.username.length > 50) {
    setFieldError("registerUsername", "registerUsernameError", text.usernameLength);
    $("registerUsername").focus();
    return;
  }
  if (data.password.length < 8) {
    setFieldError("registerPassword", "registerPasswordError", text.passwordLength);
    $("registerPassword").focus();
    return;
  }
  if (new TextEncoder().encode(data.password).length > 72) {
    setFieldError("registerPassword", "registerPasswordError", text.passwordBytes);
    $("registerPassword").focus();
    return;
  }
  if (!data.nickname) delete data.nickname;
  if (!data.phone) delete data.phone;
  setFormBusy(form, true, text.registerWorking);
  try {
    await requestJson("/user/register", "POST", data);
    const result = await requestJson("/user/login", "POST", { username: data.username, password: data.password });
    state.token = result.token;
    localStorage.setItem("token", state.token);
    state.currentUser = result.user;
    form.reset();
    renderLoginStatus();
    renderUserInfo();
    showView("profile");
    setFormFeedback("profileFeedback", "\u8d26\u53f7\u5df2\u521b\u5efa\u5e76\u767b\u5f55\uff0c\u4f60\u53ef\u4ee5\u7ee7\u7eed\u5b8c\u5584\u8d44\u6599\u3002", "success");
  } catch (err) {
    setFormFeedback("registerFeedback", friendlyAuthError(err, "\u6682\u65f6\u65e0\u6cd5\u521b\u5efa\u8d26\u53f7\uff0c\u8bf7\u68c0\u67e5\u8f93\u5165\u540e\u91cd\u8bd5\u3002"), "error");
    $("registerFeedback").focus();
  } finally {
    setFormBusy(form, false, "");
  }
};

$("showRegister").onclick = () => {
  setFormFeedback("loginFeedback");
  showView("register");
};

$("showLogin").onclick = () => {
  setFormFeedback("registerFeedback");
  showView("profile");
};

$("updateForm").onsubmit = async (event) => {
  event.preventDefault();
  const form = event.target;
  const values = Object.fromEntries(new FormData(form).entries());
  const data = {};
  Object.entries(values).forEach(([key, value]) => {
    const normalized = typeof value === "string" ? value.trim() : value;
    if (String(normalized) !== String(state.currentUser[key] || (key === "gender" ? "unknown" : ""))) {
      data[key] = normalized;
    }
  });
  setFormFeedback("profileFeedback");
  if (!Object.keys(data).length) {
    setFormFeedback("profileFeedback", text.noProfileChanges);
    return;
  }
  setFormBusy(form, true, text.profileWorking);
  try {
    state.currentUser = await requestJson("/user/update", "PUT", data);
    renderLoginStatus();
    renderUserInfo();
    setFormFeedback("profileFeedback", "\u8d44\u6599\u5df2\u4fdd\u5b58\uff0c\u9875\u9762\u4fe1\u606f\u5df2\u540c\u6b65\u66f4\u65b0\u3002", "success");
  } catch (err) {
    setFormFeedback("profileFeedback", friendlyAuthError(err, "\u6682\u65f6\u65e0\u6cd5\u4fdd\u5b58\u8d44\u6599\uff0c\u8bf7\u68c0\u67e5\u8f93\u5165\u540e\u91cd\u8bd5\u3002"), "error");
    $("profileFeedback").focus();
  } finally {
    setFormBusy(form, false, "");
  }
};

$("logout").onclick = async () => {
  const button = $("logout");
  button.disabled = true;
  button.innerText = "\u6b63\u5728\u9000\u51fa...";
  let logoutConfirmed = true;
  try {
    if (state.token) await request("/user/logout", { method: "POST" });
  } catch (err) {
    logoutConfirmed = false;
  }
  state.token = "";
  state.currentUser = null;
  localStorage.removeItem("token");
  renderLoginStatus();
  renderUserInfo();
  showView("profile");
  setFormFeedback(
    "loginFeedback",
    logoutConfirmed ? "\u5df2\u5b89\u5168\u9000\u51fa\u5f53\u524d\u8d26\u53f7\u3002" : "\u5df2\u4ece\u672c\u673a\u9000\u51fa\uff0c\u4f46\u670d\u52a1\u5668\u4f1a\u8bdd\u672a\u80fd\u786e\u8ba4\u5173\u95ed\u3002",
    logoutConfirmed ? "success" : "error"
  );
  button.disabled = false;
  button.innerText = "\u9000\u51fa";
};

$("clearFavorites").onclick = () => setClearPrompt("favorite", true);
$("cancelClearFavorites").onclick = () => {
  setClearPrompt("favorite", false);
  $("clearFavorites").focus();
};
$("clearHistory").onclick = () => setClearPrompt("history", true);
$("cancelClearHistory").onclick = () => {
  setClearPrompt("history", false);
  $("clearHistory").focus();
};

async function confirmClearSaved(type) {
  const isFavorite = type === "favorite";
  const confirmButton = $(isFavorite ? "confirmClearFavorites" : "confirmClearHistory");
  const cancelButton = $(isFavorite ? "cancelClearFavorites" : "cancelClearHistory");
  const idleLabel = confirmButton.innerText;
  confirmButton.disabled = true;
  cancelButton.disabled = true;
  confirmButton.innerText = "正在清空...";
  try {
    await request(isFavorite ? "/favorite/clear" : "/history/clear", { method: "DELETE" });
    if (await loadSavedItems(type)) {
      setSavedFeedback(type, isFavorite ? "收藏已全部清空。" : "浏览历史已全部清空。", "success");
    }
  } catch (err) {
    confirmButton.disabled = false;
    cancelButton.disabled = false;
    confirmButton.innerText = idleLabel;
    setSavedFeedback(type, err.message || "清空失败，请重试。", "error");
  }
}

$("confirmClearFavorites").onclick = () => confirmClearSaved("favorite");
$("confirmClearHistory").onclick = () => confirmClearSaved("history");

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
