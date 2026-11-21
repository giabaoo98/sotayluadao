/* Sổ Tay Lừa Đảo — frontend */
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const TYPE_PLACEHOLDER = {
  all: "Nhập số điện thoại, số tài khoản, link website…",
  phone: "Nhập số điện thoại hoặc Zalo, VD: 0900 000 117",
  bank: "Nhập số tài khoản ngân hàng, VD: 7777 0000 1111",
  web: "Nhập tên miền website, VD: demo-shop-gia-re",
  social: "Nhập link hoặc tên tài khoản Facebook / TikTok",
};

let currentType = "all";

/* ---------------- utils ---------------- */
const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const vnd = (n) =>
  n > 0 ? new Intl.NumberFormat("vi-VN").format(n) + "đ" : "—";

const compact = (n) => {
  const f = (v) => v.toFixed(1).replace(/\.0$/, "").replace(".", ",");
  return n >= 1e9 ? f(n / 1e9) + " tỷ"
    : n >= 1e6 ? f(n / 1e6) + " triệu"
    : n >= 1e3 ? Math.round(n / 1e3) + "k"
    : String(n);
};

function timeAgo(str) {
  if (!str) return "";
  const d = new Date(str.replace(" ", "T"));
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 3600) return Math.max(1, Math.floor(diff / 60)) + " phút trước";
  if (diff < 86400) return Math.floor(diff / 3600) + " giờ trước";
  if (diff < 2592000) return Math.floor(diff / 86400) + " ngày trước";
  return d.toLocaleDateString("vi-VN");
}

function toast(msg) {
  let el = $(".toast");
  if (!el) {
    el = document.createElement("div");
    el.className = "toast";
    document.body.appendChild(el);
  }
  el.textContent = msg;
  requestAnimationFrame(() => el.classList.add("show"));
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove("show"), 2600);
}

