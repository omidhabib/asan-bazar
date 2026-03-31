/**
 * chat.js - AJAX message sending + polling for new messages
 * Polls every 3 seconds for new messages (WebSocket-ready structure)
 */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('message-input');
    const container = document.getElementById('messages-container');
    if (!form || !container) return;

    // Get conversation pk from URL (/messages/5/)
    const pathParts = window.location.pathname.split('/').filter(Boolean);
    const convPk = pathParts[pathParts.length - 1];

    let lastMessageId = 0;
    // Get ID of last visible message
    const existingMessages = container.querySelectorAll('[data-msg-id]');
    if (existingMessages.length > 0) {
        lastMessageId = parseInt(existingMessages[existingMessages.length - 1].dataset.msgId) || 0;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            for (let c of document.cookie.split(';')) {
                c = c.trim();
                if (c.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(c.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function appendMessage(msg) {
        const div = document.createElement('div');
        div.className = `flex ${msg.is_self ? 'justify-end' : 'justify-start'}`;
        div.dataset.msgId = msg.id;
        div.innerHTML = `
            <div class="max-w-xs lg:max-w-md">
                <div class="px-4 py-2.5 rounded-2xl text-sm leading-relaxed
                    ${msg.is_self ? 'bg-indigo-600 text-white rounded-br-sm' : 'bg-white text-gray-800 shadow-sm rounded-bl-sm'}">
                    ${escapeHtml(msg.content)}
                </div>
                <p class="text-xs text-gray-400 mt-1 ${msg.is_self ? 'text-right' : ''}">${msg.timestamp}</p>
            </div>
        `;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
        lastMessageId = Math.max(lastMessageId, msg.id);
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // AJAX send message
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const content = input.value.trim();
        if (!content) return;

        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `content=${encodeURIComponent(content)}&csrfmiddlewaretoken=${getCookie('csrftoken')}`,
        })
        .then(res => res.json())
        .then(data => {
            if (data.content) {
                appendMessage({ ...data, is_self: true });
                input.value = '';
            }
        })
        .catch(console.error);
    });

    // Poll every 3 seconds for new messages
    const pollInterval = setInterval(() => {
        fetch(`/messages/${convPk}/poll/?after=${lastMessageId}`)
            .then(res => res.json())
            .then(data => {
                data.messages.forEach(msg => {
                    if (!container.querySelector(`[data-msg-id="${msg.id}"]`)) {
                        appendMessage(msg);
                    }
                });
            })
            .catch(console.error);
    }, 3000);

    // Scroll to bottom on load
    container.scrollTop = container.scrollHeight;

    // Clean up on page leave
    window.addEventListener('beforeunload', () => clearInterval(pollInterval));
});
