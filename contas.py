import calendar
import datetime
import json
import os
import socket
import sys
import threading
import tkinter as tk
from tkinter import messagebox
import winsound

# Bibliotecas de bandeja (Systray)
from PIL import Image, ImageDraw
import pystray

PORTA_SOCKET = 49234  # Porta local para garantir apenas uma instância aberta
PASTA_APP = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_DADOS = os.path.join(PASTA_APP, "contas.json")
ARQUIVO_BACKUP = os.path.join(PASTA_APP, "contas_backup.json")


def data_valida(ano, mes, dia):
    _, ultimo = calendar.monthrange(ano, mes)
    return datetime.date(ano, mes, min(dia, ultimo))


def gerar_icone_sistema():
    """Gera um ícone verde com símbolo amigável para a bandeja sem precisar de imagem externa."""
    img = Image.new("RGBA", (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((4, 4, 60, 60), fill="#27ae60")
    draw.rectangle((18, 28, 46, 36), fill="white")
    draw.rectangle((28, 18, 36, 46), fill="white")
    return img


class AppContas:

    def __init__(self, root):
        self.root = root
        self.root.title("Minhas Contas")
        self.root.geometry("700x780")
        self.root.minsize(600, 500)
        self.root.configure(bg="#f4f6f9")

        self.ultimo_alarme_disparado = None  # Evita popups repetidos no mesmo dia
        self.contas = self.carregar_contas()

        self.criar_cabecalho()
        self.criar_banner_resumo()
        self.criar_area_lista()

        # Intercepta o botão "X" para apenas esconder a janela
        self.root.protocol("WM_DELETE_WINDOW", self.esconder_janela)

        self.atualizar_lista()
        self.iniciar_bandeja_sistema()

        # Checagem em segundo plano a cada 15 minutos
        self.root.after(900000, self.monitoramento_automatico)

    def iniciar_bandeja_sistema(self):
        """Cria o ícone no Systray (perto do relógio)"""
        menu = pystray.Menu(
            pystray.MenuItem("Abrir Contas", lambda: self.mostrar_janela()),
            pystray.MenuItem("Fechar Totalmente", lambda: self.fechar_definitivo()),
        )
        self.tray_icon = pystray.Icon(
            "MinhasContas",
            gerar_icone_sistema(),
            "Minhas Contas",
            menu,
        )
        # Roda o ícone em uma thread separada para não travar a interface
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def esconder_janela(self):
        """Esconde a janela do programa e da barra de tarefas"""
        self.root.withdraw()

    def mostrar_janela(self):
        """Restaura a janela na frente de tudo com foco"""
        self.root.after(0, self._restaurar_interface)

    def _restaurar_interface(self):
        self.root.deiconify()
        self.root.state("normal")
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after_idle(self.root.attributes, "-topmost", False)
        self.root.focus_force()
        self.atualizar_lista()

    def fechar_definitivo(self):
        """Encerra o processo completamente"""
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()
        sys.exit(0)

    def monitoramento_automatico(self):
        """Roda a cada 15 min. Se virar o dia ou chegar no vencimento, abre a tela sozinho!"""
        self.atualizar_lista()
        self.verificar_acionamento_automatico()
        self.root.after(900000, self.monitoramento_automatico)

    def verificar_acionamento_automatico(self):
        hoje = datetime.date.today()
        # Se já avisou hoje, não fica abrindo e incomodando
        if self.ultimo_alarme_disparado == hoje:
            return

        urgentes = []
        for conta in self.contas:
            info = self.analisar_conta(conta)
            if info["tipo"] in ("hoje", "atrasado"):
                urgentes.append(conta["nome"])

        if urgentes:
            self.ultimo_alarme_disparado = hoje
            self.mostrar_janela()
            # Emite aviso sonoro suave do próprio Windows
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

    def carregar_contas(self):
        if os.path.exists(ARQUIVO_DADOS):
            try:
                with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                if os.path.exists(ARQUIVO_BACKUP):
                    try:
                        with open(ARQUIVO_BACKUP, "r", encoding="utf-8") as fb:
                            return json.load(fb)
                    except Exception:
                        return []
        return []

    def salvar_contas(self):
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(self.contas, f, ensure_ascii=False, indent=2)
        with open(ARQUIVO_BACKUP, "w", encoding="utf-8") as f:
            json.dump(self.contas, f, ensure_ascii=False, indent=2)

    def criar_cabecalho(self):
        frame_topo = tk.Frame(self.root, bg="#1a252f", padx=20, pady=12)
        frame_topo.pack(fill="x")

        self.lbl_data_topo = tk.Label(
            frame_topo, font=("Arial", 16, "bold"), fg="white", bg="#1a252f"
        )
        self.lbl_data_topo.pack(side="left")

        btn_add = tk.Button(
            frame_topo,
            text="➕ Nova Conta",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=12,
            pady=4,
            relief="raised",
            cursor="hand2",
            command=self.janela_adicionar_conta,
        )
        btn_add.pack(side="right")

    def criar_banner_resumo(self):
        self.frame_resumo = tk.Frame(self.root, padx=15, pady=10)
        self.frame_resumo.pack(fill="x")

        self.lbl_resumo = tk.Label(
            self.frame_resumo, font=("Arial", 14, "bold")
        )
        self.lbl_resumo.pack()

    def criar_area_lista(self):
        container = tk.Frame(self.root, bg="#f4f6f9")
        container.pack(fill="both", expand=True, padx=15, pady=5)

        self.canvas = tk.Canvas(container, bg="#f4f6f9", highlightthickness=0)
        scrollbar = tk.Scrollbar(
            container, orient="vertical", command=self.canvas.yview
        )

        self.frame_itens = tk.Frame(self.canvas, bg="#f4f6f9")
        self.frame_itens.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.frame_itens, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width),
        )
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def analisar_conta(self, conta):
        hoje = datetime.date.today()
        dia = int(conta.get("dia", 1))
        ultimo_pago = conta.get("ultimo_pago", "")

        chave_este_mes = f"{hoje.year}-{hoje.month:02d}"
        venc_este_mes = data_valida(hoje.year, hoje.month, dia)

        if hoje <= venc_este_mes:
            dias = (venc_este_mes - hoje).days
            if ultimo_pago == chave_este_mes:
                return {
                    "ordem": 4,
                    "bg": "#d4edda",
                    "fg": "#155724",
                    "borda": "#28a745",
                    "texto": f"✅ PAGO! (Vencimento dia {dia})",
                    "pago_agora": True,
                    "chave": chave_este_mes,
                    "tipo": "pago",
                }
            elif dias == 0:
                return {
                    "ordem": 1,
                    "bg": "#fff3cd",
                    "fg": "#856404",
                    "borda": "#e0a800",
                    "texto": "⚠️ VENCE HOJE! Não esqueça de pagar.",
                    "pago_agora": False,
                    "chave": chave_este_mes,
                    "tipo": "hoje",
                }
            elif dias <= 3:
                return {
                    "ordem": 2,
                    "bg": "#fff3cd",
                    "fg": "#856404",
                    "borda": "#ffc107",
                    "texto": f"⚠️ Vence em {dias} dia(s) (Dia {dia})",
                    "pago_agora": False,
                    "chave": chave_este_mes,
                    "tipo": "urgente",
                }
            else:
                return {
                    "ordem": 3,
                    "bg": "#ffffff",
                    "fg": "#2c3e50",
                    "borda": "#bdc3c7",
                    "texto": f"🗓️ Em dia — Vence dia {dia} (faltam {dias} dias)",
                    "pago_agora": False,
                    "chave": chave_este_mes,
                    "tipo": "futuro",
                }
        else:
            if ultimo_pago == chave_este_mes:
                mes_prox = 1 if hoje.month == 12 else hoje.month + 1
                ano_prox = hoje.year + 1 if hoje.month == 12 else hoje.year
                venc_prox = data_valida(ano_prox, mes_prox, dia)
                dias_prox = (venc_prox - hoje).days
                return {
                    "ordem": 5,
                    "bg": "#e8f5e9",
                    "fg": "#2e7d32",
                    "borda": "#a5d6a7",
                    "texto": f"✅ Em dia! Próximo vencimento: {venc_prox.strftime('%d/%m')} ({dias_prox} dias)",
                    "pago_agora": True,
                    "chave": chave_este_mes,
                    "tipo": "pago",
                }
            else:
                dias_atraso = (hoje - venc_este_mes).days
                return {
                    "ordem": 0,
                    "bg": "#f8d7da",
                    "fg": "#721c24",
                    "borda": "#dc3545",
                    "texto": f"🚨 ATRASADO! Venceu há {dias_atraso} dia(s) (Dia {dia})",
                    "pago_agora": False,
                    "chave": chave_este_mes,
                    "tipo": "atrasado",
                }

    def atualizar_lista(self):
        hoje = datetime.date.today()
        self.lbl_data_topo.config(
            text=f"📋 Minhas Contas  ({hoje.strftime('%d/%m/%Y')})"
        )

        for widget in self.frame_itens.winfo_children():
            widget.destroy()

        if not self.contas:
            self.frame_resumo.config(bg="#f4f6f9")
            self.lbl_resumo.config(
                text="Nenhuma conta cadastrada.", fg="#7f8c8d", bg="#f4f6f9"
            )
            return

        itens_processados = []
        atrasadas = 0
        vencendo_hoje = 0

        for idx, conta in enumerate(self.contas):
            info = self.analisar_conta(conta)
            itens_processados.append((info["ordem"], idx, conta, info))
            if info["tipo"] == "atrasado":
                atrasadas += 1
            elif info["tipo"] == "hoje":
                vencendo_hoje += 1

        if atrasadas > 0:
            self.frame_resumo.config(bg="#f8d7da")
            self.lbl_resumo.config(
                text=f"🚨 ATENÇÃO: Há {atrasadas} conta(s) atrasada(s)!",
                fg="#721c24",
                bg="#f8d7da",
            )
        elif vencendo_hoje > 0:
            self.frame_resumo.config(bg="#fff3cd")
            self.lbl_resumo.config(
                text=f"⚠️ ATENÇÃO: Você tem {vencendo_hoje} conta(s) vencendo HOJE!",
                fg="#856404",
                bg="#fff3cd",
            )
        else:
            self.frame_resumo.config(bg="#d4edda")
            self.lbl_resumo.config(
                text="🎉 Tudo certo por hoje! Nenhuma conta urgente pendente.",
                fg="#155724",
                bg="#d4edda",
            )

        itens_processados.sort(key=lambda x: x[0])

        for _, idx_original, conta, info in itens_processados:
            card = tk.Frame(
                self.frame_itens,
                bg=info["bg"],
                highlightbackground=info["borda"],
                highlightthickness=2,
                padx=15,
                pady=14,
            )
            card.pack(fill="x", pady=6, padx=5)

            info_frame = tk.Frame(card, bg=info["bg"])
            info_frame.pack(side="left", fill="both", expand=True)

            nome_label = tk.Label(
                info_frame,
                text=conta["nome"],
                font=("Arial", 17, "bold"),
                bg=info["bg"],
                fg=info["fg"],
                anchor="w",
            )
            nome_label.pack(fill="x")

            status_label = tk.Label(
                info_frame,
                text=info["texto"],
                font=("Arial", 13, "bold" if info["ordem"] <= 1 else "normal"),
                bg=info["bg"],
                fg=info["fg"],
                anchor="w",
            )
            status_label.pack(fill="x", pady=(3, 0))

            btn_frame = tk.Frame(card, bg=info["bg"])
            btn_frame.pack(side="right")

            if not info["pago_agora"]:
                btn_pago = tk.Button(
                    btn_frame,
                    text="✅ Marcar Pago",
                    font=("Arial", 13, "bold"),
                    bg="#28a745",
                    fg="white",
                    padx=10,
                    pady=5,
                    cursor="hand2",
                    command=lambda i=idx_original, ch=info[
                        "chave"
                    ]: self.alternar_pagamento(i, ch, marcar=True),
                )
            else:
                btn_pago = tk.Button(
                    btn_frame,
                    text="↩ Desfazer",
                    font=("Arial", 11),
                    bg="#6c757d",
                    fg="white",
                    padx=6,
                    pady=4,
                    command=lambda i=idx_original: self.alternar_pagamento(
                        i, "", marcar=False
                    ),
                )
            btn_pago.pack(side="left", padx=5)

            btn_del = tk.Button(
                btn_frame,
                text="🗑️",
                font=("Arial", 12),
                bg="#ffffff",
                fg="#dc3545",
                relief="groove",
                padx=6,
                pady=4,
                command=lambda i=idx_original: self.confirmar_exclusao(i),
            )
            btn_del.pack(side="left", padx=5)

    def alternar_pagamento(self, idx, chave, marcar):
        self.contas[idx]["ultimo_pago"] = chave if marcar else ""
        self.salvar_contas()
        self.atualizar_lista()

    def confirmar_exclusao(self, idx):
        nome = self.contas[idx]["nome"]
        resp = messagebox.askyesno(
            "Excluir Conta",
            f"Deseja realmente apagar a conta '{nome}'?",
            parent=self.root,
        )
        if resp:
            del self.contas[idx]
            self.salvar_contas()
            self.atualizar_lista()

    def janela_adicionar_conta(self):
        janela = tk.Toplevel(self.root)
        janela.title("Nova Conta")
        janela.geometry("380x280")
        janela.resizable(False, False)
        janela.grab_set()

        tk.Label(
            janela,
            text="Nome da Conta (ex: Luz, Água, Cartão):",
            font=("Arial", 12, "bold"),
            pady=8,
        ).pack()
        entry_nome = tk.Entry(
            janela, font=("Arial", 14), justify="center", width=22
        )
        entry_nome.pack(pady=5)
        entry_nome.focus_set()

        tk.Label(
            janela,
            text="Dia do Vencimento (1 a 31):",
            font=("Arial", 12, "bold"),
            pady=8,
        ).pack()
        entry_dia = tk.Entry(
            janela, font=("Arial", 14), justify="center", width=8
        )
        entry_dia.pack(pady=5)

        def salvar():
            nome = entry_nome.get().strip()
            dia_str = entry_dia.get().strip()

            if not nome:
                messagebox.showwarning(
                    "Atenção", "Digite o nome da conta!", parent=janela
                )
                return

            if not dia_str.isdigit() or not (1 <= int(dia_str) <= 31):
                messagebox.showwarning(
                    "Atenção", "O dia deve ser entre 1 e 31!", parent=janela
                )
                return

            self.contas.append(
                {"nome": nome, "dia": int(dia_str), "ultimo_pago": ""}
            )
            self.salvar_contas()
            self.atualizar_lista()
            janela.destroy()

        btn_salvar = tk.Button(
            janela,
            text="Salvar Conta",
            font=("Arial", 13, "bold"),
            bg="#27ae60",
            fg="white",
            padx=15,
            pady=6,
            command=salvar,
        )
        btn_salvar.pack(pady=15)


