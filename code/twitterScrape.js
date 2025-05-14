// Observer for tweets entering viewport (scroll detection only)
const tweetObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const tweet = entry.target;

            // === Extract tweet content with emojis ===
            const contentElement = tweet.querySelector('div[lang]');
            let tweetText = "";
            if (contentElement) {
                let rawHTML = contentElement.innerHTML;
                // Replace <img> emojis with their alt text
                rawHTML = rawHTML.replace(/<img[^>]*alt="([^"]+)"[^>]*>/g, '$1');
                // Strip HTML tags
                tweetText = rawHTML.replace(/<[^>]+>/g, '').trim();
            }

            // === Extract image URLs (excluding avatars/emojis) ===
            const imageElements = tweet.querySelectorAll('img');
            const imageUrls = Array.from(imageElements)
                .map(img => img.src)
                .filter(src => !src.includes('profile_images') && !src.includes('emoji') && !src.includes('abs.twimg.com'));

            // === Extract interaction counts ===
            const replies = tweet.querySelector('[data-testid="reply"]')?.innerText || '0';
            const retweets = tweet.querySelector('[data-testid="retweet"]')?.innerText || '0';
            const likes = tweet.querySelector('[data-testid="like"]')?.innerText || '0';
            const views = tweet.querySelector('[data-testid="viewCount"]')?.innerText || '0';

            console.log("👀 Tweet now visible:", tweetText);
            if (imageUrls.length > 0) {
                console.log("🖼️ Images:", imageUrls);
            }
            console.log(`💬 Replies: ${replies} 🔁 Retweets: ${retweets} ❤️ Likes: ${likes} 👁️ Views: ${views}`);
        }
    });
}, { threshold: 0.5 });

// Attach observer to currently loaded tweets
document.querySelectorAll('article[role="article"]').forEach(tweet => {
    tweetObserver.observe(tweet);
});

// Observer to detect new tweets being added to the page
const observer = new MutationObserver(() => {
    document.querySelectorAll('article[role="article"]').forEach(tweet => {
        tweetObserver.observe(tweet); // make sure all new tweets are observed
    });
});

observer.observe(document.body, { childList: true, subtree: true });
