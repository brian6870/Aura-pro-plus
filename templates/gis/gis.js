// static/gis/gis.js

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const resultDiv = document.getElementById("result");

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const fileInput = form.querySelector('input[name="soil_file"]');
    if (!fileInput.files.length) {
      showError("Please upload a file first.");
      return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("soil_file", file);

    try {
      resultDiv.style.display = "block";
      resultDiv.innerHTML = "<p>⏳ Analyzing soil data... please wait.</p>";

      const response = await fetch("/gis/api/analyze-soil", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Server error: ${text}`);
      }

      const data = await response.json();
      displayResult(data);
    } catch (err) {
      showError(`❌ ${err.message}`);
    }
  });

  function displayResult(data) {
    if (!data || typeof data !== "object") {
      showError("Invalid response received from server.");
      return;
    }

    resultDiv.innerHTML = `
      <div class="result-card">
        <h3>Soil Analysis Result</h3>
        <ul>
          <li><strong>Location:</strong> ${data.location || "N/A"}</li>
          <li><strong>pH:</strong> ${data.ph || "N/A"}</li>
          <li><strong>Nitrogen:</strong> ${data.nitrogen || "N/A"}</li>
          <li><strong>Phosphorus:</strong> ${data.phosphorus || "N/A"}</li>
          <li><strong>Potassium:</strong> ${data.potassium || "N/A"}</li>
        </ul>
      </div>
    `;
  }

  function showError(message) {
    resultDiv.style.display = "block";
    resultDiv.innerHTML = `<p class="error">${message}</p>`;
  }
});
