'''


'''

from logging import RootLogger
import tkinter as tk
from tkinter import messagebox
import json
import os


USUARIOS_FILE = "usuarios.json"
SERVICOS_FILE = "servicos.json"
AGENDAMENTOS_FILE = "agendamentos.json"


def carregar_dados(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


usuarios = carregar_dados(USUARIOS_FILE)
servicos = carregar_dados(SERVICOS_FILE)
agendamentos = carregar_dados(AGENDAMENTOS_FILE)

usuario_logado = None


def registrar_usuario(tipo, username, senha):
    if username in usuarios:
        messagebox.showerror("Erro", "Usuário já existe!")
    else:
        usuarios[username] = {"senha": senha, "tipo": tipo}
        salvar_dados(USUARIOS_FILE, usuarios)
        messagebox.showinfo("Sucesso", f"Usuário {username} registrado como {tipo}!")

def login(username, senha):
    global usuario_logado
    if username in usuarios and usuarios[username]["senha"] == senha:
        usuario_logado = {"username": username, "tipo": usuarios[username]["tipo"]}
        messagebox.showinfo("Login", f"Bem-vindo {username} ({usuarios[username]['tipo']})")
        abrir_menu()
    else:
        messagebox.showerror("Erro", "Usuário ou senha inválidos!")


def adicionar_servico(nome_servico):
    if usuario_logado and usuario_logado["tipo"] == "prestador":
        servicos[nome_servico] = {"prestador": usuario_logado["username"]}
        salvar_dados(SERVICOS_FILE, servicos)
        messagebox.showinfo("Sucesso", f"Serviço '{nome_servico}' adicionado!")
    else:
        messagebox.showerror("Erro", "Somente prestadores podem adicionar serviços!")

def remover_servico(nome_servico):
    if usuario_logado and usuario_logado["tipo"] == "prestador":
        if nome_servico in servicos and servicos[nome_servico]["prestador"] == usuario_logado["username"]:
            del servicos[nome_servico]
            salvar_dados(SERVICOS_FILE, servicos)
            messagebox.showinfo("Sucesso", f"Serviço '{nome_servico}' removido!")
        else:
            messagebox.showerror("Erro", "Você só pode remover seus próprios serviços!")
    else:
        messagebox.showerror("Erro", "Somente prestadores podem remover serviços!")

def agendar_servico(servico_nome, data_hora):
    if usuario_logado and usuario_logado["tipo"] == "cliente":
        if servico_nome not in servicos:
            messagebox.showerror("Erro", "Serviço não encontrado!")
            return
        novo_agendamento = {
            "cliente": usuario_logado["username"],
            "servico": servico_nome,
            "data_hora": data_hora
        }
        agendamentos_key = f"{usuario_logado['username']}_{servico_nome}_{data_hora}"
        agendamentos[agendamentos_key] = novo_agendamento
        salvar_dados(AGENDAMENTOS_FILE, agendamentos)
        messagebox.showinfo("Sucesso", f"Serviço '{servico_nome}' agendado para {data_hora}")
    else:
        messagebox.showerror("Erro", "Somente clientes podem agendar serviços!")

def cancelar_agendamento(chave):
    if usuario_logado and usuario_logado["tipo"] == "cliente":
        if chave in agendamentos and agendamentos[chave]["cliente"] == usuario_logado["username"]:
            del agendamentos[chave]
            salvar_dados(AGENDAMENTOS_FILE, agendamentos)
            messagebox.showinfo("Sucesso", "Agendamento cancelado!")
        else:
            messagebox.showerror("Erro", "Você só pode cancelar seus próprios agendamentos!")
    else:
        messagebox.showerror("Erro", "Somente clientes podem cancelar agendamentos!")


# Função para exportar todos os arquivos JSON
def exportar_arquivos_json():
    salvar_dados(USUARIOS_FILE, usuarios)
    salvar_dados(SERVICOS_FILE, servicos)
    salvar_dados(AGENDAMENTOS_FILE, agendamentos)
    messagebox.showinfo("Exportação", "Todos os dados foram exportados para JSON com sucesso!")



# Interface gráfica
root = tk.Tk()
root.title("Sistema de Agendamento")
root.geometry("430x580")
root.configure(bg="#3399ff")  # Azul mais claro

def abrir_login():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Login", font=("Arial", 18), fg="white", bg="#3399ff").pack(pady=10)
    tk.Label(root, text="Usuário:", fg="white", bg="#3399ff").pack()
    entry_user = tk.Entry(root)
    entry_user.pack()
    tk.Label(root, text="Senha:", fg="white", bg="#3399ff").pack()
    entry_pass = tk.Entry(root, show="*")
    entry_pass.pack()

    tk.Button(root, text="Entrar", command=lambda: login(entry_user.get(), entry_pass.get())).pack(pady=10)
    tk.Button(root, text="Registrar Cliente", command=lambda: registrar_usuario("cliente", entry_user.get(), entry_pass.get())).pack()
    tk.Button(root, text="Registrar Prestador", command=lambda: registrar_usuario("prestador", entry_user.get(), entry_pass.get())).pack()
    tk.Button(root, text="Exportar Arquivos JSON", command=exportar_arquivos_json).pack(pady=10)

def abrir_menu():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text=f"Menu - {usuario_logado['username']} ({usuario_logado['tipo']})", font=("Arial", 14), fg="white", bg="#3399ff").pack(pady=10)

    if usuario_logado["tipo"] == "prestador":
        tk.Label(root, text="Adicionar Serviço:", fg="white", bg="#3399ff").pack()
        entry_servico = tk.Entry(root)
        entry_servico.pack()
        tk.Button(root, text="Adicionar", command=lambda: adicionar_servico(entry_servico.get())).pack(pady=5)

        tk.Label(root, text="Remover Serviço:", fg="white", bg="#3399ff").pack()
        entry_remove = tk.Entry(root)
        entry_remove.pack()
        tk.Button(root, text="Remover", command=lambda: remover_servico(entry_remove.get())).pack(pady=5)

        tk.Label(root, text="Agendamentos dos seus serviços:", fg="white", bg="#3399ff").pack(pady=10)
        for chave, ag in agendamentos.items():
            if servicos.get(ag["servico"], {}).get("prestador") == usuario_logado["username"]:
                tk.Label(root, text=f"{ag['data_hora']} - {ag['servico']} (Cliente: {ag['cliente']})", fg="white", bg="#3399ff").pack()

    if usuario_logado["tipo"] == "cliente":
        tk.Label(root, text="Serviços disponíveis:", fg="white", bg="#3399ff").pack(pady=5)
        for nome, info in servicos.items():
            tk.Label(root, text=f"{nome} (Prestador: {info['prestador']})", fg="white", bg="#3399ff").pack()

        tk.Label(root, text="Agendar Serviço:", fg="white", bg="#3399ff").pack()
        entry_servico = tk.Entry(root)
        entry_servico.pack()
        tk.Label(root, text="Data e Hora (YYYY-MM-DD HH:MM):", fg="white", bg="#3399ff").pack()
        entry_data = tk.Entry(root)
        entry_data.pack()
        tk.Button(root, text="Agendar", command=lambda: agendar_servico(entry_servico.get(), entry_data.get())).pack(pady=5)

        tk.Label(root, text="Seus agendamentos:", fg="white", bg="#3399ff").pack(pady=10)
        for chave, ag in agendamentos.items():
            if ag["cliente"] == usuario_logado["username"]:
                tk.Label(root, text=f"{ag['data_hora']} - {ag['servico']} (Prestador: {servicos[ag['servico']]['prestador']})", fg="white", bg="#3399ff").pack()
                tk.Button(root, text="Cancelar", command=lambda c=chave: cancelar_agendamento(c)).pack()

    tk.Button(root, text="Sair", command=abrir_login).pack(pady=20)

abrir_login()
root.mainloop()