/**
 * AI-CHA – Chat window logic
 * ==========================
 * Manages the conversation state and communicates with the FastAPI backend.
 *
 * Configuration
 * -------------
 * Change API_BASE_URL if your backend runs on a different host / port.
 */

"use strict";

/* ── Configuration ─────────────────────────────────────────────────────── */

/** Base URL of the FastAPI backend. */
const API_BASE_URL = "http://127.0.0.1:8000";

/* ── State ──────────────────────────────────────────────────────────────── */

/**
 * Conversation history sent with every request so the model has context.
 * Each entry: { role: "user" | "assistant", content: string }
 * @type {Array<{role: string, content: string}>}
 */
const history = [];

/* ── DOM helpers ────────────────────────────────────────────────────────── */

const chatMessages = /** @type {HTMLElement} */ (document.getElementById("chatMessages"));
const userInput    = /** @type {HTMLTextAreaElement} */ (document.getElementById("userInput"));
const sendBtn      = /** @type {HTMLButtonElement} */ (document.getElementById("sendBtn"));

/**
 * Append a chat bubble to the message thread and scroll into view.
 *
 * @param {"user"|"assistant"|"typing"} role
 * @param {string} text
 * @returns {HTMLElement} The created bubble element.
 */
function appendMessage(role, text) {
  const bubble = document.createElement("div");
  bubble.classList.add("message", role);
  bubble.textContent = text;
  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return bubble;
}

/**
 * Auto-grow the textarea to fit its content (up to its CSS max-height).
 */
function autoResizeTextarea() {
  userInput.style.height = "auto";
  userInput.style.height = `${userInput.scrollHeight}px`;
}

/* ── Send message ───────────────────────────────────────────────────────── */

/**
 * Read the user's input, send it to the backend, and display the reply.
 * Disables the input controls while a request is in-flight.
 */
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  // Show the user's bubble immediately.
  appendMessage("user", text);
  history.push({ role: "user", content: text });

  // Clear input and disable controls while waiting.
  userInput.value = "";
  autoResizeTextarea();
  setControlsEnabled(false);

  // Optimistic "typing…" indicator.
  const typingBubble = appendMessage("typing", "AI-CHA is thinking…");

  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, history: history.slice(0, -1) }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Server error ${response.status}`);
    }

    const data = await response.json();
    const reply = data.reply || "(no response)";

    // Replace the typing indicator with the actual reply.
    typingBubble.remove();
    appendMessage("assistant", reply);
    history.push({ role: "assistant", content: reply });

  } catch (err) {
    typingBubble.remove();
    appendMessage("assistant", `⚠️ Error: ${err.message}`);
  } finally {
    setControlsEnabled(true);
    userInput.focus();
  }
}

/**
 * Enable or disable the send button and textarea.
 *
 * @param {boolean} enabled
 */
function setControlsEnabled(enabled) {
  sendBtn.disabled = !enabled;
  userInput.disabled = !enabled;
}

/* ── Event listeners ────────────────────────────────────────────────────── */

// Send on button click.
sendBtn.addEventListener("click", sendMessage);

// Send on Enter; Shift+Enter inserts a newline.
userInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
});

// Grow textarea as the user types.
userInput.addEventListener("input", autoResizeTextarea);

/* ── Initial greeting ───────────────────────────────────────────────────── */

appendMessage("assistant", "Hello! I'm AI-CHA. How can I help you today?");
