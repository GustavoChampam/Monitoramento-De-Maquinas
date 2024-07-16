import time
import logging
import random
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SistemaAcompanhamento:
    def __init__(self, root):
        self.maquinas = {
            'I30': {'estado': True, 'problema': None, 'pecas_produzidas': 0, 'pecas_refugo': 0, 'historico_status': [], 'historico_refugo': []},
            'I40': {'estado': True, 'problema': None, 'pecas_produzidas': 0, 'pecas_refugo': 0, 'historico_status': [], 'historico_refugo': []},
            'I50': {'estado': True, 'problema': None, 'pecas_produzidas': 0, 'pecas_refugo': 0, 'historico_status': [], 'historico_refugo': []},
            'H20': {'estado': True, 'problema': None, 'pecas_produzidas': 0, 'pecas_refugo': 0, 'historico_status': [], 'historico_refugo': []}
        }
        self.estoque_pecas = 0
        self.pecas_refugo_total = 0
        self.possiveis_problemas = [
            'Motor falhou',
            'Falta de lubrificação',
            'Falha elétrica',
            'Superaquecimento'
        ]
        self.root = root
        self.labels = {}
        self.canvases = {}
        self.circles = {}
        self.botoes_consertar = {}

        self.setup_logging()
        self.setup_interface()
        self.root.after(1000, self.verificar_maquinas_e_atualizar)

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(), logging.FileHandler("sistema_acompanhamento.log")]
        )

    def verificar_maquinas(self):
        for maquina, status in self.maquinas.items():
            if not status['estado']:  # Se a máquina já está quebrada, continue
                status['historico_status'].append(0)
                continue

            # Gerar um problema aleatório com uma chance de 20%
            if random.random() < 0.2:  # 20% de chance de falha a cada verificação
                falha_ocorrida = True
                problema = random.choice(self.possiveis_problemas)
            else:
                falha_ocorrida = False
                problema = None

            if falha_ocorrida:
                status['estado'] = False
                status['problema'] = problema
                logging.info(f'{maquina} quebrou. Problema: {status["problema"]}')
                self.alertar_manutencao(maquina, status['problema'])
                status['historico_status'].append(0)
                # Adiciona uma peça ao refugo
                status['pecas_refugo'] += 1
                self.pecas_refugo_total += 1
                logging.info(f'Peça de refugo adicionada por {maquina}. Total de peças de refugo: {status["pecas_refugo"]}')
            else:
                # Incrementa o número de peças produzidas
                status['pecas_produzidas'] += 1
                self.estoque_pecas += 1
                logging.info(f'{maquina} produziu uma peça. Total produzidas: {status["pecas_produzidas"]}')
                status['historico_status'].append(1)
            
            # Adicionar a informação de refugo ao histórico
            status['historico_refugo'].append(status['pecas_refugo'])

    def alertar_manutencao(self, maquina, problema):
        logging.info(f'Alerta de manutenção: {maquina} - {problema}')
        messagebox.showwarning('Alerta de Manutenção', f'{maquina} quebrou. Problema: {problema}')

    def consertar_maquina(self, maquina):
        if self.maquinas[maquina]['estado'] == False:
            self.maquinas[maquina]['estado'] = True
            self.maquinas[maquina]['problema'] = None
            messagebox.showinfo('Máquina consertada', f'A máquina {maquina} foi consertada com sucesso!')
            logging.info(f'Máquina {maquina} foi consertada.')

    def atualizar_interface(self):
        for maquina, status in self.maquinas.items():
            label = self.labels[maquina]
            canvas = self.canvases[maquina]
            estado = 'Funcionando' if status['estado'] else f'Quebrado ({status["problema"]})'
            label.config(text=f'{maquina}: {estado} | Peças Produzidas: {status["pecas_produzidas"]} | Peças de Refugo: {status["pecas_refugo"]}')

            # Atualiza a cor da bolinha
            color = 'green' if status['estado'] else 'red'
            canvas.itemconfig(self.circles[maquina], fill=color)

        self.estoque_label.config(text=f'Estoque de Peças: {self.estoque_pecas}')
        self.refugo_label.config(text=f'Total de Peças de Refugo: {self.pecas_refugo_total}')
        self.atualizar_graficos()
        self.root.after(1000, self.verificar_maquinas_e_atualizar)  # Verifica a cada 1 segundo

    def verificar_maquinas_e_atualizar(self):
        self.verificar_maquinas()
        self.atualizar_interface()

    def atualizar_graficos(self):
        fig = Figure(figsize=(12, 6), dpi=100)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        
        ax1.set_title('Status das Máquinas ao Longo do Tempo')
        ax1.set_xlabel('Tempo')
        ax1.set_ylabel('Estado (1 = Funcionando, 0 = Quebrado)')
        
        ax2.set_title('Peças de Refugo ao Longo do Tempo')
        ax2.set_xlabel('Tempo')
        ax2.set_ylabel('Peças de Refugo')

        for maquina, status in self.maquinas.items():
            ax1.plot(status['historico_status'], label=maquina)
            ax2.plot(status['historico_refugo'], label=maquina)

        ax1.legend()
        ax2.legend()

        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self.graficos_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_interface(self):
        self.root.title("Sistema de Acompanhamento de Máquinas")

        # Estilo
        style = ttk.Style()
        style.configure("TFrame", padding=10)
        style.configure("TLabel", padding=5, font=('Helvetica', 12))
        style.configure("TButton", padding=5, font=('Helvetica', 12))
        style.configure("TCanvas", background='white')

        # Frame principal
        mainframe = ttk.Frame(self.root)
        mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Frame das máquinas
        maquinas_frame = ttk.Frame(mainframe, borderwidth=2, relief="sunken")
        maquinas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Labels, Canvas e Botões das máquinas
        for maquina in self.maquinas:
            frame = ttk.Frame(maquinas_frame)
            frame.pack(fill='x', pady=5)

            canvas = tk.Canvas(frame, width=20, height=20, background='white')
            canvas.pack(side='left', padx=5)
            circle = canvas.create_oval(2, 2, 18, 18, fill='green')

            label = ttk.Label(frame, text=f'{maquina}: Funcionando | Peças Produzidas: 0 | Peças de Refugo: 0')
            label.pack(side='left')

            # Botão para consertar a máquina
            botao = ttk.Button(frame, text=f'Consertar {maquina}', command=lambda m=maquina: self.consertar_maquina(m))
            botao.pack(side='left', padx=5)

            self.labels[maquina] = label
            self.canvases[maquina] = canvas
            self.circles[maquina] = circle
            self.botoes_consertar[maquina] = botao

        # Frame do estoque
        estoque_frame = ttk.Frame(mainframe, borderwidth=2, relief="sunken")
        estoque_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Label do estoque
        self.estoque_label = ttk.Label(estoque_frame, text=f'Estoque de Peças: {self.estoque_pecas}')
        self.estoque_label.pack()

        # Label do refugo
        self.refugo_label = ttk.Label(estoque_frame, text=f'Total de Peças de Refugo: {self.pecas_refugo_total}')
        self.refugo_label.pack()

        # Frame dos gráficos
        self.graficos_frame = ttk.Frame(mainframe, borderwidth=2, relief="sunken")
        self.graficos_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.atualizar_graficos()

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaAcompanhamento(root)
    root.mainloop()
