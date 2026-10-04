import ctypes
import os
import socket
import subprocess
import sys
import winreg

def ativar_ansi_windows():
    """Habilita suporte nativo a cores ANSI no console do Windows."""
    if os.name == 'nt':
        kernel32 = ctypes.windll.kernel32
        h_stdout = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(h_stdout, ctypes.byref(mode))
        kernel32.SetConsoleMode(h_stdout, mode.value | 0x0004)

class Cores:
    VERDE = '\033[92m'
    VERMELHO = '\033[91m'
    AMARELO = '\033[93m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'
    NEGRITO = '\033[1m'
    RESET = '\033[0m'

class Relatorio:
    def __init__(self):
        self.seguros = 0
        self.alertas = 0
        self.criticos = 0

    def add_seguro(self): self.seguros += 1
    def add_alerta(self): self.alertas += 1
    def add_critico(self): self.criticos += 1

relatorio = Relatorio()

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def obter_ip_local() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        s.close()

def exibir_banner():
    banner = r"""
    █████╗ ██╗  ██╗ █████╗ ██╗   ██╗ █████╗ ██████╗ ███████╗██╗   ██╗
   ██╔══██╗██║  ██║██╔══██╗██║   ██║██╔══██╗██╔══██╗██╔════╝██║   ██║
   ███████║███████║███████║██║   ██║███████║██║  ██║█████╗  ██║   ██║
   ██╔══██║██╔══██║██╔══██║╚██╗ ██╔╝██╔══██║██║  ██║██╔══╝  ╚██╗ ██╔╝
   ██║  ██║██║  ██║██║  ██║ ╚████╔╝ ██║  ██║██████╔╝███████╗ ╚████╔╝ 
   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═════╝ ╚══════╝  ╚═══╝ 
    """
    print(f"{Cores.CIANO}{banner}{Cores.RESET}")
    print(f"{Cores.NEGRITO}{' ' * 20}WINDOWS SECURITY AUDITOR v2.2{Cores.RESET}")
    print(f"{Cores.VERDE}{' ' * 24}Coded by: ahavadev{Cores.RESET}")
    print(f"\n{Cores.NEGRITO}{'='*70}{Cores.RESET}")

def titulo(texto: str):
    print(f"\n{Cores.NEGRITO}{'='*70}")
    print(f" {texto}")
    print(f"{'='*70}{Cores.RESET}")

def regra_firewall_existe(porta: int) -> bool:
    """Verifica se a regra de bloqueio criada pelo auditor está ativa no Firewall."""
    nome_regra = f"[Auditor]_Bloqueio_Porta_{porta}"
    cmd = ["netsh", "advfirewall", "firewall", "show", "rule", f"name={nome_regra}"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0

# ---------------------------------------------------------
# Testes de Segurança
# ---------------------------------------------------------
def teste_null_session(ip_alvo: str):
    titulo("1. Teste de Sessão Nula (Acesso Anônimo a IPC$)")
    print(f"{Cores.AZUL}[INFO]{Cores.RESET} Conectando a \\\\{ip_alvo}\\IPC$ sem credenciais...")
    
    cmd_conectar = ["net", "use", f"\\\\{ip_alvo}\\IPC$", "", "/u:"]
    cmd_desconectar = ["net", "use", f"\\\\{ip_alvo}\\IPC$", "/delete", "/y"]

    res = subprocess.run(cmd_conectar, capture_output=True, text=True)
    
    if res.returncode == 0:
        print(f"{Cores.VERMELHO}[CRÍTICO] Conexão Nula BEM-SUCEDIDA!{Cores.RESET}")
        print(" -> O computador permite logon anônimo a recursos IPC$.")
        subprocess.run(cmd_desconectar, capture_output=True)
        relatorio.add_critico()
    else:
        print(f"{Cores.VERDE}[SEGURO] Conexão anônima recusada pelo sistema.{Cores.RESET}")
        relatorio.add_seguro()

def teste_vulnerabilidade_smb():
    titulo("2. Verificação de SMBv1 (MS17-010 / EternalBlue)")
    print(f"{Cores.AZUL}[INFO]{Cores.RESET} Consultando configuração do serviço LanmanServer...")
    
    smb1_ativo = False

    try:
        caminho = r"SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, caminho) as key:
            valor, _ = winreg.QueryValueEx(key, "SMB1")
            if valor == 1:
                smb1_ativo = True
    except FileNotFoundError:
        cmd_ps = "Get-SmbServerConfiguration | Select-Object -ExpandProperty EnableSMB1Protocol"
        res = subprocess.run(["powershell", "-NoProfile", "-Command", cmd_ps], capture_output=True, text=True)
        if "True" in res.stdout:
            smb1_ativo = True
    except Exception:
        pass

    if smb1_ativo:
        print(f"{Cores.VERMELHO}[CRÍTICO] VULNERÁVEL: SMBv1 está habilitado!{Cores.RESET}")
        print(" -> Recomendação: Desative o recurso SMB 1.0/CIFS imediatamente.")
        relatorio.add_critico()
    else:
        print(f"{Cores.VERDE}[SEGURO] O protocolo legado SMBv1 está desativado.{Cores.RESET}")
        relatorio.add_seguro()

def teste_smb_signing():
    titulo("3. Assinatura Digital de Pacotes SMB (Anti-NTLM Relay)")
    print(f"{Cores.AZUL}[INFO]{Cores.RESET} Verificando exigência de assinatura SMB no LanmanServer...")

    caminho = r"SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, caminho) as key:
            requer_assinatura, _ = winreg.QueryValueEx(key, "requiresecuritysignature")
    except (FileNotFoundError, OSError):
        requer_assinatura = 0

    if requer_assinatura == 1:
        print(f"{Cores.VERDE}[SEGURO] Assinatura SMB é OBRIGATÓRIA (RequireSecuritySignature = 1).{Cores.RESET}")
        relatorio.add_seguro()
    else:
        print(f"{Cores.AMARELO}[ALERTA] Assinatura SMB NÃO é obrigatória.{Cores.RESET}")
        print(" -> Em redes locais não confiáveis, este host pode estar vulnerável a NTLM Relay.")
        relatorio.add_alerta()

def teste_enum4linux():
    titulo("4. Restrição de Enumeração Anônima (LSA)")
    caminho = r"SYSTEM\CurrentControlSet\Control\Lsa"

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, caminho) as key:
            valor, _ = winreg.QueryValueEx(key, "restrictanonymous")
        
        if valor == 0:
            print(f"{Cores.AMARELO}[ALERTA] RestrictAnonymous = 0.{Cores.RESET}")
            print(" -> Permite enumeração restrita de nomes/SIDs por clientes anônimos.")
            relatorio.add_alerta()
        elif valor == 1:
            print(f"{Cores.VERDE}[BOM] RestrictAnonymous = 1 (Apenas usuários autenticados enumeram).{Cores.RESET}")
            relatorio.add_seguro()
        elif valor == 2:
            print(f"{Cores.VERDE}[EXCELENTE] RestrictAnonymous = 2 (Acesso anônimo bloqueado).{Cores.RESET}")
            relatorio.add_seguro()
    except (FileNotFoundError, OSError):
        print(f"{Cores.AZUL}[INFO] Chave não definida explicitamente (adota o padrão seguro do Windows).{Cores.RESET}")
        relatorio.add_seguro()

