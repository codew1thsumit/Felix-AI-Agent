const state = {
    currentSessionId: null,
    ws: null,
    sessions: [],
    isWaiting: false,
    isStopping: false,
    streamingMessage: null,
    streamingText: "",
    connectionGeneration: 0,
    wsReadyPromise: null,
    activityTimer: null,
    activityIndex: 0,
    renameSessionId: null,
};


const elements = {
    modelPillName: document.getElementById("modelPillName"),
    profileModelName: document.getElementById("profileModelName"),
    sidebar: document.getElementById("sidebar"),
    sidebarToggle: document.getElementById("sidebarToggle"),
    sessionList: document.getElementById("sessionList"),
    sessionCount: document.getElementById("sessionCount"),
    sessionSearch: document.getElementById("sessionSearch"),
    newChatBtn: document.getElementById("newChatBtn"),
    chatContainer: document.getElementById("chatContainer"),
    welcomeScreen: document.getElementById("welcomeScreen"),
    messages: document.getElementById("messages"),
    messageInput: document.getElementById("messageInput"),
    sendBtn: document.getElementById("sendBtn"),
    stopBtn: document.getElementById("stopBtn"),
    themeToggle: document.getElementById("themeToggle"),
    themeIcon: document.getElementById("themeIcon"),
    themeLabel: document.getElementById("themeLabel"),
    topThemeToggle: document.getElementById("topThemeToggle"),
    clearChatButton: document.getElementById("clearChatButton"),
    collapseSidebar: document.getElementById("collapseSidebar"),
    brandButton: document.getElementById("brandButton"),
    scrollBottom: document.getElementById("scrollBottom"),
    closeRename: document.getElementById("closeRename"),
    cancelRename: document.getElementById("cancelRename"),
    saveRename: document.getElementById("saveRename"),
    renameModal: document.getElementById("renameModal"),
    renameInput: document.getElementById("renameInput"),
    toastRegion: document.getElementById("toastRegion"),
};


// ============================================================
// TOAST  (was called everywhere but never defined -> crash)
// ============================================================

function showToast(message) {
    if (!elements.toastRegion) return;
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;
    elements.toastRegion.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-6px)";
        setTimeout(() => toast.remove(), 320);
    }, 2400);
}


// ============================================================
// MARKDOWN
// ============================================================

marked.setOptions({
    breaks: true,
});


function renderMarkdown(text) {
    // marked v12 calls renderer.code(text, lang, escaped) with
    // POSITIONAL arguments. The old code destructured the first
    // argument as an object, so codeText/lang were always
    // undefined and every code block rendered empty ("TEXT").
    const renderer = new marked.Renderer();

    renderer.code = function (code, lang) {
        const raw = typeof code === "string" ? code : (code && code.text) || "";
        const rawLang = typeof lang === "string"
            ? lang
            : (code && code.lang) || "";
        const language = (rawLang || "text").trim().split(/\s+/)[0] || "text";
        const safeCode = escapeHtml(raw);

        return `<pre><div class="code-header"><span>${escapeHtml(language)}</span><button class="copy-btn" type="button" onclick="copyCode(this)">Copy</button></div><code class="language-${escapeHtml(language)}">${safeCode}</code></pre>`;
    };

    return marked.parse(text || "", { renderer });
}

// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(text) {

    const div = document.createElement(
        "div"
    );

    div.textContent = text ?? "";

    return div.innerHTML;
}


// ============================================================
// COPY CODE
// ============================================================

async function copyCode(btn) {
    const code = btn?.closest("pre")?.querySelector("code");
    if (!code) return;

    const text = code.textContent || "";

    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
        } else {
            const area = document.createElement("textarea");
            area.value = text;
            area.style.position = "fixed";
            area.style.opacity = "0";
            document.body.appendChild(area);
            area.focus();
            area.select();
            document.execCommand("copy");
            area.remove();
        }

        const old = btn.textContent;
        btn.textContent = "Copied!";
        btn.classList.add("copied");
        setTimeout(() => {
            if (btn.isConnected) {
                btn.textContent = old || "Copy";
                btn.classList.remove("copied");
            }
        }, 1500);
    } catch (error) {
        console.error("Failed to copy code:", error);
        showToast("Could not copy code.");
    }
}


// ============================================================
// COPY FULL MESSAGE
// ============================================================

async function copyMessage(btn) {
    const content = btn?.closest(".message")?.querySelector(".message-content");
    if (!content) return;
    const text = content.innerText || "";
    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
        } else {
            const area = document.createElement("textarea");
            area.value = text;
            area.style.position = "fixed";
            area.style.opacity = "0";
            document.body.appendChild(area);
            area.focus();
            area.select();
            document.execCommand("copy");
            area.remove();
        }
        const old = btn.innerHTML;
        btn.innerHTML = `<svg viewBox="0 0 24 24"><path d="M20 6 9 17l-5-5"/></svg> Copied`;
        setTimeout(() => {
            if (btn.isConnected) btn.innerHTML = old;
        }, 1500);
    } catch (e) {
        console.error("Failed to copy message:", e);
        showToast("Could not copy message.");
    }
}


