const form = document.querySelector("#evaluation-form");
const message = document.querySelector("#form-message");

async function loadDashboard() {
  const [statsResponse, historyResponse] = await Promise.all([fetch("/api/stats"), fetch("/api/evaluations")]);
  const stats = await statsResponse.json();
  // Analytics KPI cards
document.querySelector("#analytics-total").textContent =
    stats.total_evaluations;

document.querySelector("#analytics-a-wins").textContent =
    stats.winner_counts.A || 0;

document.querySelector("#analytics-b-wins").textContent =
    stats.winner_counts.B || 0;

document.querySelector("#analytics-ties").textContent =
    stats.winner_counts.Tie || 0;
// Calculate win-rate percentages
const total = stats.total_evaluations;
const winsA = stats.winner_counts.A || 0;
const winsB = stats.winner_counts.B || 0;
const ties = stats.winner_counts.Tie || 0;

const percentage = (value) => {
    return total > 0
        ? `${((value / total) * 100).toFixed(1)}%`
        : "0%";
};

document.querySelector("#analytics-a-rate").textContent =
    percentage(winsA);

document.querySelector("#analytics-b-rate").textContent =
    percentage(winsB);

document.querySelector("#analytics-tie-rate").textContent =
    percentage(ties);

// Average criterion scores
const criteria = stats.criteria_averages;

const criteriaLabels = [
    ["Accuracy", "accuracy"],
    ["Relevance", "relevance"],
    ["Clarity", "clarity"],
    ["Completeness", "completeness"]
];

document.querySelector("#criteria-chart").innerHTML =
    criteriaLabels.map(([label, key]) => {
        const scoreA = criteria[`${key}_a`];
        const scoreB = criteria[`${key}_b`];

        return `
            <div class="chart-row">
                <strong>${label}</strong>
                <div>Response A: ${scoreA.toFixed(2)} / 5</div>
                <div>Response B: ${scoreB.toFixed(2)} / 5</div>
            </div>
        `;
    }).join("");


// Score distribution
const distribution = stats.score_distribution;
const counts = [1, 2, 3, 4, 5].map(score => {
    const item = distribution.find(row => row.score === score);
    return item ? item.count : 0;
});

const maxCount = Math.max(...counts, 1);

document.querySelector("#distribution-chart").innerHTML =
    counts.map((count, index) => `
        <div class="distribution-row">
            <strong>${index + 1}/5</strong>
            <div class="distribution-track">
                <div class="distribution-fill"
                     style="width: ${count / maxCount * 100}%">
                </div>
            </div>
            <span>${count}</span>
        </div>
    `).join("");
  const evaluations = await historyResponse.json();
  document.querySelector("#total-count").textContent = stats.total_evaluations;
  document.querySelector("#average-score").textContent = stats.total_evaluations ? `${stats.average_score}/5` : "—";
  document.querySelector("#wins-a").textContent = stats.winner_counts.A || 0;
  document.querySelector("#wins-b").textContent = stats.winner_counts.B || 0;
  const history = document.querySelector("#history-list");
  if (!evaluations.length) {
    history.innerHTML = '<div class="empty-state">No evaluations yet. Save your first comparison above.</div>';
    return;
  }
  history.innerHTML = evaluations.map(item => `
    <article class="history-item">
        <div>
            <div class="history-prompt">
                ${escapeHtml(item.prompt)}
            </div>

            <div class="history-meta">
                A: ${Number(item.score_a).toFixed(2)}/5 |
                B: ${Number(item.score_b).toFixed(2)}/5 |
                ${new Date(item.created_at).toLocaleString()}
            </div>

            <div class="history-scores">
                <strong>Response A:</strong>
                Accuracy ${item.accuracy_a}/5 ·
                Relevance ${item.relevance_a}/5 ·
                Clarity ${item.clarity_a}/5 ·
                Completeness ${item.completeness_a}/5
            </div>

            <div class="history-scores">
                <strong>Response B:</strong>
                Accuracy ${item.accuracy_b}/5 ·
                Relevance ${item.relevance_b}/5 ·
                Clarity ${item.clarity_b}/5 ·
                Completeness ${item.completeness_b}/5
            </div>

            ${item.notes ? `<div class="history-meta">${escapeHtml(item.notes)}</div>` : ""}
        </div>

        <div>
            <span class="winner-chip">
                ${item.winner === "Tie" ? "Tie" : `Response ${item.winner} wins`}
            </span>
            <button class="delete-button" data-delete="${item.id}" type="button">
                Delete
            </button>
        </div>
    </article>
`).join("");
}
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
}
function updateOverallScores() {
    const criteria = ["accuracy", "relevance", "clarity", "completeness"];

    ["a", "b"].forEach(response => {
        const total = criteria.reduce((sum, criterion) => {
            return sum + Number(
                document.querySelector(`#${criterion}-${response}`).value
            );
        }, 0);

        const average = total / criteria.length;

        document.querySelector(`#overall-score-${response}`)
            .textContent = `${average.toFixed(2)} / 5`;
            const scoreA = criteria.reduce((sum, criterion) => {
    return sum + Number(
        document.querySelector(`#${criterion}-a`).value
    );
}, 0) / 4;

const scoreB = criteria.reduce((sum, criterion) => {
    return sum + Number(
        document.querySelector(`#${criterion}-b`).value
    );
}, 0) / 4;

const winnerSelect = document.querySelector("#winner");

if (scoreA > scoreB) {
    winnerSelect.value = "A";
} else if (scoreB > scoreA) {
    winnerSelect.value = "B";
} else {
    winnerSelect.value = "Tie";
}
    });
}

