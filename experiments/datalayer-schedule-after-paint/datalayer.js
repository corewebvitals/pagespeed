// --- INP Yield Pattern Implementation ---

// This helper ensures that a function only runs after the next paint (or safe fallback)
async function awaitPaint(fn) {
    await new Promise((resolve) => {
        // Fallback timeout: ensures we don’t hang forever if RAF never fires
        setTimeout(resolve, 200); 

        // Request the next animation frame (signals readiness to paint)
        requestAnimationFrame(() => {
            // Small delay to ensure the frame is actually painted, not just queued
            setTimeout(resolve, 50);
        });
    });

    // Once the paint (or fallback) happens, run the provided function
    if (typeof fn === 'function') {
        fn();
    }
}

// --- Applying the pattern to Google Tag Manager dataLayer.push ---

// Ensure dataLayer exists
window.dataLayer = window.dataLayer || [];

if (typeof window.dataLayer.push === 'function') {
    // Preserve the original push function
    const originalDataLayerPush = window.dataLayer.push;

    // Override dataLayer.push to defer execution until after paint
    window.dataLayer.push = function (...args) {
        awaitPaint(() => {
            // Call the original push with its arguments after yielding to paint
            originalDataLayerPush.apply(window.dataLayer, args);
        });
    };
}