// ============================================================
// SCROLL
// ============================================================

function scrollToBottom() {

    requestAnimationFrame(() => {

        elements.chatContainer.scrollTop =
            elements.chatContainer.scrollHeight;

    });
}


// Only auto-follow the stream when the user is near the bottom
// (ChatGPT behaviour). Otherwise reading older text fights
// the scroll.
function isNearBottom() {
    const el = elements.chatContainer;
    return (
        el.scrollHeight -
        el.scrollTop -
        el.clientHeight
    ) < 160;
}


function followScroll() {
    if (isNearBottom()) {
        scrollToBottom();
    }
}


// ============================================================
// TEXTAREA
// ============================================================

function autoResizeTextarea() {

    const el =
        elements.messageInput;

    el.style.height = "auto";

    el.style.height =
        Math.min(
            el.scrollHeight,
            200
        ) + "px";
}


// ============================================================
// SEND / STOP BUTTON
// ============================================================

function updateSendButton() {

    if (!elements.sendBtn) {
        return;
    }

    if (state.isWaiting) {

        // Send button doubles as the stop button while
        // generating (the icon becomes a stop square).
        elements.sendBtn.disabled = false;

        if (elements.stopBtn) {
            elements.stopBtn.classList.add("visible");
        }

        elements.sendBtn.innerHTML = `
            <span style="
                display:block;
                width:10px;
                height:10px;
                background:currentColor;
                border-radius:2px;
            "></span>
        `;

        elements.sendBtn.title =
            "Stop generation";

    } else {

        if (elements.stopBtn) {
            elements.stopBtn.classList.remove("visible");
        }

        const hasText =
            elements.messageInput.value.trim().length > 0;

        elements.sendBtn.disabled =
            !hasText;

        elements.sendBtn.innerHTML = `
            <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
            >
                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
            </svg>
        `;

        elements.sendBtn.title =
            "Send message";
    }
}


// ============================================================
// FETCH SESSIONS
// ============================================================

async function fetchSessions() {

    try {

        const res = await fetch(
            "/api/sessions"
        );

        if (!res.ok) {
            throw new Error(
                `HTTP ${res.status}`
            );
        }

        state.sessions =
            await res.json();

        renderSessionList();

        if (
            state.sessions.length === 0 &&
            !state.currentSessionId
        ) {
            await createNewSession();
        } else if (
            !state.currentSessionId &&
            state.sessions.length > 0
        ) {
            await loadSession(state.sessions[0].id);
        }

    } catch (e) {

        console.error(
            "Failed to fetch sessions:",
            e
        );
    }
}


// ============================================================
// RENDER SESSION LIST
// ============================================================

function renderSessionList() {

    if (elements.sessionCount) {
        elements.sessionCount.textContent =
            String(state.sessions.length);
    }

    if (
        !state.sessions ||
        state.sessions.length === 0
    ) {

        elements.sessionList.innerHTML =
            `
            <div class="session-loading">
                No conversations yet
            </div>
            `;

        return;
    }


    elements.sessionList.innerHTML =
        state.sessions
            .map(
                (s) => `
                <div
                    class="session-item ${
                        s.id === state.currentSessionId
                            ? "active"
                            : ""
                    }"
                    data-id="${escapeHtml(s.id)}"
                    data-title="${escapeHtml(s.title.toLowerCase())}"
                >

                    <span class="session-item-title">
                        ${escapeHtml(s.title)}
                    </span>

                    <div class="session-item-actions">
                        <button
                            class="session-action rename"
                            onclick="
                                event.stopPropagation();
                                openRename('${s.id}');
                            "
                            title="Rename"
                            aria-label="Rename chat"
                        >
                            <svg viewBox="0 0 24 24">
                                <path d="M12 20h9"/>
                                <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>
                            </svg>
                        </button>
                        <button
                            class="session-action delete"
                            onclick="
                                event.stopPropagation();
                                deleteSession('${s.id}');
                            "
                            title="Delete"
                            aria-label="Delete chat"
                        >
                            <svg viewBox="0 0 24 24">
                                <path d="M3 6h18"/>
                                <path d="M8 6V4h8v2"/>
                                <path d="M19 6l-1 14H6L5 6"/>
                            </svg>
                        </button>
                    </div>

                </div>
                `
            )
            .join("");


    elements.sessionList
        .querySelectorAll(".session-item")
        .forEach(
            (item) => {

                item.addEventListener(
                    "click",
                    () => {
                        loadSession(
                            item.dataset.id
                        );
                    }
                );

            }
        );


    // Re-apply the current search filter after re-render
    if (elements.sessionSearch) {
        filterSessions(elements.sessionSearch.value);
    }
}


// ============================================================
// SEARCH FILTER  (search box existed but did nothing)
// ============================================================

function filterSessions(query) {
    const q = (query || "").trim().toLowerCase();

    elements.sessionList
        .querySelectorAll(".session-item")
        .forEach((item) => {
            const title =
                item.dataset.title ||
                (item.querySelector(".session-item-title")?.textContent || "").toLowerCase();

            item.style.display =
                (!q || title.includes(q)) ? "" : "none";
        });
}


