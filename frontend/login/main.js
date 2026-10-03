/**
 * Fire Watcher — Lógica Principal da Tela de Login Standalone
 * Gerencia a animação orientada por scroll (lerp), interações do card "Liquid Glass",
 * reflexos dinâmicos e autenticação com stub de redirecionamento para o Streamlit.
 */

import { GalaxyBackground } from './galaxy.js';

// ==========================================================================
// Configuração Global do Sistema
// ==========================================================================

/**
 * URL de redirecionamento pós-autenticação para o dashboard principal Streamlit.
 * Altere conforme o ambiente de implantação.
 */
const REDIRECT_URL = "http://localhost:8501";

// ==========================================================================
// Inicialização do Motor WebGL e Seleção de Elementos DOM
// ==========================================================================

const galaxy = new GalaxyBackground('galaxy-canvas');

const scrollWrapper = document.getElementById('scroll-wrapper');
const heroLayer = document.getElementById('hero-layer');
const loginCard = document.getElementById('login-card');
const heroScrollBtn = document.getElementById('hero-scroll-btn');
const scrollIndicator = document.getElementById('scroll-indicator');

const loginForm = document.getElementById('login-form');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const btnTogglePassword = document.getElementById('btn-toggle-password');
const btnSubmit = document.getElementById('btn-submit');
const formAlert = document.getElementById('form-alert');
const linkForgot = document.getElementById('link-forgot');

// ==========================================================================
// Estado de Scroll Suavizado com Lerp (Linear Interpolation)
// ==========================================================================

let targetProgress = 0.0;
let currentProgress = 0.0;
const LERP_FACTOR = 0.085;

const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function getScrollProgress() {
    if (!scrollWrapper) return 0;
    const maxScroll = scrollWrapper.scrollHeight - window.innerHeight;
    if (maxScroll <= 0) return 1;
    return Math.min(Math.max(window.scrollY / maxScroll, 0), 1);
}

function updateScrollLoop() {
    targetProgress = getScrollProgress();

    if (prefersReducedMotion) {
        currentProgress = targetProgress;
    } else {
        currentProgress += (targetProgress - currentProgress) * LERP_FACTOR;
    }

    // 1. Atualização do Hero Layer (Progress 0 -> 1: sobe 40px e fade out)
    const heroOpacity = Math.max(0, 1 - Math.pow(currentProgress * 1.4, 1.2));
    const heroTranslateY = -currentProgress * 45;
    heroLayer.style.opacity = heroOpacity.toFixed(3);
    heroLayer.style.transform = `translateY(${heroTranslateY.toFixed(1)}px)`;
    heroLayer.style.pointerEvents = currentProgress > 0.35 ? 'none' : 'auto';

    // 2. Atualização do Card de Login Liquid Glass (Progress 0 -> 1: sobe de 55vh até 0)
    const cardTranslateY = (1 - currentProgress) * 55;
    const cardOpacity = Math.min(Math.max((currentProgress - 0.05) / 0.85, 0), 1);
    const cardScale = 0.94 + 0.06 * currentProgress;
    const cardBlur = (1 - currentProgress) * 14;

    loginCard.style.transform = `translate3d(0, ${cardTranslateY.toFixed(1)}vh, 0) scale(${cardScale.toFixed(3)})`;
    loginCard.style.opacity = cardOpacity.toFixed(3);
    loginCard.style.filter = cardBlur > 0.2 ? `blur(${cardBlur.toFixed(1)}px)` : 'none';
    loginCard.style.pointerEvents = currentProgress > 0.65 ? 'auto' : 'none';

    // 3. Comunicação com a Galáxia WebGL
    galaxy.setScrollProgress(currentProgress);

    requestAnimationFrame(updateScrollLoop);
}

requestAnimationFrame(updateScrollLoop);

// ==========================================================================
// Interatividade do Card Liquid Glass
// ==========================================================================

// Reflexo especular dinâmico que rastreia o cursor do mouse sobre o card
loginCard.addEventListener('mousemove', (e) => {
    const rect = loginCard.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    loginCard.style.setProperty('--mx', `${x}px`);
    loginCard.style.setProperty('--my', `${y}px`);
});