def teste_ntlm_compatibility():
    titulo("5. Versão do Protocolo de Autenticação NTLM")
    caminho = r"SYSTEM\CurrentControlSet\Control\Lsa"

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, caminho) as key:
            valor, _ = winreg.QueryValueEx(key, "LmCompatibilityLevel")
        
        if valor < 3:
            print(f"{Cores.VERMELHO}[CRÍTICO] LmCompatibilityLevel = {valor}. NTLMv1 ainda permitido!{Cores.RESET}")
            print(" -> Sujeito a quebra rápida de hashes em trânsito.")
            relatorio.add_critico()
        elif valor in (3, 4):
            print(f"{Cores.AMARELO}[BOM] NTLMv2 em uso, mas compatibilidade com versões antigas ativa.{Cores.RESET}")
            relatorio.add_alerta()
        elif valor == 5:
            print(f"{Cores.VERDE}[EXCELENTE] LmCompatibilityLevel = 5. Apenas NTLMv2 aceito.{Cores.RESET}")
            relatorio.add_seguro()
    except (FileNotFoundError, OSError):
        print(f"{Cores.AZUL}[INFO] Chave LmCompatibilityLevel ausente (o Windows usa NTLMv2 por padrão).{Cores.RESET}")
        relatorio.add_seguro()

# ---------------------------------------------------------
# 6. Escaneamento e Mapeamento de Portas
# ---------------------------------------------------------
def teste_portas(ip_alvo: str):
    titulo("6. Mapeamento de Portas e Status do Firewall")
    print(f"{Cores.AZUL}[NOTA]{Cores.RESET} Conexões locais (deste PC para ele mesmo) ignoram regras de entrada do Firewall.")
    print("O script verifica o serviço local E se o Firewall já está protegendo a porta contra a rede.\n")

    portas = {
        135: ("RPC Endpoint Mapper", "Comunicação interna do Windows e chamadas RPC"),
        139: ("NetBIOS Session Service", "Compartilhamento legado de arquivos em rede"),
        445: ("SMB Direct Host", "Compartilhamento de pastas e impressoras na rede local"),
        3389: ("RDP", "Área de Trabalho Remota")
    }

    portas_abertas_sem_firewall = {}
    portas_bloqueadas_firewall = {}

    for porta, (nome, desc) in portas.items():
        bloqueado_no_firewall = regra_firewall_existe(porta)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)
        res = sock.connect_ex((ip_alvo, porta))
        sock.close()

        if res == 0:
            if bloqueado_no_firewall:
                print(f" Porta {porta:<5} ({nome:<26}): {Cores.VERDE}[PROTEGIDA NO FIREWALL]{Cores.RESET} (Ativa localmente, mas bloqueada para conexões externas)")
                portas_bloqueadas_firewall[porta] = (nome, desc)
                relatorio.add_seguro()
            else:
                print(f" Porta {porta:<5} ({nome:<26}): {Cores.VERMELHO}EXPOSTA / ABERTA{Cores.RESET} (Sem regra de bloqueio no Firewall)")
                portas_abertas_sem_firewall[porta] = (nome, desc)
                relatorio.add_alerta()
        else:
            print(f" Porta {porta:<5} ({nome:<26}): {Cores.VERDE}FECHADA / INATIVA{Cores.RESET}")
            relatorio.add_seguro()

    return portas_abertas_sem_firewall, portas_bloqueadas_firewall

