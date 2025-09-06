// Configurações da aplicação
const CONFIG = {
    API_BASE_URL: 'http://localhost:5000',
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000,
    TOAST_DURATION: 5000,
    HEALTH_CHECK_INTERVAL: 30000
};

// Estado da aplicação
const state = {
    isConnected: false,
    questionCount: 0,
    answeredQuestions: 0,
    executedQueries: 0,
    responseTimes: [],
    lastQuery: null,
    theme: 'light'
};

// Elementos DOM
const elements = {
    chatMessages: document.getElementById('chatMessages'),
    messageInput: document.getElementById('messageInput'),
    sendButton: document.getElementById('sendButton'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    connectionStatus: document.getElementById('connectionStatus'),
    systemStatus: document.getElementById('systemStatus'),
    apiStatus: document.getElementById('apiStatus'),
    latency: document.getElementById('latency'),
    lastQuery: document.getElementById('lastQuery'),
    totalQuestions: document.getElementById('totalQuestions'),
    avgResponse: document.getElementById('avgResponse'),
    questionsAnswered: document.getElementById('questionsAnswered'),
    queriesExecuted: document.getElementById('queriesExecuted'),
    charCounter: document.getElementById('charCounter'),
    themeToggle: document.getElementById('themeToggle'),
    toastContainer: document.getElementById('toastContainer')
};

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkApiHealth();
    
    // Verificação periódica da API
    setInterval(checkApiHealth, CONFIG.HEALTH_CHECK_INTERVAL);
});

// Inicializar aplicação
function initializeApp() {
    // Carregar tema salvo
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    // Carregar estatísticas salvas
    loadSavedStats();
    
    // Atualizar UI inicial
    updateUI();
    
    showToast('Bem-vindo ao PetHotel AI! 🐾', 'success');
}

// Configurar event listeners
function setupEventListeners() {
    // Input de mensagem
    elements.messageInput.addEventListener('keypress', handleKeyPress);
    elements.messageInput.addEventListener('input', handleInputChange);
    
    // Botão de envio
    elements.sendButton.addEventListener('click', sendMessage);
    
    // Toggle de tema
    elements.themeToggle.addEventListener('click', toggleTheme);
    
    // Scroll automático no chat
    elements.chatMessages.addEventListener('DOMNodeInserted', scrollToBottom);
}

// Manipular teclas pressionadas
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Manipular mudanças no input
function handleInputChange(event) {
    const length = event.target.value.length;
    elements.charCounter.textContent = `${length}/500`;
    
    // Mudar cor baseado no limite
    if (length > 450) {
        elements.charCounter.style.color = 'var(--error-500)';
    } else if (length > 400) {
        elements.charCounter.style.color = 'var(--warning-500)';
    } else {
        elements.charCounter.style.color = 'var(--gray-400)';
    }
    
    // Habilitar/desabilitar botão de envio
    elements.sendButton.disabled = length === 0 || length > 500;
}

// Verificar saúde da API
async function checkApiHealth() {
    try {
        const startTime = Date.now();
        const response = await fetchWithTimeout(`${CONFIG.API_BASE_URL}/health`, {
            method: 'GET'
        }, 5000);
        
        const responseTime = Date.now() - startTime;
        
        if (response.ok) {
            setConnectionStatus(true, responseTime);
        } else {
            setConnectionStatus(false);
        }
    } catch (error) {
        console.error('Erro ao verificar API:', error);
        setConnectionStatus(false);
    }
}

// Definir status da conexão
function setConnectionStatus(isOnline, responseTime = null) {
    state.isConnected = isOnline;
    
    const statusElements = [elements.connectionStatus, elements.systemStatus];
    
    statusElements.forEach(element => {
        const dot = element.querySelector('.status-dot');
        const text = element.querySelector('span');
        
        if (isOnline) {
            dot.className = 'status-dot online';
            text.textContent = 'Online';
            elements.apiStatus.textContent = 'Online';
            
            if (responseTime !== null) {
                elements.latency.textContent = `${responseTime}ms`;
            }
        } else {
            dot.className = 'status-dot offline';
            text.textContent = 'Offline';
            elements.apiStatus.textContent = 'Offline';
            elements.latency.textContent = '--ms';
        }
    });
}