// ============================================================
// CREATE SESSION
// ============================================================

async function createNewSession() {

    try {

        const res = await fetch(
            "/api/sessions",
            {
                method: "POST"
            }
        );

        if (!res.ok) {
            throw new Error(
                `HTTP ${res.status}`
            );
        }

        const session =
            await res.json();


        state.sessions.unshift(
            session
        );


        renderSessionList();


        await loadSession(
            session.id
        );


    } catch (e) {

        console.error(
            "Failed to create session:",
            e
        );

        showToast("Could not create a new chat.");
    }
}


// ============================================================
// CLOSE CURRENT WEBSOCKET
// ============================================================

function closeCurrentWebSocket() {

    if (!state.ws) {
        return;
    }

    try {
        state.ws.onclose = null;
        state.ws.onerror = null;
        state.ws.close();
    } catch (e) {
        console.warn(e);
    }

    state.ws = null;
    state.wsReadyPromise = null;
}


// ============================================================
// LOAD SESSION
// ============================================================

async function loadSession(
    sessionId
) {

    if (!sessionId) {
        return;
    }


    // Cancel old connection
    closeCurrentWebSocket();


    state.connectionGeneration++;

    const generation =
        state.connectionGeneration;


    state.currentSessionId =
        sessionId;

    state.isWaiting = false;
    state.isStopping = false;
    state.streamingMessage = null;
    state.streamingText = "";

    stopResponseActivity();


    closeSidebar();


    renderSessionList();


    elements.messages.innerHTML = "";

    removeThinking();


    elements.welcomeScreen.style.display =
        "none";


    updateSendButton();


    try {

        const res = await fetch(
            `/api/sessions/${encodeURIComponent(sessionId)}/messages`
        );


        if (!res.ok) {
            throw new Error(
                `HTTP ${res.status}`
            );
        }


        const messages =
            await res.json();


        // If user changed sessions while
        // the request was loading, ignore
        // this old request.
        if (
            generation !==
            state.connectionGeneration
        ) {
            return;
        }


        if (
            messages.length === 0
        ) {

            elements.welcomeScreen.style.display =
                "flex";

        } else {

            messages.forEach(
                (msg) => {

                    appendMessage(
                        msg.role,
                        msg.content,
                        false
                    );

                }
            );

            scrollToBottom();
        }


    } catch (e) {

        console.error(
            "Failed to load messages:",
            e
        );

        elements.welcomeScreen.style.display =
            "flex";
    }


    connectWebSocket(
        sessionId,
        generation
    );
}


// ============================================================
// DELETE SESSION
// ============================================================

async function deleteSession(
    sessionId
) {

    if (
        !confirm(
            "Delete this conversation?"
        )
    ) {
        return;
    }


    const deletingCurrent =
        state.currentSessionId ===
        sessionId;


    // Close current websocket BEFORE
    // deleting the session.
    if (deletingCurrent) {

        closeCurrentWebSocket();

        state.isWaiting = false;
        state.isStopping = false;

        state.streamingMessage = null;
        state.streamingText = "";

        stopResponseActivity();

        elements.messages.innerHTML = "";

        removeThinking();

        elements.welcomeScreen.style.display =
            "flex";
    }


    try {

        const res = await fetch(
            `/api/sessions/${encodeURIComponent(sessionId)}`,
            {
                method: "DELETE"
            }
        );


        if (!res.ok) {

            throw new Error(
                `HTTP ${res.status}`
            );
        }


        // Remove from local state
        state.sessions =
            state.sessions.filter(
                (s) => s.id !== sessionId
            );


        if (deletingCurrent) {

            state.currentSessionId =
                null;

            // Create a completely fresh
            // conversation.
            const newSessionRes =
                await fetch(
                    "/api/sessions",
                    {
                        method: "POST"
                    }
                );


            if (
                newSessionRes.ok
            ) {

                const newSession =
                    await newSessionRes.json();


                await loadSession(
                    newSession.id
                );
            }

        } else {

            renderSessionList();
        }


    } catch (e) {

        console.error(
            "Failed to delete session:",
            e
        );

        showToast("Could not delete chat.");

        await fetchSessions();
    }
}


// ============================================================
// CONNECT WEBSOCKET
// ============================================================

