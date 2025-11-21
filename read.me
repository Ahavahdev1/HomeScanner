# 🛡️ AHAVA-GUARD: Windows Security Auditor

> **Auditoria de Segurança Reversa e Hardening para Windows**

O **AHAVA-GUARD** é uma ferramenta de auto-diagnóstico escrita em Python puro. Ela simula localmente as técnicas de reconhecimento utilizadas por atacantes (Red Team) para verificar se o seu computador possui vulnerabilidades críticas expostas na rede.

Diferente de scanners complexos, este script foca em configurações específicas do ecossistema Windows (SMB, Registro, RPC) que muitas vezes passam despercebidas.

---

## 🚀 Funcionalidades

O script executa automaticamente 4 módulos de verificação:

1.  **🕵️ Teste de Sessão Nula (Null Session)**
    *   *Técnica:* Tenta conectar ao compartilhamento oculto `IPC$` sem credenciais.
    *   *Simula:* `smbclient -N` ou ataques de enumeração anônima.
    *   *Objetivo:* Verificar se hackers podem listar usuários/arquivos sem senha.

2.  **🦠 Verificação SMBv1 (EternalBlue)**
    *   *Técnica:* Analisa chaves do Registro do Windows e configurações do PowerShell.
    *   *Simula:* `nmap --script smb-vuln-ms17-010`
    *   *Objetivo:* Garantir que o protocolo obsoleto e perigoso (alvo do WannaCry) esteja desativado.

3.  **📝 Enumeração de Registro (RestrictAnonymous)**
    *   *Técnica:* Lê a chave `Lsa\RestrictAnonymous`.
    *   *Simula:* `enum4linux`
    *   *Objetivo:* Validar se o sistema impede que anônimos coletem listas de contas do sistema.

4.  **🔥 Scan de Portas Ativo (Auto IP)**
    *   *Técnica:* Detecta o IP real da máquina e tenta conexões via socket.
    *   *Simula:* `nmap -F`
    *   *Objetivo:* Verificar se o Firewall está bloqueando corretamente portas críticas (445, 3389, 135) para conexões externas.

---

## 📦 Instalação das Bibliotecas

Uma das principais vantagens do **AHAVA-GUARD** é que ele não possui dependências externas. **Você NÃO precisa usar o `pip install`.**

O script utiliza apenas a **Biblioteca Padrão (Standard Library)** que já vem instalada junto com o Python:

*   `socket` (Conexões de rede)
*   `winreg` (Acesso ao Registro do Windows)
*   `ctypes` (Interação com APIs do sistema)
*   `subprocess` (Execução de comandos CMD/PowerShell)
*   `os` & `sys` (Sistema operacional)

### O único requisito é ter o Python instalado:
1.  Baixe o Python em [python.org](https://www.python.org/downloads/).
2.  Durante a instalação, marque a opção **"Add Python to PATH"**.

---

## 🛠️ Como Executar

Como o script acessa configurações protegidas do sistema (Registro e Rede), ele precisa de privilégios elevados.

1.  **Baixe o código:**
    Salve o arquivo como `ahava_guard.py`.

2.  **Abra o terminal como Administrador:**
    *   Clique com botão direito no CMD ou PowerShell > *"Executar como Administrador"*.

3.  **Rode o comando:**
    ```bash
    python ahava_guard.py
    ```

## 🔍 Interpretando o Relatório

O programa utiliza um sistema de cores para facilitar a leitura:

| Cor | Significado | Ação Recomendada |
| :--- | :--- | :--- |
| 🟢 **VERDE** | **SEGURO** | Nenhuma ação necessária. Configuração correta. |
| 🟡 **AMARELO** | **ALERTA** | Configuração padrão do Windows (pode ser melhorada). |
| 🔴 **VERMELHO** | **PERIGO** | Vulnerabilidade detectada! Feche a porta ou altere o registro. |

## ⚠️ Aviso Legal (Disclaimer)

Esta ferramenta foi desenvolvida para fins **educacionais e de defesa (Blue Team)**. O objetivo é ajudar administradores e usuários a protegerem seus próprios sistemas (Self-Check).

Não utilize este código para auditar redes ou computadores de terceiros sem autorização explícita. O autor não se responsabiliza pelo mau uso da ferramenta.

---

<div align="center">
    <p><b>Desenvolvido por ahavadev</b></p>
    <p>🔒 Secure your world.</p>
</div>
