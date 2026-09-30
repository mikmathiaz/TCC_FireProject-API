# Guia Passo a Passo: Publicando o Fire Watcher no GitHub

Este guia orienta a publicação do projeto no GitHub e as boas práticas de versionamento para o seu TCC.

---

## 1. Criando o Repositório no GitHub (via Web)

1. Acesse sua conta no [GitHub](https://github.com/) e faça login.
2. No canto superior direito, clique no botão **+** e selecione **"New repository"**.
3. Preencha os campos:
   - **Repository name:** `fire-watcher` (ou outro nome de sua preferência)
   - **Description:** `Sistema de Monitoramento Inteligente e Detecção Precoce de Queimadas — TCC em Engenharia da Computação`
   - **Public / Private:** Escolha conforme sua preferência (se for público, qualquer um pode ver; se for privado, apenas você e orientadores autorizados).
4. **IMPORTANTE:**
   - **NÃO** marque a opção *"Add a README file"*.
   - **NÃO** adicione *.gitignore* nem *License* nessa tela.
   - *(O projeto já possui `.gitignore` e `README.md` completos configurados na sua máquina).*
5. Clique em **"Create repository"**.

---

## 2. Conectando seu Código Local ao Repositório Criado

O repositório Git local já foi inicializado e seu primeiro commit acadêmico já foi registrado.

Agora, basta abrir o terminal na pasta do projeto (`C:\Users\mikae\.gemini\antigravity-ide\scratch\fire-watcher`) e executar os seguintes comandos:

```bash
# 1. Vincular o repositório remoto (substitua SEU_USUARIO e NOME_DO_REPOSITORIO pelo link que o GitHub gerou)
git remote add origin https://github.com/SEU_USUARIO/fire-watcher.git

# 2. Enviar os arquivos para a branch principal (main)
git push -u origin main
```

*(Se o Git solicitar autenticação, realize o login pelo navegador ou utilize um Personal Access Token do GitHub).*

---

## 3. Fluxo de Trabalho Git para o TCC (Dia a Dia)

Sempre que fizermos novas alterações ou adicionarmos novos módulos:

```bash
# Verificar arquivos modificados
git status

# Adicionar as modificações ao pacote de envio
git add .

# Criar um commit com mensagem descritiva (padrão Conventional Commits)
git commit -m "feat: adiciona nova funcionalidade X"

# Enviar para o GitHub
git push
```