function connectWebSocket(
    sessionId,
    generation
) {

    closeCurrentWebSocket();


    const protocol =
        location.protocol === "https:"
            ? "wss:"
            : "ws:";


    let resolveReady;
    let rejectReady;

    let settled = false;

    state.wsReadyPromise = new Promise((resolve, reject) => {
        resolveReady = resolve;
        rejectReady = reject;
    });

    // Prevent unhandled-rejection noise if nobody awaits it.
    state.wsReadyPromise.catch(() => {});


    const ws = new WebSocket(
        `${protocol}//${location.host}/ws/${encodeURIComponent(sessionId)}`
    );


    state.ws = ws;


    ws.onopen = () => {

        if (
            generation !==
            state.connectionGeneration
        ) {

            ws.close();

            return;
        }

        console.log(
            "FELIX WebSocket connected:",
            sessionId
        );

        settled = true;

        resolveReady(ws);

        updateSendButton();
    };


    ws.onmessage = (
        event
    ) => {

        // Ignore events from an old
        // connection.
        if (
            generation !==
            state.connectionGeneration
        ) {
            return;
        }


        let data;


        try {

            data =
                JSON.parse(
                    event.data
                );

        } catch (e) {

            console.error(
                "Invalid WebSocket message:",
                event.data
            );

            return;
        }


        // ====================================================
        // THINKING
        // ====================================================

        if (
            data.type ===
            "thinking"
        ) {

            state.isWaiting =
                true;

            state.isStopping =
                false;

            state.streamingText =
                "";

            state.streamingMessage =
                null;

            updateSendButton();

            appendThinking();

            return;
        }


        // ====================================================
        // TOKEN
        // ====================================================

        if (
            data.type ===
            "token"
        ) {

            const token =
                data.content || "";


            if (!token) {
                return;
            }


            removeThinking();


            if (
                !state.streamingMessage
            ) {

                state.streamingMessage =
                    createStreamingMessage();

                state.streamingText =
                    "";
            }


            state.streamingText +=
                token;


            updateStreamingMessage();


            return;
        }


        // ====================================================
        // FINAL RESPONSE
        // ====================================================

        if (
            data.type ===
            "response"
        ) {

            state.isWaiting =
                false;

            state.isStopping =
                false;


            removeThinking();


            if (
                state.streamingMessage
            ) {

                state.streamingText =
                    data.content || state.streamingText;

                updateStreamingMessage(true);

                attachMessageActions(
                    state.streamingMessage
                );

                finishResponseActivity(
                    state.streamingMessage.querySelector("[data-activity]")
                );

            } else {

                appendMessage(
                    "assistant",
                    data.content || "",
                    true
                );
            }


            state.streamingMessage =
                null;

            state.streamingText =
            "";

            stopResponseActivity();

            updateSendButton();


            // Refresh titles/order
            fetchSessions();


            return;
        }


        // ====================================================
        // STOPPED
        // ====================================================

        if (
            data.type ===
            "stopped"
        ) {

            state.isWaiting =
                false;

            state.isStopping =
                false;


            removeThinking();


            if (
                state.streamingMessage
            ) {

                updateStreamingMessage(true);

                attachMessageActions(
                    state.streamingMessage
                );

                finishResponseActivity(
                    state.streamingMessage.querySelector("[data-activity]")
                );

            } else {
                stopResponseActivity();
            }


            state.streamingMessage =
                null;

            state.streamingText =
                "";


            updateSendButton();


            return;
        }


        // ====================================================
        // TITLE
        // ====================================================

        if (
            data.type ===
            "title_update"
        ) {

            const session =
                state.sessions.find(
                    (s) =>
                        s.id ===
                        sessionId
                );


            if (session) {

                session.title =
                    data.title;

                renderSessionList();
            }


            return;
        }


        // ====================================================
        // EVENT
        // ====================================================

        if (
            data.type ===
            "event"
        ) {

            console.log(
                "FELIX event:",
                data.event
            );

            const source = (data.event && data.event.source) || "";

            if (source === "memory") {
                activateResponseSource("memory");
            }

            if (source === "gemini" || source === "model") {
                setActiveModel("gemini");
                activateResponseSource("model");
            }

            if (source === "openrouter" || source === "openrouter_free") {
                setActiveModel("openrouter");
                activateResponseSource("model");
            }

            if (source === "wikipedia" || source === "web") {
                activateResponseSource("wikipedia");
            }

            return;
        }


        // ====================================================
        // ERROR
        // ====================================================

        if (
            data.type ===
            "error"
        ) {

            state.isWaiting =
                false;

            state.isStopping =
                false;


            removeThinking();


            if (
                data.message
            ) {

                appendMessage(
                    "assistant",
                    `Sorry, an error occurred:\n\n${data.message}`,
                    true
                );
            }


            state.streamingMessage =
                null;

            state.streamingText =
                "";


            stopResponseActivity();

            updateSendButton();
        }
    };


    ws.onclose = () => {

        if (
            generation !==
            state.connectionGeneration
        ) {
            return;
        }


        state.isWaiting =
            false;

        state.isStopping =
            false;

        updateSendButton();


        // Wake up anyone waiting on the connection promise.
        if (!settled) {
            settled = true;
            try {
                rejectReady(new Error("WebSocket closed."));
            } catch (e) {}
        }


        console.log(
            "FELIX WebSocket closed:",
            sessionId
        );
    };


    ws.onerror = (
        error
    ) => {

        if (
            generation !==
            state.connectionGeneration
        ) {
            return;
        }


        console.error(
            "FELIX WebSocket error:",
            error
        );


        state.isWaiting =
            false;

        state.isStopping =
            false;

        updateSendButton();
    };
}


// ============================================================
// FELIX RESPONSE ACTIVITY
// ============================================================

function assistantAvatarHtml() {
    return '<img class="assistant-logo" src="/static/felix-logo.png?v=felix-logo-final-1" alt="">';
}