// Enviar mensagem
async function sendMessage() {
    const message = elements.messageInput.value.trim();
    if (!message || !state.isConnected) return;
    
    // Desabilitar interface durante envio
    setInputState(false);
    showLoading(true);
    
    // Adicionar mensagem do usuário
    addMessage(message, 'user');
    
    // Limpar input
    elements.messageInput.value = '';
    elements.charCounter.textContent = '0/500';
    elements.charCounter.style.color = 'var(--gray-400)';
    
    try {
        const startTime = Date.now();
        
        // Enviar para API com retry
        const response = await fetchWithRetry(`${CONFIG.API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ pergunta: message })
        });
        
        const responseTime = Date.now() - startTime;
        state.responseTimes.push(responseTime);
        
        const data = await response.json();
        
        // Processar resposta
        if (data.status === 'sucesso') {
            handleSuccessResponse(data);
            state.answeredQuestions++;
            
            if (data.query) {
                state.executedQueries++;
                await executeQuery(data);
            }
            
            showToast('Pergunta processada com sucesso! ✅', 'success');
        } else {
            handleErrorResponse(data);
            showToast('Não foi possível processar a pergunta 😕', 'warning');
        }
        
        // Atualizar estatísticas
        state.questionCount++;
        state.lastQuery = {
            text: message,
            timestamp: new Date()
        };
        
        updateUI();
        saveStats();
        
    } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
        addMessage('Desculpe, ocorreu um erro ao processar sua pergunta. Verifique se a API está funcionando.', 'assistant', true);
        showToast('Erro de conexão com a API 🔌', 'error');
    } finally {
        showLoading(false);
        setInputState(true);
        elements.messageInput.focus();
    }
}

// Enviar pergunta rápida
function sendQuickQuestion(question) {
    elements.messageInput.value = question;
    sendMessage();
}

// Processar resposta de sucesso
function handleSuccessResponse(data) {
    let responseText = `Perfeito! Encontrei as informações que você procura. 🎯\n\n`;
    responseText += `**${data.pergunta_da_query}**\n\n`;
    
    if (data.query) {
        responseText += `Aqui está a consulta SQL correspondente:`;
        addMessage(responseText, 'assistant');
        addQueryDisplay(data.query);
    } else {
        addMessage(responseText, 'assistant');
    }
}

// Processar resposta de erro
function handleErrorResponse(data) {
    let errorText = `Hmm, não consegui entender sua pergunta. 🤔\n\n`;
    errorText += `${data.mensagem || 'Tente reformular sua pergunta ou use uma das opções sugeridas.'}\n\n`;
    errorText += `**Perguntas que posso responder:**\n`;
    errorText += `• Vendas por tipo de pagamento 💳\n`;
    errorText += `• Produtos mais vendidos 📦\n`;
    errorText += `• Custo das estadias por pet 🏨`;
    
    addMessage(errorText, 'assistant', true);
}

// Executar query para mostrar resultados
async function executeQuery(chatData) {
    try {
        let queryType = determineQueryType(chatData.pergunta_do_usuario);
        
        if (queryType) {
            const response = await fetchWithRetry(`${CONFIG.API_BASE_URL}/execute-query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tipo_query: queryType })
            });
            
            const data = await response.json();
            
            if (data.status === 'sucesso' && data.resultado) {
                displayQueryResults(data.resultado, queryType);
            }
        }
    } catch (error) {
        console.error('Erro ao executar query:', error);
    }
}

// Determinar tipo de query
function determineQueryType(pergunta) {
    const perguntaLower = pergunta.toLowerCase();
    
    if (perguntaLower.includes('vendas') && perguntaLower.includes('pagamento')) {
        return 'vendas_por_pagamento';
    } else if (perguntaLower.includes('produtos') && perguntaLower.includes('vendidos')) {
        return 'produtos_mais_vendidos';
    } else if (perguntaLower.includes('estadias') && perguntaLower.includes('pet')) {
        return 'estadias_por_pet';
    }
    
    return null;
}

// Exibir resultados da query
function displayQueryResults(results, queryType) {
    let resultText = `\n\n**📊 Resultados:**\n\n`;
    
    const entries = Object.entries(results);
    if (entries.length > 0) {
        entries.slice(0, 5).forEach(([key, value]) => {
            if (queryType === 'vendas_por_pagamento') {
                resultText += `💳 **${key}:** R$ ${value.toFixed(2)}\n`;
            } else if (queryType === 'produtos_mais_vendidos') {
                resultText += `📦 **${key}:** ${value} unidades\n`;
            } else if (queryType === 'estadias_por_pet') {
                resultText += `🐾 **${key}:** R$ ${value.toFixed(2)}\n`;
            }
        });
        
        if (entries.length > 5) {
            resultText += `\n*... e mais ${entries.length - 5} itens.*`;
        }
    } else {
        resultText += `Nenhum resultado encontrado.`;
    }
    
    addMessage(resultText, 'assistant');
}