async function api(path, opts) {
  const res = await fetch(path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Có lỗi xảy ra, vui lòng thử lại.");
  return data;
}

/* ---------------- stats ---------------- */
function setStat(el, value) {
  el.textContent = Number(value || 0).toLocaleString("vi-VN");
  el.classList.add("stat-in");
}

async function loadStats() {
  try {
    const s = await api("/api/stats");
    setStat($("#st-reports"), s.total_reports);
    setStat($("#st-targets"), s.total_targets || 0);
    $("#st-amount").textContent = compact(s.total_amount);
  } catch {
    /* im lặng */
  }
}

/* ---------------- ticker ---------------- */
async function loadTicker() {
  try {
    const { items } = await api("/api/alerts");
    const track = $("#ticker-track");
    const html = items.map((t) => `<span>${esc(t)}</span>`).join("");
    track.innerHTML = html + html;
  } catch { /* im lặng */ }
}

/* ---------------- search ---------------- */
function riskBadge(risk) {
  return `<span class="risk-badge risk-${risk.key}"><i></i>${esc(risk.label)}</span>`;
}

function renderResults(data) {
  const section = $("#ket-qua");
  const box = $("#results");
  const title = $("#results-title");
  const sub = $("#results-sub");
  section.hidden = false;

  title.textContent = `Kết quả cho “${data.query}”`;
  sub.textContent =
    data.count > 0
      ? `Tìm thấy ${data.count} đối tượng khớp trong cơ sở dữ liệu đã kiểm duyệt.`
      : "Không tìm thấy dữ liệu trùng khớp.";

  if (!data.count) {
    box.innerHTML = `
      <div class="empty-state">
        <h3>Chưa có báo cáo nào cho thông tin này</h3>
        <p class="muted">
          Đây <b>không</b> phải là xác nhận an toàn. Đối tượng có thể mới hoạt động hoặc dùng thông tin khác.
          Hãy kiểm tra thêm: tên chủ tài khoản có khớp tên đơn vị bán không, có yêu cầu chuyển tiền ngoài luồng không,
          và luôn giữ lại bằng chứng giao dịch.
        </p>
        <button class="btn btn-outline btn-sm" data-open-report>Báo cáo đối tượng này</button>
      </div>`;
    box.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }

  box.innerHTML = data.matches
    .map(
      (m) => `
      <article class="result-card">
        <div class="result-head">
          ${riskBadge(m.risk)}
          <div class="result-main">
            <div class="result-target">${esc(m.target)}</div>
            <div class="result-meta">
              <span>${esc(m.type_label)}</span>
              <span>Báo cáo gần nhất: <b>${esc(timeAgo(m.last_report))}</b></span>
            </div>
          </div>
          <div class="result-stats">
            <div><b>${m.report_count}</b><span>báo cáo</span></div>
            <div><b>${vnd(m.total_amount)}</b><span>thiệt hại</span></div>
          </div>
        </div>
        <div class="reports-list">
          ${m.reports
            .map(
              (r) => `
            <div class="report-item">
              <h4>${esc(r.title)}</h4>
              <p>${esc(r.reason)}</p>
              <div class="report-foot">
                ${r.channel ? `<span class="tag">${esc(r.channel)}</span>` : ""}
                ${r.amount ? `<span>Thiệt hại: <b>${vnd(r.amount)}</b></span>` : ""}
                <span>${esc(r.created_at)}</span>
                <span>Người gửi: ${esc(r.alias || "Ẩn danh")}</span>
              </div>
            </div>`
            )
            .join("")}
        </div>
      </article>`
    )
    .join("");

  box.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function doSearch(q, type = currentType) {
  q = (q || "").trim();
  if (q.length < 2) {
    toast("Nhập ít nhất 2 ký tự để tra cứu.");
    return;
  }
  $("#results").innerHTML = `<div class="skeleton" style="height:150px"></div>`;
  $("#ket-qua").hidden = false;
  try {
    const data = await api(`/api/search?q=${encodeURIComponent(q)}&type=${encodeURIComponent(type)}`);
    renderResults(data);
    const url = new URL(location.href);
    url.searchParams.set("q", q);
    if (type !== "all") url.searchParams.set("type", type);
    else url.searchParams.delete("type");
    history.replaceState(null, "", url);
  } catch (e) {
    toast(e.message);
  }
}

/* ---------------- top + recent ---------------- */
async function loadTop() {
  try {
    const { items } = await api("/api/top?limit=6");
    $("#top-list").innerHTML = items
      .map(
        (it) => `
      <article class="wcard" data-target="${esc(it.target)}">
        <div class="wcard-top">
          ${riskBadge(it.risk)}
          <span class="wcard-meta">${esc(it.type_label)}</span>
        </div>
        <div class="wcard-target">${esc(it.target)}</div>
        <div class="wcard-meta">Báo cáo gần nhất ${esc(timeAgo(it.last_report))}</div>
        <div class="wcard-foot">
          <span><b>${it.report_count}</b> báo cáo</span>
          <span><b>${vnd(it.total_amount)}</b></span>
        </div>
      </article>`
      )
      .join("");
    $$("#top-list .wcard").forEach((el) =>
      el.addEventListener("click", () => {
        $("#q").value = el.dataset.target;
        doSearch(el.dataset.target, "all");
      })
    );
  } catch { /* im lặng */ }
}

async function loadRecent() {
  try {
    const { items } = await api("/api/recent?limit=10");
    $(".table tbody").innerHTML = items
      .map(
        (r) => `
      <tr>
        <td class="t-target" data-label="Đối tượng">${esc(r.target)}</td>
        <td data-label="Loại"><span class="tag" style="background:#eef1f6;color:#475467;border-radius:6px;padding:2px 8px;font-size:12px;font-weight:600">${esc(r.type_label)}</span></td>
        <td class="t-reason" data-label="Nội dung"><span><b>${esc(r.title)}</b><br><span class="muted">${esc(r.reason)}</span></span></td>
        <td class="num" data-label="Thiệt hại">${vnd(r.amount)}</td>
        <td class="muted" data-label="Thời gian" style="white-space:nowrap">${esc(timeAgo(r.created_at))}</td>
      </tr>`
      )
      .join("");
  } catch { /* im lặng */ }
}

/* ---------------- menu di động ---------------- */
const menuBtn = $("#menu-btn");
const nav = $("#nav");

function closeMenu() {
  if (!nav || !nav.classList.contains("open")) return;
  nav.classList.remove("open");
  menuBtn.setAttribute("aria-expanded", "false");
}

if (menuBtn) {
  menuBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    const open = nav.classList.toggle("open");
    menuBtn.setAttribute("aria-expanded", String(open));
  });
  nav.addEventListener("click", (e) => {
    if (e.target.closest("a, button")) closeMenu();
  });
  document.addEventListener("click", (e) => {
    if (!e.target.closest("#nav") && !e.target.closest("#menu-btn")) closeMenu();
  });
  window.addEventListener("resize", () => {
    if (window.innerWidth > 900) closeMenu();
  });
}