function responseActivityHtml() {
    // Only show components that are actually connected/used.
    // Wikipedia is added dynamically when the backend invokes it.
    const nodes = [
        ["felix", "FELIX"],
        ["memory", "Memory"],
        ["model", "Gemini"],
    ];

    return `
        <div class="response-activity" data-activity>
            ${nodes.map((node, index) => `
                ${index ? '<span class="response-link" aria-hidden="true"></span>' : ''}
                <span class="response-node" data-source="${node[0]}">
                    <span class="response-node-dot"></span>
                    <span>${node[1]}</span>
                </span>
            `).join("")}
        </div>
    `;
}

function stopResponseActivity() {
    if (state.activityTimer) {
        clearInterval(state.activityTimer);
        state.activityTimer = null;
    }
}

function startResponseActivity(container) {
    stopResponseActivity();
    if (!container) return;

    const nodes = Array.from(container.querySelectorAll(".response-node"));
    if (!nodes.length) return;

    state.activityIndex = 0;
    nodes.forEach((node) => node.classList.remove("active"));
    nodes[0].classList.add("active");

    state.activityTimer = setInterval(() => {
        const currentNodes = Array.from(container.querySelectorAll(".response-node"));
        if (!currentNodes.length) return;
        currentNodes.forEach((node) => node.classList.remove("active"));
        currentNodes[state.activityIndex % currentNodes.length].classList.add("active");
        state.activityIndex += 1;
    }, 850);
}

function finishResponseActivity(container) {
    stopResponseActivity();
    if (!container) return;
    container.classList.add("done");
    container.querySelectorAll(".response-node").forEach((node) => node.classList.add("active"));
    setTimeout(() => {
        if (container.isConnected) container.remove();
    }, 450);
}

function setActiveModel(model) {
    const isOpenRouter =
        model === "openrouter" ||
        model === "openrouter_free";

    const pillLabel = isOpenRouter
        ? "OpenRouter"
        : "Gemini 3.5 Flash-Lite";

    if (elements.modelPillName) {
        elements.modelPillName.textContent = pillLabel;
    }

    if (elements.profileModelName) {
        elements.profileModelName.textContent = isOpenRouter
            ? "OpenRouter · LangGraph"
            : "Gemini 3.5 Flash-Lite · LangGraph";
    }

    const activity = document.querySelector("[data-activity]");
    if (activity) {
        const node = activity.querySelector('[data-source="model"]');
        const label = node?.querySelector("span:last-child");
        if (label) {
            label.textContent = isOpenRouter ? "OpenRouter" : "Gemini";
        }
    }
}

function activateResponseSource(source) {
    const activity = document.querySelector("[data-activity]");
    if (!activity) return;

    const labels = {
        wikipedia: "Wikipedia",
        web: "Web",
        gemini: "Gemini",
        model: "Gemini",
        openrouter: "OpenRouter",
        openrouter_free: "OpenRouter",
        memory: "Memory",
        felix: "FELIX",
    };

    if (source === "openrouter" || source === "openrouter_free" || source === "gemini") {
        source = "model";
    }

    let node = activity.querySelector(`[data-source="${source}"]`);
    if (!node && labels[source]) {
        const link = document.createElement("span");
        link.className = "response-link";
        link.setAttribute("aria-hidden", "true");

        node = document.createElement("span");
        node.className = "response-node";
        node.dataset.source = source;
        node.innerHTML = `<span class="response-node-dot"></span><span>${escapeHtml(labels[source])}</span>`;

        activity.appendChild(link);
        activity.appendChild(node);
    }

    if (node) {
        activity.querySelectorAll(".response-node").forEach((item) => item.classList.remove("active"));
        node.classList.add("active");
    }
}

// ============================================================
// CREATE STREAMING MESSAGE
// ============================================================

function createStreamingMessage() {

    elements.welcomeScreen.style.display =
        "none";


    const div =
        document.createElement(
            "div"
        );


    div.className =
        "message assistant";


    div.innerHTML = `
        <div class="message-avatar">
            ${assistantAvatarHtml()}
        </div>

        <div class="message-content">
            ${responseActivityHtml()}
            <div class="streaming-content"></div>
        </div>
    `;


    elements.messages.appendChild(
        div
    );

    startResponseActivity(div.querySelector("[data-activity]"));

    followScroll();


    return div;
}


// ============================================================
// UPDATE STREAMING MESSAGE
// ============================================================

function updateStreamingMessage(final = false) {

    if (
        !state.streamingMessage
    ) {
        return;
    }


    const content =
        state.streamingMessage
            .querySelector(
                ".streaming-content"
            );


    if (!content) {
        return;
    }


    content.innerHTML =
        renderMarkdown(
            state.streamingText
        );


    // Highlight code blocks
    content
        .querySelectorAll("pre code")
        .forEach(
            (block) => {

                try {

                    hljs.highlightElement(
                        block
                    );

                } catch (e) {
                    console.warn(e);
                }
            }
        );


    // ChatGPT-style blinking caret while tokens arrive.
    const oldCursor =
        content.querySelector(".stream-cursor");

    if (oldCursor) {
        oldCursor.remove();
    }

    if (!final) {
        const cursor =
            document.createElement("span");

        cursor.className =
            "stream-cursor";

        cursor.setAttribute(
            "aria-hidden",
            "true"
        );

        content.appendChild(cursor);
    }


    followScroll();
}


