document.addEventListener("DOMContentLoaded", function () {
    // ===================== RADAR CHART (3 ROLE) =====================
    const radarCanvas = document.getElementById("radarChart");
    if (radarCanvas && window.Chart) {
        try {
            const scoresRaw = radarCanvas.getAttribute("data-role-scores") || "{}";
            const scores = JSON.parse(scoresRaw);

            const labels = [];
            const dataValues = [];

            Object.entries(scores).forEach(([key, value]) => {
                const label = key
                    .split("_")
                    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
                    .join(" ");
                labels.push(label);
                dataValues.push(value || 0);
            });

            if (labels.length > 0) {
                new Chart(radarCanvas, {
                    type: "radar",
                    data: {
                        labels: labels,
                        datasets: [{
                            label: "Kecocokan per Role (%)",
                            data: dataValues,
                            fill: true,
                            backgroundColor: "rgba(37, 99, 235, 0.20)",
                            borderColor: "rgba(37, 99, 235, 1)",
                            pointBackgroundColor: "rgba(37, 99, 235, 1)",
                            pointBorderColor: "#fff",
                            pointHoverBackgroundColor: "#fff",
                            pointHoverBorderColor: "rgba(37, 99, 235, 1)"
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            r: {
                                beginAtZero: true,
                                min: 0,
                                max: 100,
                                ticks: {
                                    stepSize: 20
                                },
                                grid: {
                                    circular: true   // ⬅ grid jadi lingkaran
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
            }
        } catch (e) {
            console.error("Error building radar chart:", e);
        }
    }

    // ===================== WORD CLOUD =====================
    const wcElement = document.getElementById("wordcloud");
    if (wcElement && window.WordCloud) {
        let keywords = [];
        try {
            const raw = wcElement.getAttribute("data-keywords") || "[]";
            const parsed = JSON.parse(raw);
            if (Array.isArray(parsed)) {
                keywords = parsed;
            }
        } catch (e) {
            console.error("Error parsing keywords for wordcloud:", e);
        }

        if (keywords.length > 0) {
            const list = keywords.map((w, idx) => {
                const base = keywords.length - idx;
                const weight = base + 10;
                return [w, weight];
            });

            WordCloud(wcElement, {
                list: list,
                gridSize: 10,
                weightFactor: 2,
                shrinkToFit: true,
                backgroundColor: "rgba(0,0,0,0)",
                color: function () {
                    const colors = [
                        "#1d4ed8", "#2563eb", "#0f766e",
                        "#9333ea", "#b45309", "#be123c"
                    ];
                    return colors[Math.floor(Math.random() * colors.length)];
                }
            });
        } else {
            wcElement.innerHTML =
                "<span class='text-muted'>Tidak ada keyword yang cukup untuk word cloud.</span>";
        }
    } else if (wcElement && !window.WordCloud) {
        wcElement.innerHTML =
            "<span class='text-muted'>Library word cloud belum termuat.</span>";
    }
});
