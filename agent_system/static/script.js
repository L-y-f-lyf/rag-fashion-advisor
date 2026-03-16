// ==================== 全局变量 ====================
const API_BASE_URL = window.location.origin;
let currentApiKey = '';

// ==================== 初始化 ====================
document.addEventListener('DOMContentLoaded', function() {
    // 从 localStorage 加载 API Key
    const savedApiKey = localStorage.getItem('dashscope_api_key');
    if (savedApiKey) {
        document.getElementById('apiKey').value = savedApiKey;
        currentApiKey = savedApiKey;
    }
});

// ==================== 保存 API Key ====================
function saveApiKey() {
    const apiKey = document.getElementById('apiKey').value.trim();
    if (apiKey) {
        localStorage.setItem('dashscope_api_key', apiKey);
        currentApiKey = apiKey;
    }
}

// ==================== 获取 API Key ====================
function getApiKey() {
    const apiKey = document.getElementById('apiKey').value.trim();
    if (!apiKey) {
        alert('请先输入通义千问 API Key！');
        return null;
    }
    return apiKey;
}

// ==================== 切换标签页 ====================
function switchTab(tab) {
    // 移除所有激活状态
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });

    // 激活当前标签
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
    document.getElementById(`${tab}Tab`).classList.add('active');
}

// ==================== 显示/隐藏加载状态 ====================
function showLoading(text = '正在处理...') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.querySelector('.loading-text');
    loadingText.textContent = text;
    overlay.classList.add('show');
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.remove('show');
}