def escutar_segunda_instancia(app):
    """Fica escutando se o usuário clicou 2x no atalho na Área de Trabalho com o programa já aberto."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", PORTA_SOCKET))
        s.listen(2)
        while True:
            conn, _ = s.accept()
            msg = conn.recv(1024)
            if msg == b"SHOW":
                app.mostrar_janela()
            conn.close()
    except Exception:
        pass


if __name__ == "__main__":
    # Verificação de Instância Única via Socket
    s_teste = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s_teste.bind(("127.0.0.1", PORTA_SOCKET))
        s_teste.close()
    except OSError:
        # Programa já está aberto em segundo plano! Apenas pede para ele aparecer na tela
        try:
            s_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_cliente.connect(("127.0.0.1", PORTA_SOCKET))
            s_cliente.sendall(b"SHOW")
            s_cliente.close()
        except Exception:
            pass
        sys.exit(0)

    root = tk.Tk()
    app = AppContas(root)

    # Inicia a thread que recebe os cliques do atalho da Área de Trabalho
    threading.Thread(
        target=escutar_segunda_instancia, args=(app,), daemon=True
    ).start()

    # Se foi iniciado com o Windows (parâmetro --silencioso)
    if "--silencioso" in sys.argv:
        app.esconder_janela()
        app.verificar_acionamento_automatico()
    else:
        # Aberto normalmente pelo atalho
        app.verificar_acionamento_automatico()

    root.mainloop()