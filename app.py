import subprocess
import socket
import winreg
import ctypes
import os
import sys

class Cores:
    VERDE = '\033[92m'
    VERMELHO = '\033[91m'
    AMARELO = '\033[93m'
    RESET = '\033[0m'
    NEGRITO = '\033[1m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def obter_ip_local():
    """
    Tenta descobrir o IP real da máquina (aquele que aparece no ipconfig).
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def exibir_banner():
    # Banner gerado em estilo 'Block' para impacto visual
    banner = r"""
    █████╗ ██╗  ██╗ █████╗ ██╗   ██╗ █████╗ ██████╗ ███████╗██╗   ██╗
   ██╔══██╗██║  ██║██╔══██╗██║   ██║██╔══██╗██╔══██╗██╔════╝██║   ██║
   ███████║███████║███████║██║   ██║███████║██║  ██║█████╗  ██║   ██║
   ██╔══██║██╔══██║██╔══██║╚██╗ ██╔╝██╔══██║██║  ██║██╔══╝  ╚██╗ ██╔╝
   ██║  ██║██║  ██║██║  ██║ ╚████╔╝ ██║  ██║██████╔╝███████╗ ╚████╔╝ 
   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═════╝ ╚══════╝  ╚═══╝ 
    """
    print(f"{Cores.CIANO}{banner}{Cores.RESET}")
    print(f"{Cores.NEGRITO}{' ' * 20}WINDOWS SECURITY AUDITOR{Cores.RESET}")
    print(f"{Cores.VERDE}{' ' * 22}Coded by: ahavadev{Cores.RESET}")
    print(f"\n{Cores.NEGRITO}{'='*70}{Cores.RESET}")

def titulo(texto):
    print(f"\n{Cores.NEGRITO}{'='*70}")
    print(f" {texto}")
    print(f"{'='*70}{Cores.RESET}")

# ---------------------------------------------------------
# 1. REPLICA DO: smbclient -L //IP -N
# ---------------------------------------------------------
def teste_null_session(ip_alvo):
    titulo("1. Teste de Sessão Nula (Igual ao 'smbclient -N')")
    print(f"{Cores.AZUL}[INFO]{Cores.RESET} Tentando conectar em {ip_alvo} sem usuário e senha...")
    
    comando = f'net use \\\\{ip_alvo}\\IPC$ "" /u:""'
    
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        
        if "com êxito" in resultado.stdout or "successfully" in resultado.stdout:
            print(f"{Cores.VERMELHO}[PERIGO] Conexão Nula BEM SUCEDIDA!{Cores.RESET}")
            print(" -> Seu PC permite que estranhos listem arquivos sem senha.")
            print(" -> Resultado equivalente ao Kali: Listagem de pastas permitida.")
            os.system(f'net use \\\\{ip_alvo}\\IPC$ /delete >nul 2>&1')
        else:
            print(f"{Cores.VERDE}[SEGURO] A conexão foi recusada.{Cores.RESET}")
            print(f" -> O Windows bloqueou o acesso sem senha ao IP {ip_alvo}.")
            print(f" -> Resultado equivalente ao Kali: {Cores.NEGRITO}NT_STATUS_ACCESS_DENIED{Cores.RESET}")
            
    except Exception as e:
        print(f"[ERRO] Falha ao executar teste: {e}")

# ---------------------------------------------------------
# 2. REPLICA DO: nmap --script smb-vuln*
# ---------------------------------------------------------
def teste_vulnerabilidade_smb():
    titulo("2. Teste de Vulnerabilidade SMB (Igual ao 'nmap smb-vuln')")
    print(f"{Cores.AZUL}[INFO]{Cores.RESET} Verificando configuração interna do SMBv1...")
    
    vulneravel = False
    
    try:
        caminho = r"SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, caminho)
        try:
            valor, tipo = winreg.QueryValueEx(key, "SMB1")
            if valor == 1:
                vulneravel = True
        except FileNotFoundError:
            pass
    except:
        pass

    cmd = "Get-SmbServerConfiguration | Select-Object -ExpandProperty EnableSMB1Protocol"
    try:
        ps_resultado = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
        if "True" in ps_resultado.stdout.strip():
            vulneravel = True
    except:
        pass

    if vulneravel:
        print(f"{Cores.VERMELHO}[CRÍTICO] VULNERÁVEL! O SMBv1 está ativado.{Cores.RESET}")
        print(" -> Seu PC pode estar suscetível a ataques como EternalBlue.")
    else:
        print(f"{Cores.VERDE}[SEGURO] O SMBv1 está desativado.{Cores.RESET}")
        print(" -> Você está protegido contra as falhas antigas de SMB.")

# ---------------------------------------------------------
# 3. REPLICA DO: enum4linux
# ---------------------------------------------------------
def teste_enum4linux():
    titulo("3. Teste de Enumeração (Igual ao 'enum4linux')")
    print(f"{Cores.AZUL}[INFO]{Cores.RESET} Checando registro 'RestrictAnonymous'...")

    try:
        caminho = r"SYSTEM\CurrentControlSet\Control\Lsa"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, caminho)
        valor, tipo = winreg.QueryValueEx(key, "restrictanonymous")
        
        print(f" -> Valor atual da chave RestrictAnonymous: {valor}")
        
        if valor == 0:
            print(f"{Cores.AMARELO}[ALERTA] Valor 0 (Padrão).{Cores.RESET}")
            print(" -> Permite alguma enumeração, mas o bloqueio de sessão nula (teste 1) geralmente protege.")
        elif valor == 1:
            print(f"{Cores.VERDE}[BOM] Valor 1. A enumeração de contas é restrita.{Cores.RESET}")
        elif valor == 2:
            print(f"{Cores.VERDE}[EXCELENTE] Valor 2. Acesso anônimo totalmente bloqueado.{Cores.RESET}")
            
    except Exception as e:
        print(f"{Cores.AMARELO}[INFO] Chave de registro não encontrada (Usa padrão do Windows).{Cores.RESET}")

# ---------------------------------------------------------
# 4. REPLICA DO: nmap -F (Portas Abertas)
# ---------------------------------------------------------
def teste_portas_nmap(ip_alvo):
    titulo("4. Verificação de Portas (Igual ao 'nmap')")
    print(f"{Cores.AZUL}[INFO]{Cores.RESET} Escaneando o IP: {ip_alvo}")
    
    portas = [139, 445, 3389, 135]
    
    for porta in portas:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((ip_alvo, porta))
        estado = f"{Cores.VERMELHO}OPEN{Cores.RESET}" if result == 0 else f"{Cores.VERDE}CLOSED{Cores.RESET}"
        print(f" Porta {porta}: {estado}")
        sock.close()
    
    print(f"\n -> Se a porta 445 está {Cores.VERMELHO}OPEN{Cores.RESET}, mas o Teste 1 deu {Cores.VERDE}SEGURO{Cores.RESET},")
    print("    então seu firewall/autenticação está funcionando corretamente!")

def main():
    # Limpa a tela e exibe o banner
    os.system('cls')
    exibir_banner()
    
    if not is_admin():
        print(f"\n{Cores.VERMELHO}[!] ERRO: Execute este script como ADMINISTRADOR.{Cores.RESET}")
        input("Pressione Enter para sair...")
        return

    # --- DETECÇÃO AUTOMÁTICA DE IP ---
    meu_ip = obter_ip_local()
    print(f"[*] IP Detectado automaticamente: {Cores.AMARELO}{meu_ip}{Cores.RESET}")
    print("O script usará este IP para simular um acesso externo.")
    # ----------------------------------

    teste_null_session(meu_ip)
    teste_vulnerabilidade_smb()
    teste_enum4linux()
    teste_portas_nmap(meu_ip)
    
    print("\n" + "="*70)
    input("Pressione Enter para finalizar...")

if __name__ == "__main__":
    main()
