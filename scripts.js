document.addEventListener("DOMContentLoaded", function() {
  const chatToggleBtn = document.getElementById("chat-toggle");
  const chatbotContainer = document.getElementById("chatbot-container");
  const chatCloseBtn = document.getElementById("chat-close");
  const chatBody = document.getElementById("chat-body");
  const chatInput = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const micBtn = document.getElementById("mic-btn");
  const langSelect = document.getElementById("chat-language");

  function toggleChatbot() {
    if (!chatbotContainer) return;
    chatbotContainer.classList.toggle('open');
    if (chatbotContainer.classList.contains('open')) chatInput.focus();
  }

  if (chatToggleBtn) chatToggleBtn.addEventListener("click", toggleChatbot);
  if (chatCloseBtn) chatCloseBtn.addEventListener("click", toggleChatbot);

  function appendMessage(role, text) {
    if (!chatBody) return;
    const msg = document.createElement("div");
    msg.className = "chat-message " + (role === "user" ? "from-user" : "from-assistant");
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;
    msg.appendChild(bubble);
    chatBody.appendChild(msg);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  async function sendMessage() {
    if (!chatInput || !langSelect) return;
    const text = chatInput.value.trim();
    if (!text) return;
    appendMessage("user", text);
    chatInput.value = "";
    appendMessage("assistant", "Thinking...");

    try {
      const res = await fetch("/chat", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({message: text, language: langSelect.value})
      });
      const data = await res.json();

      // Remove last "Thinking..." bubble
      const lastBubble = chatBody.querySelectorAll(".from-assistant .bubble");
      if (lastBubble.length) lastBubble[lastBubble.length-1].parentNode.remove();

      appendMessage("assistant", data.error ? "Error: " + data.error : data.reply);

      if (window.speechSynthesis && data.reply) {
        const utter = new SpeechSynthesisUtterance(data.reply);
        const langMap = {en:"en-US", hi:"hi-IN", es:"es-ES", ta:"ta-IN"};
        utter.lang = langMap[langSelect.value] || "en-US";
        window.speechSynthesis.speak(utter);
      }
    } catch {
      appendMessage("assistant", "Network error. Try again.");
    }
  }

  if (sendBtn) sendBtn.addEventListener("click", sendMessage);
  if (chatInput) chatInput.addEventListener("keydown", e => { if(e.key==="Enter") sendMessage(); });

  if (micBtn && "webkitSpeechRecognition" in window) {
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";
    recognition.onresult = e => { chatInput.value = e.results[0][0].transcript; sendMessage(); };
    recognition.onerror = () => appendMessage("assistant","Voice input error.");
    micBtn.addEventListener("click", () => recognition.start());
  } else if (micBtn) {
    micBtn.disabled = true;
    micBtn.title = "Voice not supported";
    micBtn.style.opacity = 0.5;
    micBtn.setAttribute("aria-disabled","true");
  }
});
