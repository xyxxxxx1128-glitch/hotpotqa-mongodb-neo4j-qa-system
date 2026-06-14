const API_BASE = window.API_BASE || "http://127.0.0.1:8000";

const state = {
  usingSampleData: false,
  selectedQuestionId: null,
  graphChart: null,
  typeChart: null,
  levelChart: null,
};

const elements = {
  keyword: document.querySelector("#keyword"),
  searchButton: document.querySelector("#searchButton"),
  status: document.querySelector("#status"),
  resultList: document.querySelector("#resultList"),
  questionTitle: document.querySelector("#questionTitle"),
  answerText: document.querySelector("#answerText"),
  detailMeta: document.querySelector("#detailMeta"),
  pathList: document.querySelector("#pathList"),
};

document.addEventListener("DOMContentLoaded", async () => {
  state.graphChart = echarts.init(document.querySelector("#graphChart"));
  state.typeChart = echarts.init(document.querySelector("#typeChart"));
  state.levelChart = echarts.init(document.querySelector("#levelChart"));

  elements.searchButton.addEventListener("click", () => runSearch());
  elements.keyword.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      runSearch();
    }
  });

  window.addEventListener("resize", () => {
    state.graphChart.resize();
    state.typeChart.resize();
    state.levelChart.resize();
  });

  await runSearch();
  await loadClusters();
});

async function apiGet(path) {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

async function runSearch() {
  const keyword = elements.keyword.value.trim();
  setStatus("正在检索...");
  try {
    const questions = await apiGet(`/api/search?q=${encodeURIComponent(keyword)}&limit=20`);
    state.usingSampleData = false;
    renderResults(questions);
    setStatus("已连接 FastAPI + MongoDB + Neo4j 后端");
  } catch (error) {
    const questions = window.SAMPLE_DATA.questions.filter((item) => {
      const text = `${item.question} ${item.answer} ${item.type} ${item.level}`.toLowerCase();
      return text.includes(keyword.toLowerCase());
    });
    state.usingSampleData = true;
    renderResults(questions);
    setStatus("当前使用 GitHub Pages 静态展示数据");
  }
}

function renderResults(questions) {
  elements.resultList.innerHTML = "";
  if (questions.length === 0) {
    elements.resultList.innerHTML = '<div class="empty">没有检索到相关问题</div>';
    return;
  }

  questions.forEach((item, index) => {
    const button = document.createElement("button");
    button.className = "result-item";
    button.innerHTML = `
      <span class="result-index">${index + 1}</span>
      <span class="result-content">
        <strong>${escapeHtml(item.question)}</strong>
        <small>答案：${escapeHtml(item.answer || "未知")} / 类型：${escapeHtml(
          item.type || "unknown"
        )} / 难度：${escapeHtml(item.level || "unknown")}</small>
      </span>
    `;
    button.addEventListener("click", () => loadQuestionGraph(item.id));
    elements.resultList.appendChild(button);
  });

  loadQuestionGraph(questions[0].id);
}

async function loadQuestionGraph(questionId) {
  state.selectedQuestionId = questionId;
  let graph;
  if (state.usingSampleData) {
    graph = window.SAMPLE_DATA.graphs[questionId];
  } else {
    graph = await apiGet(`/api/question/${encodeURIComponent(questionId)}/graph`);
  }
  renderQuestionDetail(graph);
  renderGraph(graph);
}

function renderQuestionDetail(graph) {
  if (!graph || !graph.question) {
    return;
  }
  elements.questionTitle.textContent = graph.question.text || graph.question.question || "";
  elements.answerText.textContent = graph.answer || "暂无答案";
  elements.detailMeta.textContent = `类型：${graph.question.type || "unknown"} / 难度：${
    graph.question.level || "unknown"
  }`;

  const sentenceNodes = graph.nodes.filter((node) => node.category === "Sentence");
  elements.pathList.innerHTML = sentenceNodes
    .map((node, index) => `<li>第 ${index + 1} 跳证据：${escapeHtml(node.name)}</li>`)
    .join("");
}

function renderGraph(graph) {
  const categories = [
    { name: "Question" },
    { name: "Document" },
    { name: "Sentence" },
    { name: "Answer" },
  ];
  const categoryIndex = new Map(categories.map((item, index) => [item.name, index]));
  const data = graph.nodes.map((node) => ({
    id: node.id,
    name: node.name,
    value: node.name,
    category: categoryIndex.get(node.category) ?? 0,
    symbolSize: node.category === "Question" ? 58 : node.category === "Answer" ? 48 : 38,
    label: {
      show: true,
      formatter: truncate(node.name, 32),
    },
  }));

  state.graphChart.setOption({
    tooltip: {
      formatter(params) {
        if (params.dataType === "edge") {
          return params.data.name;
        }
        return `${params.data.value}`;
      },
    },
    legend: [{ data: categories.map((item) => item.name), top: 8 }],
    series: [
      {
        type: "graph",
        layout: "force",
        roam: true,
        categories,
        data,
        links: graph.links.map((link) => ({
          source: link.source,
          target: link.target,
          name: link.name,
          label: { show: true, formatter: link.name },
        })),
        force: {
          repulsion: 420,
          edgeLength: 150,
        },
        lineStyle: {
          color: "#7a869a",
          width: 1.4,
          curveness: 0.08,
        },
        edgeSymbol: ["none", "arrow"],
        edgeSymbolSize: 7,
      },
    ],
  });
}

async function loadClusters() {
  let typeData;
  let levelData;
  try {
    typeData = await apiGet("/api/clusters/type");
    levelData = await apiGet("/api/clusters/level");
  } catch (error) {
    typeData = window.SAMPLE_DATA.clusters.type;
    levelData = window.SAMPLE_DATA.clusters.level;
  }
  renderBarChart(state.typeChart, "问题类型聚类", typeData, "类型");
  renderBarChart(state.levelChart, "问题难度聚类", levelData, "难度");
}

function renderBarChart(chart, title, data, xAxisName) {
  chart.setOption({
    title: {
      text: title,
      left: "center",
      top: 8,
      textStyle: { fontSize: 16, fontWeight: 700, color: "#142033" },
    },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      valueFormatter: (value) => `${Number(value).toLocaleString()} 条`,
    },
    grid: { left: 92, right: 28, top: 64, bottom: 48, containLabel: false },
    xAxis: {
      type: "category",
      name: xAxisName,
      nameLocation: "middle",
      nameGap: 30,
      data: data.map((item) => item.name),
      axisLabel: { color: "#475467", fontSize: 12 },
      axisLine: { lineStyle: { color: "#98a2b3" } },
    },
    yAxis: {
      type: "value",
      name: "数量（条）",
      nameGap: 48,
      nameTextStyle: { color: "#475467", fontWeight: 700 },
      axisLabel: {
        color: "#475467",
        formatter: (value) => Number(value).toLocaleString(),
        margin: 14,
      },
      splitLine: { lineStyle: { color: "#e4eaf2" } },
    },
    series: [
      {
        type: "bar",
        data: data.map((item) => item.count),
        barMaxWidth: 80,
        label: {
          show: true,
          position: "top",
          color: "#142033",
          fontWeight: 700,
          formatter: (params) => Number(params.value).toLocaleString(),
        },
        itemStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "#2563eb" },
              { offset: 1, color: "#0f766e" },
            ],
          },
          borderRadius: [6, 6, 0, 0],
        },
      },
    ],
  });
}

function setStatus(message) {
  elements.status.textContent = message;
}

function truncate(text, length) {
  if (!text) return "";
  return text.length > length ? `${text.slice(0, length)}...` : text;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
