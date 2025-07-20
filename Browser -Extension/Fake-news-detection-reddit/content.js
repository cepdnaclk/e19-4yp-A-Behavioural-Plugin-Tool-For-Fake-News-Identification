(() => {
    console.log("✅ Content script loaded");

    const seenPostIds = new Set();

    // Extract postId from the <shreddit-post id="t3_xxx">
    const extractPostId = (element) => {
        const idAttr = element.getAttribute("id");
        if (idAttr && idAttr.startsWith("t3_")) {
            return idAttr.substring(3);
        }
        return null;
    };

    // Inject Fake News button next to the new Share button
    const injectFakeNewsButton = (postEl, postId) => {
        // Access the shadow root
        const shadow = postEl.shadowRoot;
        if (!shadow) {
            console.warn(`⚠️ No shadowRoot found for post: ${postId}`);
            return;
        }

        // Find the action row
        const actionRow = shadow.querySelector('div[data-testid="action-row"]');
        if (!actionRow) {
            console.warn(`⚠️ Action row not found in post: ${postId}`);
            return;
        }

        // Find the Share button (adjust selector as needed)
        const shareBtn = actionRow.querySelector('shreddit-post-share-button');
        if (!shareBtn) {
            console.warn(`⚠️ Share button not found in action row for post: ${postId}`);
            return;
        }

        // Prevent duplicates
        if (actionRow.querySelector(`.fakenews-button[data-id="${postId}"]`)) return;

        console.log("✅ Injecting Analyze button for post:", postId);

        const btn = document.createElement("button");
        btn.className = "flex flex-row justify-center items-center h-xl font-semibold relative fakenews-button";
        btn.dataset.id = postId;

        // Use relative path from the extension root (Chrome will resolve it)
        const iconUrl = chrome.runtime.getURL("assets/search.png");

        btn.innerHTML = `<img src="${iconUrl}" alt="Search Icon" style="width: 26px; height: 26px; margin-right: 6px; vertical-align: middle;">Check News`;

        Object.assign(btn.style, {
            marginLeft: "8px",
            padding: "4px 8px",
            fontSize: "12px",
            border: "1px solid #ccc",
            borderRadius: "16px",
            backgroundColor: "#e2e3e5",
            cursor: "pointer",
            display: "flex",
            alignItems: "center"
        });

        const resultSpan = document.createElement("span");
        Object.assign(resultSpan.style, {
            marginLeft: "8px",
            fontWeight: "bold",
        });

        btn.addEventListener("click", async () => {
            console.log("🔍 Button clicked:", postId);
            resultSpan.textContent = "⏳ Analyzing...";
            resultSpan.style.color = "black";

            try {
                const API_BASE_URL =
                    location.hostname === "localhost"
                        ? "http://localhost:8000"
                        : "https://75a0bffeb671.ngrok-free.app";

                const response = await fetch(`${API_BASE_URL}/analyze`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ post_id: postId })
                });

                if (!response.ok) {
                    throw new Error("API Error");
                }

                const result = await response.json();
                const label = result.label;
                const confidence = result.confidence;

                if (label === "FAKE") {
                    resultSpan.textContent = `🚫 Fake (${confidence * 100}%)`;
                    resultSpan.style.color = "red";
                } else {
                    resultSpan.textContent = `✅ Real (${confidence * 100}%)`;
                    resultSpan.style.color = "green";
                }
            } catch (err) {
                console.error("❌ Error analyzing post:", err);
                resultSpan.textContent = "❌ Error";
                resultSpan.style.color = "gray";
            }
        });


        // Inject button after the Share button
        shareBtn.after(btn);
        btn.after(resultSpan);
    };


    // Observe new posts and inject buttons
    const observeNewPosts = () => {
        const posts = document.querySelectorAll('shreddit-post[id^="t3_"]:not(.observed-fakenews)');
        console.log("🔍 Scanning for new posts:", posts.length);

        posts.forEach((postEl) => {
            console.log("🔍 Found post element:", postEl);
            const postId = extractPostId(postEl);
            if (postId && !seenPostIds.has(postId)) {
                seenPostIds.add(postId);
                injectFakeNewsButton(postEl, postId);
                postEl.classList.add("observed-fakenews");
            }
        });
    };

    // Initial + scroll scan
    observeNewPosts();

    window.addEventListener("scroll", () => {
        setTimeout(observeNewPosts, 500);
    });

    // Retry scan for dynamic loading
    let retries = 0;
    const interval = setInterval(() => {
        observeNewPosts();
        retries++;
        if (retries > 10) clearInterval(interval);
    }, 1000);
})();