// ============================================================
// APPEND NORMAL MESSAGE
// ============================================================

function appendMessage(
    role,
    content,
    animate
) {

    elements.welcomeScreen.style.display =
        "none";


    const div =
        document.createElement(
            "div"
        );


    div.className =
        `message ${role}`;


    if (animate) {

        div.style.animation =
            "messageIn 0.25s ease";
    }


    const avatarLabel =
        role === "user"
            ? "Y"
            : assistantAvatarHtml();


    const renderedContent =
        role === "assistant"
            ? renderMarkdown(content)
            : escapeHtml(content)
                .replace(
                    /\n/g,
                    "<br>"
                );


    // Hover actions for assistant messages (Copy + Regenerate).
    // The CSS for .message-actions already exists in style.css.
    const actions =
        role === "assistant"
            ? `
            <div class="message-actions">
                <button
                    class="message-action"
                    onclick="copyMessage(this)"
                    title="Copy response"
                >
                    <svg viewBox="0 0 24 24">
                        <rect x="9" y="9" width="11" height="11" rx="2"/>
                        <path d="M5 15V5a2 2 0 0 1 2-2h10"/>
                    </svg>
                    Copy
                </button>
                <button
                    class="message-action"
                    onclick="regenerateResponse()"
                    title="Regenerate response"
                >
                    <svg viewBox="0 0 24 24">
                        <path d="M21 12a9 9 0 1 1-2.64-6.36"/>
                        <path d="M21 3v6h-6"/>
                    </svg>
                    Regenerate
                </button>
            </div>
            `
            : "";


    div.innerHTML = `
        <div class="message-avatar">
            ${avatarLabel}
        </div>

        <div class="message-content">
            ${renderedContent}
        </div>

        ${actions}
    `;


    elements.messages.appendChild(
        div
    );


    div.querySelectorAll(
        "pre code"
    ).forEach(
        (block) => {

            try {

                hljs.highlightElement(
                    block
                );

            } catch (e) {}
        }
    );


    scrollToBottom();
}


// ============================================================
// REMOVE LAST ASSISTANT BUBBLE (used before regenerate)
// ============================================================

function removeLastAssistantMessage() {
    const assistantMessages =
        elements.messages.querySelectorAll(
            ".message.assistant"
        );

    const last =
        assistantMessages[
            assistantMessages.length - 1
        ];

    if (last) {
        last.remove();
    }
}



// ============================================================
// ATTACH COPY / REGENERATE ACTIONS TO A MESSAGE
// (used to give finished streaming bubbles the same hover
// actions that appendMessage() gives normal messages)
// ============================================================

function attachMessageActions(messageEl) {
    if (!messageEl) return;
    if (messageEl.querySelector(".message-actions")) return;

    const actions = document.createElement("div");
    actions.className = "message-actions";

    actions.innerHTML = `
        <button
            class="message-action"
            onclick="copyMessage(this)"
            title="Copy response"
        >
            <svg viewBox="0 0 24 24">
                <rect x="9" y="9" width="11" height="11" rx="2"/>
                <path d="M5 15V5a2 2 0 0 1 2-2h10"/>
            </svg>
            Copy
        </button>
        <button
            class="message-action"
            onclick="regenerateResponse()"
            title="Regenerate response"
        >
            <svg viewBox="0 0 24 24">
                <path d="M21 12a9 9 0 1 1-2.64-6.36"/>
                <path d="M21 3v6h-6"/>
            </svg>
            Regenerate
        </button>
    `;

    messageEl.appendChild(actions);
}

// ============================================================
// THINKING
// ============================================================

