import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";
import * as swRegistration from "@/swRegistration";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

// Register service worker for PWA offline support
swRegistration.register({
  onSuccess: () => console.log("[Goal Kick] Ready to work offline!"),
  onUpdate: (registration) => {
    // Auto-activate the new service worker
    if (registration.waiting) {
      registration.waiting.postMessage("SKIP_WAITING");
    }
    console.log("[Goal Kick] New version available! Refreshing...");
    window.location.reload();
  },
});