// Ações de rolagem suave até o card de login
function scrollToCard() {
    const maxScroll = scrollWrapper.scrollHeight - window.innerHeight;
    window.scrollTo({
        top: maxScroll,
        behavior: prefersReducedMotion ? 'auto' : 'smooth'
    });
}

if (heroScrollBtn) heroScrollBtn.addEventListener('click', scrollToCard);
if (scrollIndicator) scrollIndicator.addEventListener('click', scrollToCard);

// Auto-scroll para o card quando qualquer campo receber foco do teclado
[usernameInput, passwordInput].forEach((input) => {
    input.addEventListener('focus', () => {
        if (currentProgress < 0.8) {
            scrollToCard();
        }
    });
});

// Alternar visibilidade da senha
btnTogglePassword.addEventListener('click', () => {
    const isPassword = passwordInput.getAttribute('type') === 'password';
    passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
    btnTogglePassword.classList.toggle('active', isPassword);
    btnTogglePassword.setAttribute(
        'aria-label',
        isPassword ? 'Ocultar senha' : 'Mostrar senha'
    );
});

// Link "Esqueci minha senha"
linkForgot.addEventListener('click', (e) => {
    e.preventDefault();
    showAlert("O serviço de recuperação de credenciais estará disponível em breve com a integração LDAP/OAuth institucional.", "info");
});

// ==========================================================================
// Gerenciamento de Alertas e Validação Inline
// ==========================================================================

function showAlert(message, type = "error") {
    formAlert.textContent = message;
    formAlert.className = `form-alert visible ${type}`;
}

function clearAlert() {
    formAlert.textContent = "";
    formAlert.className = "form-alert";
}

function triggerShake() {
    loginCard.classList.remove('shake');
    void loginCard.offsetWidth; // Força reflow para reiniciar animação
    loginCard.classList.add('shake');
    setTimeout(() => loginCard.classList.remove('shake'), 500);
}

// ==========================================================================
// Autenticação e Stub de Login
// ==========================================================================

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAlert();

    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    // Validação de campos vazios
    if (!username && !password) {
        showAlert("Por favor, preencha o usuário e a senha.");
        triggerShake();
        usernameInput.focus();
        return;
    }

    if (!username) {
        showAlert("O campo de usuário ou e-mail é obrigatório.");
        triggerShake();
        usernameInput.focus();
        return;
    }

    if (!password) {
        showAlert("O campo de senha é obrigatório.");
        triggerShake();
        passwordInput.focus();
        return;
    }

    // Estado visual de carregamento (Spinner ativo)
    setLoadingState(true);

    try {
        await handleLogin(username, password);
    } catch (error) {
        showAlert(error.message || "Falha na autenticação. Verifique suas credenciais.");
        triggerShake();
    } finally {
        setLoadingState(false);
    }
});

function setLoadingState(isLoading) {
    btnSubmit.disabled = isLoading;
    btnSubmit.classList.toggle('loading', isLoading);
    usernameInput.disabled = isLoading;
    passwordInput.disabled = isLoading;
}

/**
 * Função de Autenticação (Stub Simulado).
 * 
 * TODO: Implementar chamada real ao backend quando a autenticação for definida:
 * const response = await fetch('/api/auth/login', {
 *     method: 'POST',
 *     headers: { 'Content-Type': 'application/json' },
 *     body: JSON.stringify({ username, password })
 * });
 * const data = await response.json();
 */
async function handleLogin(username, password) {
    // Simulação de latência de rede suave (0.8 segundos)
    await new Promise((resolve) => setTimeout(resolve, 800));

    const cleanUser = username.trim().toLowerCase();
    const cleanPass = password.trim();

    const isUserValid = cleanUser === "teste" || cleanUser.startsWith("teste@");
    const isPassValid = cleanPass === "teste";

    if (!isUserValid || !isPassValid) {
        throw new Error("Credenciais inválidas. Para testar utilize usuário 'teste' e senha 'teste'.");
    }

    // Sucesso
    showAlert("Autenticação realizada com sucesso. Acessando painel...", "success");

    // Redireciona para o painel da aplicação
    setTimeout(() => {
        // Se a porta 5173 (React Vite) estiver ativa, direciona para o dashboard
        window.location.href = "http://localhost:5173/dashboard";
    }, 450);
}
