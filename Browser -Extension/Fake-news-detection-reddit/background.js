chrome.tabs.onUpdated.addListener((tabId, tab) => {
  if (tab.url && tab.url.includes("reddit.com")) {
    console.log("Reddit page detected:", tab.url);
    // No message needed for Reddit yet
  }
});