// Adicionar mensagem ao chat
function addMessage(text, sender, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    
    if (sender === 'user') {
        avatarDiv.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
            </svg>
        `;
    } else {
        avatarDiv.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 8V4H8"/>
                <rect width="16" height="12" x="4" y="8" rx="2"/>
                <path d="M2 14h2"/>
                <path d="M20 14h2"/>
                <path d="M15 13v2"/>
                <path d="M9 13v2"/>
            </svg>
        `;
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.innerHTML = processMarkdown(text);
    
    if (isError) {
        textDiv.style.borderLeftColor = 'var(--error-500)';
    }
    
    contentDiv.appendChild(textDiv);
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    elements.chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Adicionar display de query SQL
function addQueryDisplay(query) {
    const queryDiv = document.createElement('div');
    queryDiv.className = 'query-display';
    queryDiv.textContent = query;
    
    const lastMessage = elements.chatMessages.lastElementChild;
    const messageContent = lastMessage.querySelector('.message-content');
    messageContent.appendChild(queryDiv);
    
    scrollToBottom();
}

// Processar markdown simples
function processMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>')
        .replace(/•/g, '&bull;');
}

// Controlar estado do input
function setInputState(enabled) {
    elements.messageInput.disabled = !enabled;
    elements.sendButton.disabled = !enabled;
    
    if (enabled) {
        elements.messageInput.focus();
    }
}

// Mostrar/ocultar loading
function showLoading(show) {
    if (show) {
        elements.loadingOverlay.classList.add('show');
    } else {
        elements.loadingOverlay.classList.remove('show');
    }
}

// Scroll para o final do chat
function scrollToBottom() {
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

// Atualizar interface
function updateUI() {
    elements.totalQuestions.textContent = state.questionCount;
    elements.questionsAnswered.textContent = state.answeredQuestions;
    elements.queriesExecuted.textContent = state.executedQueries;
    
    // Tempo de resposta médio
    if (state.responseTimes.length > 0) {
        const avgTime = state.responseTimes.reduce((a, b) => a + b, 0) / state.responseTimes.length;
        elements.avgResponse.textContent = `${Math.round(avgTime)}ms`;
    }
    
    // Última query
    if (state.lastQuery) {
        const timeString = state.lastQuery.timestamp.toLocaleTimeString('pt-BR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        const shortText = state.lastQuery.text.substring(0, 20);
        elements.lastQuery.textContent = `${timeString} - ${shortText}${state.lastQuery.text.length > 20 ? '...' : ''}`;
    }
}

// Alternar tema
function toggleTheme() {
    const newTheme = state.theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

// Definir tema
function setTheme(theme) {
    state.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Atualizar ícone do botão
    const icon = elements.themeToggle.querySelector('svg');
    if (theme === 'dark') {
        icon.innerHTML = `
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        `;
    } else {
        icon.innerHTML = `
            <circle cx="12" cy="12" r="5"/>
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
        `;
    }
}

// Mostrar toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = getToastIcon(type);
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-message">${message}</div>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    // Remover após duração especificada
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, CONFIG.TOAST_DURATION);
}

// Obter ícone do toast
function getToastIcon(type) {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    return icons[type] || icons.info;
}

// Fetch com timeout
async function fetchWithTimeout(url, options = {}, timeout = 10000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
}

// Fetch com retry
async function fetchWithRetry(url, options = {}, retries = CONFIG.MAX_RETRIES) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetchWithTimeout(url, options);
            if (response.ok) {
                return response;
            }
            throw new Error(`HTTP ${response.status}`);
        } catch (error) {
            if (i === retries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, CONFIG.RETRY_DELAY * (i + 1)));
        }
    }
}

// Salvar estatísticas
function saveStats() {
    const stats = {
        questionCount: state.questionCount,
        answeredQuestions: state.answeredQuestions,
        executedQueries: state.executedQueries,
        responseTimes: state.responseTimes.slice(-10) // Manter apenas os últimos 10
    };
    localStorage.setItem('chatStats', JSON.stringify(stats));
}

// Carregar estatísticas salvas
function loadSavedStats() {
    try {
        const saved = localStorage.getItem('chatStats');
        if (saved) {
            const stats = JSON.parse(saved);
            state.questionCount = stats.questionCount || 0;
            state.answeredQuestions = stats.answeredQuestions || 0;
            state.executedQueries = stats.executedQueries || 0;
            state.responseTimes = stats.responseTimes || [];
        }
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

// Função para debug (disponível no console)
window.debugChat = {
    state,
    elements,
    checkApiHealth,
    showToast,
    clearStats: () => {
        localStorage.removeItem('chatStats');
        location.reload();
    }
};

