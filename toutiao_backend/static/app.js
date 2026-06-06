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
  aiSummary: "AI \u603b\u7ed3",
  aiAsk: "\u63d0\u95ee",
  aiQuestionPlaceholder: "\u9488\u5bf9\u8fd9\u7bc7\u65b0\u95fb\u63d0\u4e00\u4e2a\u95ee\u9898",
  aiSiteWelcome: "\u4f60\u53ef\u4ee5\u95ee\u6211\u65b0\u95fb\u5e93\u91cc\u7684\u5185\u5bb9\uff0c\u4f8b\u5982\uff1a\u6211\u60f3\u77e5\u9053\u6700\u8fd1\u7684\u8d22\u7ecf\u65b0\u95fb",
  loadFail: "\u52a0\u8f7d\u5931\u8d25\uff0c\u8bf7\u786e\u8ba4\u540e\u7aef\u548c MySQL \u5df2\u542f\u52a8",
  notLoggedIn: "\u672a\u767b\u5f55",
  loggedIn: "\u5df2\u767b\u5f55",
  emptyFavorite: "\u6682\u65e0\u6536\u85cf",
  emptyHistory: "\u6682\u65e0\u5386\u53f2"
};

let state = {
  categoryId: "",
  keyword: "",
  page: 1,
  pageSize: 10,
  total: 0,
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

function showView(viewName) {
  document.querySelectorAll(".view").forEach(item => item.classList.add("hidden"));
  document.querySelectorAll(".nav-btn").forEach(item => item.classList.remove("active"));
  $(`${viewName}View`).classList.remove("hidden");
  const navButton = document.querySelector(`.nav-btn[data-view="${viewName}"]`);
  if (navButton) navButton.classList.add("active");
  if (viewName === "favorites") loadFavorites();
  if (viewName === "history") loadHistory();
  if (viewName === "profile") refreshUserPanel();
}

function renderLoginStatus() {
  $("loginStatus").innerText = state.currentUser
    ? `${text.loggedIn}: ${state.currentUser.nickname || state.currentUser.username}`
    : text.notLoggedIn;
  $("logout").classList.toggle("hidden", !state.token);
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
  $("categories").innerHTML = data.map(item => `<button class="cat" data-id="${item.id}">${item.name}</button>`).join("");
}

async function loadList() {
  const params = new URLSearchParams({ page: String(state.page), page_size: String(state.pageSize) });
  if (state.categoryId) params.set("category_id", state.categoryId);
  if (state.keyword) params.set("keyword", state.keyword);
  const data = await request(`/news/list?${params.toString()}`);
  state.total = data.total;
  $("meta").innerText = `\u5171 ${data.total} \u6761\u65b0\u95fb`;
  $("page").innerText = `\u7b2c ${state.page} \u9875`;
  $("list").innerHTML = data.list.map(item => `
    <article class="item" data-id="${item.id}">
      <img src="${getImage(item.image)}" alt="${item.title}">
      <div>
        <h3>${item.title}</h3>
        <p>${item.description || text.noDesc}</p>
        <p>${item.category_name || text.unknownCategory} · ${item.views || 0} ${text.views}</p>
      </div>
    </article>
  `).join("");
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
  await addHistory(id);
  const isFavorite = await checkFavorite(id);
  $("detail").innerHTML = `
    <img class="detail-img" src="${getImage(data.image)}" alt="${data.title}">
    <h2>${data.title}</h2>
    <p class="muted">${data.category_name || text.unknownCategory} · ${data.author || text.unknownAuthor} · ${data.views || 0} ${text.views}</p>
    <div class="action-row">
      <button id="favoriteAction" data-id="${data.id}" data-favorite="${isFavorite ? "1" : "0"}">
        ${isFavorite ? "\u53d6\u6d88\u6536\u85cf" : "\u6536\u85cf"}
      </button>
    </div>
    <div class="ai-box">
      <div class="action-row">
        <button id="aiSummary" data-id="${data.id}">${text.aiSummary}</button>
      </div>
      <textarea id="aiQuestion" placeholder="${text.aiQuestionPlaceholder}"></textarea>
      <button id="aiAsk" data-id="${data.id}">${text.aiAsk}</button>
      <div id="aiAnswer" class="ai-answer"></div>
    </div>
    <p>${data.description || ""}</p>
    <div class="body">${data.content || ""}</div>
    <h3>\u76f8\u5173\u63a8\u8350</h3>
    ${(data.related_news || []).map(item => `
      <div class="related" data-id="${item.id}">
        <strong>${item.title}</strong>
        <p>${item.category_name || text.unknownCategory} · ${item.views || 0} ${text.views}</p>
      </div>
    `).join("") || `<p>${text.noRelated}</p>`}
  `;
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
    document.querySelectorAll(".cat").forEach(btn => btn.classList.remove("active"));
    cat.classList.add("active");
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
      alert(text.loginFirst);
      showView("profile");
      return;
    }
    $("aiAnswer").innerText = text.aiWorking;
    const data = await requestJson("/ai/news/summary", "POST", { news_id: Number(aiSummary.dataset.id) });
    $("aiAnswer").innerText = data.summary || "";
  }

  const aiAsk = event.target.closest("#aiAsk");
  if (aiAsk) {
    if (!state.token) {
      alert(text.loginFirst);
      showView("profile");
      return;
    }
    const question = $("aiQuestion").value.trim();
    if (!question) return;
    $("aiAnswer").innerText = text.aiWorking;
    const data = await requestJson("/ai/news/chat", "POST", {
      news_id: Number(aiAsk.dataset.id),
      question
    });
    $("aiAnswer").innerText = data.answer || "";
  }

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

$("search").onclick = async () => {
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
  document.querySelectorAll(".cat").forEach(btn => btn.classList.remove("active"));
  document.querySelector(".cat[data-id='']").classList.add("active");
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