document.querySelectorAll(".criteria-section select").forEach(select => {
    select.addEventListener("change", updateOverallScores);
});

updateOverallScores();
form.addEventListener("submit", async event => {
  event.preventDefault();
  message.textContent = "Saving evaluation...";
  message.classList.remove("error");
  const payload = {
    prompt: document.querySelector("#prompt").value,
    response_a: document.querySelector("#response-a").value,
    response_b: document.querySelector("#response-b").value,
score_a: Number((
    Number(document.querySelector("#accuracy-a").value) +
    Number(document.querySelector("#relevance-a").value) +
    Number(document.querySelector("#clarity-a").value) +
    Number(document.querySelector("#completeness-a").value)
).toFixed(2)),

score_b: Number((
    Number(document.querySelector("#accuracy-b").value) +
    Number(document.querySelector("#relevance-b").value) +
    Number(document.querySelector("#clarity-b").value) +
    Number(document.querySelector("#completeness-b").value)
).toFixed(2)),

accuracy_a: Number(document.querySelector("#accuracy-a").value),
relevance_a: Number(document.querySelector("#relevance-a").value),
clarity_a: Number(document.querySelector("#clarity-a").value),
completeness_a: Number(document.querySelector("#completeness-a").value),

accuracy_b: Number(document.querySelector("#accuracy-b").value),
relevance_b: Number(document.querySelector("#relevance-b").value),
clarity_b: Number(document.querySelector("#clarity-b").value),
completeness_b: Number(document.querySelector("#completeness-b").value),

winner: document.querySelector("#winner").value,
notes: document.querySelector("#notes").value
  };
  try {
    const response = await fetch("/api/evaluations", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload)});
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || "Could not save evaluation.");
    form.reset();
    message.textContent = "Evaluation saved successfully.";
    await loadDashboard();
  } catch (error) {
    message.textContent = error.message;
    message.classList.add("error");
  }
});
document.querySelector("#refresh-button").addEventListener("click", loadDashboard);
document.querySelector("#history-list").addEventListener("click", async event => {
  const button = event.target.closest("[data-delete]");
  if (!button || !confirm("Delete this evaluation?")) return;
  const response = await fetch(`/api/evaluations/${button.dataset.delete}`, {method:"DELETE"});
  if (response.ok) await loadDashboard();
});
loadDashboard().catch(() => {
  message.textContent = "Could not load dashboard. Is the backend server running?";
  message.classList.add("error");
});
// Export evaluations to CSV
document.querySelector("#export-button").addEventListener("click", async () => {
    try {
        const response = await fetch("/api/evaluations");

        if (!response.ok) {
            throw new Error("Could not fetch evaluations.");
        }

        const evaluations = await response.json();

        if (evaluations.length === 0) {
            alert("No evaluations available to export.");
            return;
        }

        const columns = [
            "id", "prompt", "response_a", "response_b",
            "score_a", "score_b",
            "accuracy_a", "relevance_a", "clarity_a", "completeness_a",
            "accuracy_b", "relevance_b", "clarity_b", "completeness_b",
            "winner", "notes", "created_at"
        ];

        const escapeCSV = value => {
    let text = String(value ?? "");

    // Prevent spreadsheet formula injection.
    if (/^[\s]*[=+\-@\t\r]/.test(text)) {
        text = "'" + text;
    }

    return `"${text.replace(/"/g, '""')}"`;
};
        const csv = [
            columns.join(","),
            ...evaluations.map(item =>
                columns.map(column => escapeCSV(item[column])).join(",")
            )
        ].join("\n");

        const blob = new Blob(["\uFEFF" + csv], {
            type: "text/csv;charset=utf-8;"
        });

        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = url;
        link.download = "evalforge-evaluations.csv";
        link.click();

        setTimeout(() => URL.revokeObjectURL(url), 1000);

    } catch (error) {
        alert("Export failed: " + error.message);
    }
});