function appendThinking() {

    removeThinking();


    const div =
        document.createElement(
            "div"
        );


    div.className =
        "message assistant";


    div.id =
        "thinkingMsg";


    div.innerHTML = `
        <div class="message-avatar">
            ${assistantAvatarHtml()}
        </div>

        <div class="message-content">
            ${responseActivityHtml()}
            <div class="thinking-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;


    elements.messages.appendChild(
        div
    );

    startResponseActivity(div.querySelector("[data-activity]"));

    followScroll();
}


// ============================================================
// REMOVE THINKING
// ============================================================

function removeThinking() {

    const el =
        document.getElementById(
            "thinkingMsg"
        );


    if (el) {
        el.remove();
    }
}


// ============================================================
// SEND MESSAGE
// ============================================================

async function sendMessage() {

    // If currently generating,
    // the same button becomes STOP.
    if (state.isWaiting) {

        stopGeneration();

        return;
    }


    const text =
        elements.messageInput.value.trim();


    if (!text) {
        return;
    }


    if (
        !state.ws ||
        state.ws.readyState !==
            WebSocket.OPEN
    ) {
        try {
            if (state.wsReadyPromise) {
                await Promise.race([
                    state.wsReadyPromise,
                    new Promise((_, reject) =>
                        setTimeout(
                            () => reject(new Error("WebSocket connection timeout.")),
                            5000
                        )
                    )
                ]);
            } else if (state.currentSessionId) {
                connectWebSocket(
                    state.currentSessionId,
                    state.connectionGeneration
                );
                await Promise.race([
                    state.wsReadyPromise,
                    new Promise((_, reject) =>
                        setTimeout(
                            () => reject(new Error("WebSocket connection timeout.")),
                            5000
                        )
                    )
                ]);
            }
        } catch (e) {
            console.error("WebSocket is not connected.", e);
            showToast("FELIX is connecting. Please try again.");
            return;
        }
    }

    if (!state.ws || state.ws.readyState !== WebSocket.OPEN) {
        return;
    }


    appendMessage(
        "user",
        text,
        false
    );


    state.ws.send(
        JSON.stringify(
            {
                type: "message",
                message: text
            }
        )
    );


    elements.messageInput.value =
        "";


    autoResizeTextarea();


    updateSendButton();
}


// ============================================================
// STOP GENERATION
// ============================================================

function stopGeneration() {

    if (
        !state.ws ||
        state.ws.readyState !==
            WebSocket.OPEN
    ) {
        return;
    }


    if (
        !state.isWaiting
    ) {
        return;
    }


    state.isStopping =
        true;


    state.ws.send(
        JSON.stringify(
            {
                type: "stop"
            }
        )
    );


    // Give the server a moment to confirm; if no "stopped"
    // arrives (e.g. socket died), reset the UI anyway.
    setTimeout(() => {
        if (state.isStopping) {
            state.isWaiting = false;
            state.isStopping = false;
            updateStreamingMessage(true);
            stopResponseActivity();
            state.streamingMessage = null;
            state.streamingText = "";
            updateSendButton();
        }
    }, 4000);
}


// ============================================================
// REGENERATE
// ============================================================

function regenerateResponse() {

    if (
        state.isWaiting ||
        !state.ws ||
        state.ws.readyState !==
            WebSocket.OPEN
    ) {
        return;
    }


    // Remove the previous assistant bubble so the new
    // stream replaces it visually.
    removeLastAssistantMessage();


    state.ws.send(
        JSON.stringify(
            {
                type: "regenerate"
            }
        )
    );
}


// ============================================================
// SIDEBAR
// ============================================================

function openSidebar() {

    elements.sidebar.classList.add(
        "open"
    );


    document.body.appendChild(
        createOverlay()
    );
}


function closeSidebar() {

    elements.sidebar.classList.remove(
        "open"
    );


    const overlay =
        document.querySelector(
            ".sidebar-overlay"
        );


    if (overlay) {
        overlay.remove();
    }
}


function createOverlay() {

    let overlay =
        document.querySelector(
            ".sidebar-overlay"
        );


    if (!overlay) {

        overlay =
            document.createElement(
                "div"
            );

        overlay.className =
            "sidebar-overlay active";


        overlay.addEventListener(
            "click",
            closeSidebar
        );
    }


    return overlay;
}


// ============================================================
// INPUT EVENTS
// ============================================================

elements.sendBtn.addEventListener(
    "click",
    sendMessage
);


elements.messageInput.addEventListener(
    "input",
    () => {

        autoResizeTextarea();

        updateSendButton();
    }
);


elements.messageInput.addEventListener(
    "keydown",
    (e) => {

        if (
            e.key === "Enter" &&
            !e.shiftKey
        ) {

            e.preventDefault();

            sendMessage();
        }
    }
);


// ============================================================
// UI CONTROLS
// ============================================================

function applyTheme(theme) {
    const selected = theme === "light" ? "light" : "dark";
    document.documentElement.dataset.theme = selected;

    if (elements.themeLabel) {
        elements.themeLabel.textContent =
            selected.charAt(0).toUpperCase() + selected.slice(1);
    }

    if (elements.themeIcon) {
        elements.themeIcon.innerHTML = selected === "dark"
            ? '<svg viewBox="0 0 24 24"><path d="M21 12.8A8.5 8.5 0 1 1 11.2 3 6.7 6.7 0 0 0 21 12.8Z"/></svg>'
            : '<svg viewBox="0 0 24 24"><path d="M12 3v2M12 19v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M3 12h2M19 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/><circle cx="12" cy="12" r="4"/></svg>';
    }

    localStorage.setItem("felix-theme", selected);
}

function toggleTheme() {
    applyTheme(
        document.documentElement.dataset.theme === "dark"
            ? "light"
            : "dark"
    );
}

async function clearCurrentChat() {
    if (!state.currentSessionId) return;

    if (!confirm("Clear messages from this chat?")) return;

    if (state.isWaiting) {
        stopGeneration();
    }

    try {
        const res = await fetch(
            `/api/sessions/${encodeURIComponent(state.currentSessionId)}/clear`,
            { method: "DELETE" }
        );

        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }

        elements.messages.innerHTML = "";
        removeThinking();
        stopResponseActivity();
        state.streamingMessage = null;
        state.streamingText = "";
        elements.welcomeScreen.style.display = "flex";
        showToast("Chat cleared");
    } catch (e) {
        console.error("Clear chat failed:", e);
        showToast("Could not clear chat");
    }
}

function collapseSidebar() {
    document.body.classList.toggle("sidebar-collapsed");
}

function openRename(sessionId) {
    const session = state.sessions.find((s) => s.id === sessionId);
    if (!session || !elements.renameModal) return;

    state.renameSessionId = sessionId;
    elements.renameInput.value = session.title || "New Chat";
    elements.renameModal.hidden = false;
    elements.renameInput.focus();
    elements.renameInput.select();
}

async function saveCurrentRename() {
    const sessionId = state.renameSessionId;
    if (!sessionId) return;

    const title = elements.renameInput.value.trim() || "New Chat";

    try {
        const res = await fetch(
            `/api/sessions/${encodeURIComponent(sessionId)}`,
            {
                method: "PATCH",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({title})
            }
        );

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const session = state.sessions.find((s) => s.id === sessionId);
        if (session) session.title = title;

        elements.renameModal.hidden = true;
        state.renameSessionId = null;
        renderSessionList();
        showToast("Chat renamed");
    } catch (e) {
        console.error("Rename failed:", e);
        showToast("Could not rename chat");
    }
}

function closeRenameModal() {
    if (elements.renameModal) elements.renameModal.hidden = true;
    state.renameSessionId = null;
}

function updateScrollButton() {
    if (!elements.scrollBottom) return;

    const distance =
        elements.chatContainer.scrollHeight -
        elements.chatContainer.scrollTop -
        elements.chatContainer.clientHeight;

    elements.scrollBottom.classList.toggle("visible", distance > 260);
}

if (elements.stopBtn) elements.stopBtn.addEventListener("click", stopGeneration);
if (elements.themeToggle) elements.themeToggle.addEventListener("click", toggleTheme);
if (elements.topThemeToggle) elements.topThemeToggle.addEventListener("click", toggleTheme);
if (elements.clearChatButton) elements.clearChatButton.addEventListener("click", clearCurrentChat);
if (elements.collapseSidebar) elements.collapseSidebar.addEventListener("click", collapseSidebar);
if (elements.brandButton) elements.brandButton.addEventListener("click", collapseSidebar);
if (elements.scrollBottom) elements.scrollBottom.addEventListener("click", scrollToBottom);
if (elements.closeRename) elements.closeRename.addEventListener("click", closeRenameModal);
if (elements.cancelRename) elements.cancelRename.addEventListener("click", closeRenameModal);
if (elements.saveRename) elements.saveRename.addEventListener("click", saveCurrentRename);

if (elements.renameInput) {
    elements.renameInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            saveCurrentRename();
        } else if (e.key === "Escape") {
            closeRenameModal();
        }
    });
}

if (elements.sessionSearch) {
    elements.sessionSearch.addEventListener("input", (e) => {
        filterSessions(e.target.value);
    });
}

elements.chatContainer.addEventListener("scroll", updateScrollButton);

const savedTheme = localStorage.getItem("felix-theme");
applyTheme(
    savedTheme === "light" || savedTheme === "dark"
        ? savedTheme
        : (document.documentElement.dataset.theme || "dark")
);


// ============================================================
// KEYBOARD SHORTCUTS
// ============================================================

document.addEventListener("keydown", (e) => {

    const activeTag =
        document.activeElement?.tagName || "";

    const typing =
        activeTag === "INPUT" ||
        activeTag === "TEXTAREA";


    // Ctrl / Cmd + K  ->  New chat (kbd hint shown on the button)
    if (
        (e.ctrlKey || e.metaKey) &&
        e.key.toLowerCase() === "k"
    ) {
        e.preventDefault();
        createNewSession();
        return;
    }


    // "/" focuses chat search (unless already typing)
    if (
        e.key === "/" &&
        !typing
    ) {
        e.preventDefault();
        if (elements.sessionSearch) {
            elements.sessionSearch.focus();
        }
        return;
    }


    // Escape closes the rename modal / mobile sidebar
    if (e.key === "Escape") {
        if (
            elements.renameModal &&
            !elements.renameModal.hidden
        ) {
            closeRenameModal();
            return;
        }

        if (
            elements.sidebar &&
            elements.sidebar.classList.contains("open")
        ) {
            closeSidebar();
            return;
        }
    }
});


// ============================================================
// NEW CHAT
// ============================================================

elements.newChatBtn.addEventListener(
    "click",
    createNewSession
);


// ============================================================
// SIDEBAR TOGGLE
// ============================================================

elements.sidebarToggle.addEventListener(
    "click",
    () => {

        if (
            elements.sidebar.classList.contains(
                "open"
            )
        ) {

            closeSidebar();

        } else {

            openSidebar();
        }
    }
);


// ============================================================
// SUGGESTIONS
// ============================================================

document
    .querySelectorAll(
        ".suggestion-card"
    )
    .forEach(
        (card) => {

            card.addEventListener(
                "click",
                async () => {

                    const prompt =
                        card.dataset.prompt;


                    if (
                        !state.currentSessionId
                    ) {

                        await createNewSession();
                    }


                    elements.messageInput.value =
                        prompt;


                    updateSendButton();


                    sendMessage();
                }
            );
        }
    );


// ============================================================
// START
// ============================================================

fetchSessions();