/* ---------------- tabs ---------------- */
$$(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    $$(".tab").forEach((t) => t.classList.remove("is-active"));
    tab.classList.add("is-active");
    currentType = tab.dataset.type;
    $("#q").placeholder = TYPE_PLACEHOLDER[currentType] || TYPE_PLACEHOLDER.all;
  });
});

$$("[data-sample]").forEach((b) =>
  b.addEventListener("click", () => {
    $("#q").value = b.dataset.sample;
    doSearch(b.dataset.sample, "all");
  })
);

$("#search-form").addEventListener("submit", (e) => {
  e.preventDefault();
  doSearch($("#q").value);
});

$("#clear-results").addEventListener("click", () => {
  $("#ket-qua").hidden = true;
  $("#q").value = "";
  const url = new URL(location.href);
  url.searchParams.delete("q");
  url.searchParams.delete("type");
  history.replaceState(null, "", url);
  $("#tra-cuu").scrollIntoView({ behavior: "smooth" });
});

/* ---------------- modal ---------------- */
function openReport(prefill) {
  const modal = $("#report-modal");
  modal.hidden = false;
  document.body.style.overflow = "hidden";
  if (prefill) {
    const el = $("#report-form").elements;
    if (prefill.target) el.target.value = prefill.target;
    if (prefill.type) el.type.value = prefill.type;
  }
  setTimeout(() => $("#report-form").elements.target.focus(), 60);
}
function closeReport() {
  $("#report-modal").hidden = true;
  document.body.style.overflow = "";
}
document.addEventListener("click", (e) => {
  if (e.target.closest("[data-open-report]")) {
    e.preventDefault();
    openReport();
  }
  if (e.target.closest("[data-close-report]")) {
    e.preventDefault();
    closeReport();
  }
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !$("#report-modal").hidden) closeReport();
});

$("#report-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target;
  const el = f.elements;
  const status = $("#report-status");
  const btn = f.querySelector('button[type="submit"]');
  status.textContent = "";
  status.className = "form-status";
  btn.disabled = true;
  btn.textContent = "Đang gửi…";
  try {
    const body = {
      type: el.type.value,
      target: el.target.value,
      title: el.title.value,
      reason: el.reason.value,
      amount: Number(el.amount.value || 0),
      channel: el.channel.value,
      evidence: el.evidence.value,
      alias: el.alias.value || "Ẩn danh",
    };
    const res = await api("/api/reports", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    status.textContent = `Đã ghi nhận báo cáo #${res.id}. ${res.message}`;
    status.classList.add("ok");
    f.reset();
    toast("Cảm ơn bạn, báo cáo đang chờ kiểm duyệt.");
  } catch (err) {
    status.textContent = err.message;
    status.classList.add("err");
  } finally {
    btn.disabled = false;
    btn.textContent = "Gửi báo cáo";
  }
});

/* ---------------- init ---------------- */
$("#year").textContent = new Date().getFullYear();
loadStats();
loadTicker();
loadTop();
loadRecent();

if (location.hash === "#bao-cao") openReport();

const params = new URLSearchParams(location.search);
if (params.get("q")) {
  $("#q").value = params.get("q");
  if (params.get("type")) {
    currentType = params.get("type");
    $$(".tab").forEach((t) => t.classList.toggle("is-active", t.dataset.type === currentType));
  }
  doSearch(params.get("q"), currentType);
}