// ==================== 添加消息到聊天界面 ====================
function addMessage(content, type) {
    const messagesContainer = document.getElementById('ragMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = content.replace(/\n/g, '<br>');

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    // 滚动到底部
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ==================== 发送 RAG 消息 ====================
async function sendRAGMessage() {
    const input = document.getElementById('ragInput');
    const message = input.value.trim();

    if (!message) {
        alert('请输入消息！');
        return;
    }

    const apiKey = getApiKey();
    if (!apiKey) return;

    // 显示用户消息
    addMessage(message, 'user');
    input.value = '';

    // 显示加载状态
    showLoading('正在从知识库检索相关信息...');

    try {
        const response = await fetch(`${API_BASE_URL}/rag/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: message,
                api_key: apiKey
            })
        });

        const data = await response.json();

        if (data.success) {
            addMessage(data.answer, 'assistant');
        } else {
            addMessage(`抱歉，处理请求时出错：${data.error || '未知错误'}`, 'assistant');
        }
    } catch (error) {
        console.error('RAG 聊天错误:', error);
        addMessage(`网络错误：${error.message}`, 'assistant');
    } finally {
        hideLoading();
    }
}

// ==================== 发送 Agent 消息 ====================
async function sendAgentMessage() {
    const input = document.getElementById('agentInput');
    const message = input.value.trim();

    if (!message) {
        alert('请输入消息！');
        return;
    }

    const apiKey = getApiKey();
    if (!apiKey) return;

    input.value = '';
    showLoading('Agent 正在思考...');

    try {
        const response = await fetch(`${API_BASE_URL}/agent/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                api_key: apiKey
            })
        });

        const data = await response.json();

        if (data.success) {
            displayOutfitResult(data.answer);
        } else {
            const resultContent = document.getElementById('resultContent');
            resultContent.innerHTML = `
                <div class="outfit-result">
                    <div class="outfit-section">
                        <h4>错误</h4>
                        <p>${data.error || '未知错误'}</p>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Agent 聊天错误:', error);
        const resultContent = document.getElementById('resultContent');
        resultContent.innerHTML = `
            <div class="outfit-result">
                <div class="outfit-section">
                    <h4>网络错误</h4>
                    <p>${error.message}</p>
                </div>
            </div>
        `;
    } finally {
        hideLoading();
    }
}

// ==================== 生成穿搭方案 ====================
async function generateOutfit() {
    // 获取表单数据
    const gender = document.querySelector('input[name="gender"]:checked').value;
    const scene = document.getElementById('scene').value;
    const bodyType = document.getElementById('bodyType').value;
    const style = document.getElementById('style').value;
    const additionalRequest = document.getElementById('additionalRequest').value.trim();

    const apiKey = getApiKey();
    if (!apiKey) return;

    showLoading('正在为您生成个性化穿搭方案...');

    try {
        const response = await fetch(`${API_BASE_URL}/outfit/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                gender: gender,
                scene: scene,
                body_type: bodyType,
                style: style,
                additional_request: additionalRequest,
                api_key: apiKey
            })
        });

        const data = await response.json();

        if (data.success) {
            displayOutfitResult(data.answer);
        } else {
            const resultContent = document.getElementById('resultContent');
            resultContent.innerHTML = `
                <div class="outfit-result">
                    <div class="outfit-section">
                        <h4>错误</h4>
                        <p>${data.error || '未知错误'}</p>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('生成穿搭方案错误:', error);
        const resultContent = document.getElementById('resultContent');
        resultContent.innerHTML = `
            <div class="outfit-result">
                <div class="outfit-section">
                    <h4>网络错误</h4>
                    <p>${error.message}</p>
                </div>
            </div>
        `;
    } finally {
        hideLoading();
    }
}

// ==================== 展示穿搭方案结果 ====================
function displayOutfitResult(answer) {
    const resultContent = document.getElementById('resultContent');

    // 简单的格式化处理（可根据实际返回格式调整）
    let html = '<div class="outfit-result">';

    // 尝试解析结构化内容
    const sections = [
        { pattern: /【穿搭原则】/i, title: '📌 穿搭原则' },
        { pattern: /【单品推荐】/i, title: '👕 单品推荐' },
        { pattern: /【配色建议】/i, title: '🎨 配色建议' },
        { pattern: /【搭配技巧】/i, title: '💡 搭配技巧' }
    ];

    let currentSection = '';
    let sectionContent = {};
    let content = answer;

    // 分割内容到各个部分
    sections.forEach((section, index) => {
        const match = content.match(section.pattern);
        if (match) {
            const parts = content.split(section.pattern);
            if (currentSection && parts[0].trim()) {
                sectionContent[currentSection] = parts[0].trim();
            }
            currentSection = section.title;
            content = parts[1] || '';
        }

        // 处理最后一部分
        if (index === sections.length - 1 && currentSection && content.trim()) {
            sectionContent[currentSection] = content.trim();
        }
    });

    // 如果没有成功分割，则整体显示
    if (Object.keys(sectionContent).length === 0) {
        html += `
            <div class="outfit-section">
                <h4>穿搭方案</h4>
                <div class="outfit-text">${formatText(answer)}</div>
            </div>
        `;
    } else {
        // 显示结构化内容
        for (const [title, content] of Object.entries(sectionContent)) {
            html += `
                <div class="outfit-section">
                    <h4>${title}</h4>
                    <div class="outfit-text">${formatText(content)}</div>
                </div>
            `;
        }
    }

    html += '</div>';
    resultContent.innerHTML = html;
}

// ==================== 格式化文本 ====================
function formatText(text) {
    // 将换行符转换为 <br>
    let formatted = text.replace(/\n\n/g, '<br><br>');

    // 处理列表项（数字开头的行）
    formatted = formatted.replace(/^(\d+[\.\、])\s+/gm, '<br>$1 ');

    // 处理带符号的列表项（-、* 等符号）
    formatted = formatted.replace(/^[-*•]\s+/gm, '<br>• ');

    // 处理中括号标记的内容（如【1】）
    formatted = formatted.replace(/【(\d+)】/g, '<br><strong>【$1】</strong>');

    // 处理序号（1. 2. 等）
    formatted = formatted.replace(/^(\d+)\.\s+/gm, '<br><strong>$1.</strong> ');

    // 移除开头的 <br>
    formatted = formatted.replace(/^<br>/, '');

    return formatted;
}

// ==================== 工具函数 ====================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