# ---------------------------------------------------------
# 7. Remediação e Gerenciamento Interativo de Portas
# ---------------------------------------------------------
def gerenciar_regras_firewall(abertas: dict, bloqueadas: dict):
    if not abertas and not bloqueadas:
        return

    titulo("7. Assistente de Gerenciamento do Firewall")

    # Caso 1: Portas abertas sem proteção
    if abertas:
        print(f"{Cores.AMARELO}[PORTAS EXPOSTAS]{Cores.RESET} Deseja aplicar regras de bloqueio de entrada?")
        for porta, (nome, desc) in abertas.items():
            nome_regra = f"[Auditor]_Bloqueio_Porta_{porta}"
            print(f"\n{Cores.NEGRITO}Porta {porta} ({nome}){Cores.RESET}")
            print(f"Impacto do fechamento: {Cores.AMARELO}{desc}{Cores.RESET}")
            resp = input(f"Bloquear porta {porta} no Firewall? (s/n): ").strip().lower()
            if resp in ('s', 'sim', 'y', 'yes'):
                cmd = [
                    "netsh", "advfirewall", "firewall", "add", "rule",
                    f"name={nome_regra}", "dir=in", "action=block",
                    "protocol=TCP", f"localport={porta}"
                ]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0:
                    print(f"{Cores.VERDE}[OK] Porta {porta} bloqueada com sucesso.{Cores.RESET}")
                else:
                    print(f"{Cores.VERMELHO}[ERRO] Falha ao criar regra: {res.stderr.strip()}{Cores.RESET}")

    # Caso 2: Portas já protegidas (oferece reversão se necessário)
    if bloqueadas:
        print(f"\n{Cores.AZUL}[PORTAS JÁ PROTEGIDAS]{Cores.RESET} As seguintes portas já possuem regra ativa:")
        for porta, (nome, _) in bloqueadas.items():
            print(f" - Porta {porta} ({nome})")
        
        resp_reverter = input("\nDeseja reverter (desbloquear) alguma porta agora? (s/n): ").strip().lower()
        if resp_reverter in ('s', 'sim', 'y', 'yes'):
            for porta in bloqueadas.keys():
                remover = input(f"Desbloquear a porta {porta}? (s/n): ").strip().lower()
                if remover in ('s', 'sim', 'y', 'yes'):
                    nome_regra = f"[Auditor]_Bloqueio_Porta_{porta}"
                    cmd = ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={nome_regra}"]
                    res = subprocess.run(cmd, capture_output=True, text=True)
                    if res.returncode == 0:
                        print(f"{Cores.VERDE}[OK] Regra removida. Porta {porta} liberada.{Cores.RESET}")
                    else:
                        print(f"{Cores.VERMELHO}[ERRO] Falha ao remover regra.{Cores.RESET}")

# ---------------------------------------------------------
# Execução Principal
# ---------------------------------------------------------
def exibir_resumo():
    print(f"\n{Cores.NEGRITO}{'='*70}")
    print(" RESUMO DA AUDITORIA")
    print(f"{'='*70}{Cores.RESET}")
    print(f" Itens Seguros:     {Cores.VERDE}{relatorio.seguros}{Cores.RESET}")
    print(f" Alertas / Avisos:  {Cores.AMARELO}{relatorio.alertas}{Cores.RESET}")
    print(f" Falhas Críticas:   {Cores.VERMELHO}{relatorio.criticos}{Cores.RESET}")
    print("="*70)

def main():
    ativar_ansi_windows()
    os.system('cls' if os.name == 'nt' else 'clear')
    exibir_banner()
    
    if not is_admin():
        print(f"\n{Cores.VERMELHO}[!] ERRO: Execute este script como ADMINISTRADOR.{Cores.RESET}")
        input("\nPressione Enter para sair...")
        sys.exit(1)

    ip = obter_ip_local()
    print(f"[*] IP Detectado automaticamente: {Cores.AMARELO}{ip}{Cores.RESET}")
    print("O script usará este IP para simular um acesso externo.\n")

    teste_null_session(ip)
    teste_vulnerabilidade_smb()
    teste_smb_signing()
    teste_enum4linux()
    teste_ntlm_compatibility()
    
    abertas, bloqueadas = teste_portas(ip)
    exibir_resumo()

    gerenciar_regras_firewall(abertas, bloqueadas)

    print("\nAuditoria finalizada com sucesso.")
    input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()
