document.addEventListener("DOMContentLoaded", () => {
  const statusEl = document.getElementById("detection-status");

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const activeTab = tabs[0];
    const url = activeTab?.url || "";

    if (url.includes("reddit.com")) {
      statusEl.textContent = "✅ Reddit post detected. Ready to analyze.";
      statusEl.classList.add("real");
    } else {
      statusEl.textContent = "❌ This is not a Reddit post page.";
      statusEl.classList.add("fake");
    }
  });
});
