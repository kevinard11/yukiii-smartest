document.addEventListener("DOMContentLoaded", () => {
    const urlForm = document.getElementById("urlForm");
    const urlInput = document.getElementById("urlInput");
    const errorMsg = document.getElementById("errorMsg");
    const submitBtn = document.getElementById("submitBtn");
    const latestList = document.getElementById("latestList");

    const SMARTEST_URL = "http://localhost:5000/smartest";

    // Load latest submissions on page load
    loadLatest();

    urlForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      errorMsg.classList.add("hidden");
      submitBtn.disabled = true;
      submitBtn.textContent = "Submitting...";

      try {
        const response = await fetch(SMARTEST_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            is_print: true,
            repo_url: urlInput.value.trim(),
          }),
        });

        if (!response.ok) {
          let errorMessage = "Failed to submit";
          try {
            const errorData = await response.json();
            errorMessage = errorData.message || errorMessage;
          } catch (jsonError) {
            // Kalau gagal parse JSON, biarkan pakai error default
          }
          throw new Error(errorMessage);
        }

        const data = await response.json();
        console.log("Submitted. SMARTTEST ID:", data.smartest_id);

        // Refresh latest list
        await loadLatest();

        // Optional: Redirect to detail page
        // window.location.href = `/detail.html?smartest_id=${data.smartest_id}`;

      } catch (err) {
        errorMsg.textContent = err.message || "Something went wrong";
        errorMsg.classList.remove("hidden");
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Submit";
        urlInput.value = "";
      }
    });

    async function loadLatest() {
      latestList.innerHTML = '<p class="text-gray-500">Loading...</p>';
      try {
        const response = await fetch(SMARTEST_URL);
        const data = await response.json();

        if (data.length === 0) {
          latestList.innerHTML = "<p class='text-gray-500'>Belum ada data.</p>";
          return;
        }

        latestList.innerHTML = "";
        data.forEach((item) => {
          const li = document.createElement("li");
          li.className = "p-4 bg-white border rounded-lg shadow hover:bg-blue-50 transition";
          li.innerHTML = `
            <div class="flex flex-col">
              <span class="font-bold">${item.name}</span>
              <span class="text-sm text-gray-600">${item.repo_url}</span>
              <a href="detail.html?smartest_id=${item.smartest_id}" class="text-blue-600 text-sm mt-1 hover:underline">Lihat Detail</a>
            </div>
          `;
          latestList.appendChild(li);
        });
      } catch (err) {
        latestList.innerHTML = "<p class='text-red-500'>Gagal memuat data terbaru.</p>";
      }
    }
  });
