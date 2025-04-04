document.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);
    const smartestId = params.get("smartest_id");

    if (!smartestId) {
      alert("SMARTTEST ID tidak ditemukan di URL.");
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:5000/smartest/${smartestId}`);
      const data = await response.json();

      // Set judul repo
      document.getElementById("repoName").textContent = `Repo: ${data.name}`;
      const repoUrlEl = document.getElementById("repoUrl");
      repoUrlEl.textContent = data.repo_url;
      repoUrlEl.href = data.repo_url;
      repoUrlEl.setAttribute("href", data.repo_url);
      repoUrlEl.setAttribute("target", "_blank");

      // Render global metrics (kiri)
      const globalList = document.getElementById("globalMetricsList");
      Object.entries(data.metric).forEach(([key, value]) => {
        let displayKey = key;

        // Ganti "Average" di awal dengan "Avg"
        if (displayKey.startsWith("Average")) {
          displayKey = displayKey.replace("Average", "Avg");
        }

        // Potong jika panjang > 10
        let shortKey = displayKey;
        if (displayKey.length > 10) {
          shortKey = displayKey.slice(0, 14) + "...";
        }

        const formattedValue = typeof value === "number" ? value.toFixed(3) : value;

        const li = document.createElement("li");
        li.innerHTML = `<strong title="${displayKey}">${shortKey}</strong> = ${formattedValue}`;
        globalList.appendChild(li);
      });

      // Build tabel per service (kanan)
      const headerRow = document.getElementById("serviceHeaderRow");
      const tableBody = document.getElementById("metricsTableBody");

      // Ambil nama-nama service
      const services = data.services;
      const serviceNames = services.map((s) => s.name);

      // Ambil semua nama metrik dari service pertama
      const allMetricNames = Object.keys(services[0].metric);

      // Header
      headerRow.innerHTML = `<th class="border px-4 py-2 text-left bg-white">Metrik</th>`;
      serviceNames.forEach((name) => {
        headerRow.innerHTML += `<th class="border px-4 py-2 text-left">${name}</th>`;
      });

      // Body
      allMetricNames.forEach((metricName) => {
        const tr = document.createElement("tr");

        // ==== Langkah 1: Ganti 'Average' di awal dengan 'Avg' ====
        let displayName = metricName;
        if (displayName.startsWith("Average")) {
          displayName = displayName.replace("Average", "Avg");
        }

        // ==== Langkah 2: Potong jika panjang lebih dari 10 karakter ====
        let shortDisplay = displayName;
        if (displayName.length > 10) {
          shortDisplay = displayName.slice(0, 7) + "...";
        }

        // ==== Langkah 3: Buat kolom nama metrik dengan tooltip ====
        tr.innerHTML = `
          <td class="border px-4 py-2 font-semibold bg-gray-50" title="${displayName}">
            ${shortDisplay}
          </td>
        `;

        // ==== Langkah 4: Tambahkan nilai dari setiap service ====
        services.forEach((service) => {
          const rawValue = service.metric[metricName];
          const value = typeof rawValue === "number" ? rawValue.toFixed(3) : "-";
          tr.innerHTML += `<td class="border px-4 py-2 text-right">${value}</td>`;
        });

        tableBody.appendChild(tr);
      });

    } catch (error) {
      console.error("Gagal fetch detail:", error);
      alert("Gagal mengambil data detail.");
    }
  });
