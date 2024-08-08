import time
import logging
import random
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import winsound  

class SistemaAcompanhamento:
    def __init__(self, root):
        self.maquinas = {
            'I30': {'estado': True, 'problema': None, 'pecas_produzidas': 0, 'pecas_refugo': 0, 'historico_status': deque(maxlen=50), 'historico_refugo': deque(maxlen=50), 'material_por_peca': 2, 'tempo_reparo': 0},
            'I40': {'estado': True, 'problema': None, 'pecas_produzidas': 0, 'pecas_refugo': 0, 'historico_status': deque(maxlen=50), 'historico_refugo': deque(maxlen=50), 'material_por_peca': 3, 'tempo_reparo': 0},
            'I50': {'estado': True, 'problema': None, 'pecas_produzidas': 0, 'pecas_refugo': 0, 'historico_status': deque(maxlen=50), 'historico_refugo': deque(maxlen=50), 'material_por_peca': 4, 'tempo_reparo': 0},
            'H20': {'estado': True, 'problema': None, 'pecas_produzidas': 0, 'pecas_refugo': 0, 'historico_status': deque(maxlen=50), 'historico_refugo': deque(maxlen=50), 'material_por_peca': 5, 'tempo_reparo': 0}
        }
        self.estoque_pecas = 0
        self.pecas_refugo_total = 0
        self.estoque_material = 1000  # Estoque inicial de material
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
        self.barras_reparo = {}

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
            if not status['estado']:  # Se a máquina está quebrada
                status['historico_status'].append(0)
                status['tempo_reparo'] -= 1
                self.barras_reparo[maquina]['value'] = max(0, status['tempo_reparo'])
                if status['tempo_reparo'] <= 0:
                    self.consertar_maquina(maquina)
                continue

            # Gerar um problema aleatório com uma chance de 50%
            if random.random() < 0.5:  # 50% de chance de falha a cada verificação
                falha_ocorrida = True
                problema = random.choice(self.possiveis_problemas)
            else:
                falha_ocorrida = False
                problema = None

            if falha_ocorrida:
                status['estado'] = False
                status['problema'] = problema
                status['tempo_reparo'] = random.randint(5, 10)  # Tempo de reparo entre 5 a 10 ciclos de verificação
                logging.info(f'{maquina} quebrou. Problema: {status["problema"]}')
                self.alertar_manutencao(maquina, status['problema'])
                status['historico_status'].append(0)
                # Adiciona uma peça ao refugo
                status['pecas_refugo'] += 1
                self.pecas_refugo_total += 1
                logging.info(f'Peça de refugo adicionada por {maquina}. Total de peças de refugo: {status["pecas_refugo"]}')
            else:
                if self.estoque_material >= status['material_por_peca']:
                    # Incrementa o número de peças produzidas
                    status['pecas_produzidas'] += 1
                    self.estoque_pecas += 1
                    self.estoque_material -= status['material_por_peca']
                    logging.info(f'{maquina} produziu uma peça. Total produzidas: {status["pecas_produzidas"]}')
                    status['historico_status'].append(1)
                else:
                    logging.warning(f'{maquina} parou devido à falta de material.')
                    status['historico_status'].append(0)
                    self.notificar_estoque_baixo()
            
            # Adicionar a informação de refugo ao histórico
            status['historico_refugo'].append(status['pecas_refugo'])

    def alertar_manutencao(self, maquina, problema):
        logging.info(f'Alerta de manutenção: {maquina} - {problema}')
        self.mensagens_label.config(text=f'ALERTA: {maquina} quebrou. Problema: {problema}', foreground='red')
        winsound.Beep(1000, 500)  # Alerta sonoro

    def consertar_maquina(self, maquina):
        if self.maquinas[maquina]['estado'] == False:
            self.maquinas[maquina]['estado'] = True
            self.maquinas[maquina]['problema'] = None
            self.maquinas[maquina]['tempo_reparo'] = 0
            self.mensagens_label.config(text=f'A máquina {maquina} foi consertada com sucesso!', foreground='green')
            logging.info(f'Máquina {maquina} foi consertada.')
            self.barras_reparo[maquina]['value'] = 0
            winsound.Beep(500, 500)  # Som de conserto

    def recarregar_material(self):
        quantidade = self.quantidade_entry.get()
        try:
            quantidade = int(quantidade)
            if quantidade > 0:
                self.estoque_material += quantidade
                self.material_label.config(text=f'Estoque de Material: {self.estoque_material}')
                self.mensagens_label.config(text=f'Estoque de material recarregado em {quantidade} unidades.', foreground='blue')
                logging.info(f'Estoque de material recarregado em {quantidade} unidades.')
            else:
                self.mensagens_label.config(text='Erro: Quantidade deve ser maior que zero.', foreground='red')
        except ValueError:
            self.mensagens_label.config(text='Erro: Por favor, insira um número válido.', foreground='red')

    def notificar_estoque_baixo(self):
        if self.estoque_material < 50:
            self.mensagens_label.config(text=f'Atenção: Estoque de material baixo ({self.estoque_material}). Recarregue!', foreground='orange')
            logging.warning(f'Estoque de material baixo: {self.estoque_material}')
            winsound.Beep(750, 500)

    def exportar_relatorio(self):
        with open('relatorio_maquinas.txt', 'w') as file:
            file.write('Relatório de Acompanhamento de Máquinas\n')
            file.write('=' * 40 + '\n\n')
            for maquina, status in self.maquinas.items():
                file.write(f'Máquina: {maquina}\n')
                file.write(f'  Estado: {"Funcionando" if status["estado"] else "Quebrado"}\n')
                file.write(f'  Problema: {status["problema"]}\n')
                file.write(f'  Peças Produzidas: {status["pecas_produzidas"]}\n')
                file.write(f'  Peças de Refugo: {status["pecas_refugo"]}\n')
                file.write(f'  Material por Peça: {status["material_por_peca"]}\n')
                file.write('-' * 40 + '\n')

            file.write(f'Estoque de Peças: {self.estoque_pecas}\n')
            file.write(f'Total de Peças de Refugo: {self.pecas_refugo_total}\n')
            file.write(f'Estoque de Material: {self.estoque_material}\n')

        self.mensagens_label.config(text='Relatório exportado com sucesso!', foreground='green')
        logging.info('Relatório exportado com sucesso para "relatorio_maquinas.txt".')

    def mostrar_ajuda(self):
        help_text = (
            "Sistema de Acompanhamento de Máquinas\n\n"
            "1. O sistema monitora automaticamente o estado das máquinas.\n"
            "2. Se uma máquina quebrar, um alerta será exibido e um som será reproduzido.\n"
            "3. Você pode recarregar o estoque de material quando estiver baixo.\n"
            "4. As máquinas produzem peças e acumulam peças de refugo ao longo do tempo.\n"
            "5. O botão 'Exportar Relatório' gera um arquivo de texto com o status atual das máquinas e seus estados.\n"
            "6. Use o botão 'Recarregar' para adicionar mais material ao estoque.\n"
            "7. Fique atento aos alertas de manutenção e estoque baixo."
        )
        messagebox.showinfo("Ajuda - Sistema de Acompanhamento de Máquinas", help_text)

    def atualizar_interface(self):
        for maquina, status in self.maquinas.items():
            label = self.labels[maquina]
            canvas = self.canvases[maquina]
            estado = 'Funcionando' if status['estado'] else f'Quebrado ({status["problema"]})'
            label.config(text=f'{maquina}: {estado} | Peças Produzidas: {status["pecas_produzidas"]} | Peças de Refugo: {status["pecas_refugo"]} | Material por Peça: {status["material_por_peca"]}')

            # Atualiza a cor da bolinha
            color = 'green' if status['estado'] else 'red'
            canvas.itemconfig(self.circles[maquina], fill=color)

        self.estoque_label.config(text=f'Estoque de Peças: {self.estoque_pecas}')
        self.refugo_label.config(text=f'Total de Peças de Refugo: {self.pecas_refugo_total}')
        self.material_label.config(text=f'Estoque de Material: {self.estoque_material}')
        self.atualizar_graficos()
        self.root.after(1000, self.verificar_maquinas_e_atualizar)  # Verifica a cada 1 segundo

    def verificar_maquinas_e_atualizar(self):
        self.verificar_maquinas()
        self.atualizar_interface()

    def atualizar_graficos(self):
        fig = Figure(figsize=(12, 6), dpi=75)
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
        self.root.title("Sistema de Acompanhamento de Máquinas ZF")

        # Estilo
        style = ttk.Style()
        style.configure("TFrame", padding=10)
        style.configure("TLabel", padding=5, font=('Helvetica', 12))
        style.configure("TButton", padding=5)

        # Criação do Notebook
        notebook = ttk.Notebook(self.root)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Frame principal para o Notebook
        mainframe = ttk.Frame(notebook)
        notebook.add(mainframe, text="Controle de Máquinas")

        # Frame das máquinas
        maquinas_frame = ttk.Frame(mainframe, borderwidth=2, relief="sunken")
        maquinas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Labels e Canvas das máquinas
        for i, maquina in enumerate(self.maquinas):
            frame = ttk.Frame(maquinas_frame)
            frame.grid(row=i, column=0, pady=5, sticky=(tk.W, tk.E))

            canvas = tk.Canvas(frame, width=20, height=20, background='white')
            canvas.pack(side='left', padx=5)
            circle = canvas.create_oval(2, 2, 18, 18, fill='green')

            label = ttk.Label(frame, text=f'{maquina}: Funcionando | Peças Produzidas: 0 | Peças de Refugo: 0 | Material por Peça: {self.maquinas[maquina]["material_por_peca"]}')
            label.pack(side='left')

            self.labels[maquina] = label
            self.canvases[maquina] = canvas
            self.circles[maquina] = circle

            barra_reparo = ttk.Progressbar(frame, orient="horizontal", length=200, mode="determinate")
            barra_reparo.pack(side='left', padx=5)
            barra_reparo['maximum'] = 10
            self.barras_reparo[maquina] = barra_reparo

        # Frame do estoque
        estoque_frame = ttk.Frame(mainframe, borderwidth=2, relief="sunken")
        estoque_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Labels do estoque e refugo
        self.estoque_label = ttk.Label(estoque_frame, text=f'Estoque de Peças: {self.estoque_pecas}')
        self.estoque_label.pack()

        self.refugo_label = ttk.Label(estoque_frame, text=f'Total de Peças de Refugo: {self.pecas_refugo_total}')
        self.refugo_label.pack()

        self.material_label = ttk.Label(estoque_frame, text=f'Estoque de Material: {self.estoque_material}')
        self.material_label.pack()

        # Entrada para recarregar material
        recarregar_frame = ttk.Frame(estoque_frame)
        recarregar_frame.pack(pady=10)

        ttk.Label(recarregar_frame, text="Recarregar Material: ").pack(side='left')
        self.quantidade_entry = ttk.Entry(recarregar_frame, width=10)
        self.quantidade_entry.pack(side='left', padx=5)
        recarregar_button = ttk.Button(recarregar_frame, text="Recarregar", command=self.recarregar_material)
        recarregar_button.pack(side='left')

        # Botão para exportar relatório
        exportar_button = ttk.Button(estoque_frame, text="Exportar Relatório", command=self.exportar_relatorio)
        exportar_button.pack(side='left', padx=10)

        # Frame para mensagens
        mensagens_frame = ttk.Frame(mainframe, borderwidth=2, relief="sunken")
        mensagens_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        self.mensagens_label = ttk.Label(mensagens_frame, text='Sistema iniciado.')
        self.mensagens_label.pack()

        # Criação da aba para os gráficos
        graficos_tab = ttk.Frame(notebook)
        notebook.add(graficos_tab, text="Gráficos")

        # Frame dos gráficos
        self.graficos_frame = ttk.Frame(graficos_tab, borderwidth=2, relief="sunken")
        self.graficos_frame.pack(fill=tk.BOTH, expand=True)
        
        self.atualizar_graficos()

        # Botão de ajuda
        menu_bar = tk.Menu(self.root)
        ajuda_menu = tk.Menu(menu_bar, tearoff=0)
        ajuda_menu.add_command(label="Como usar", command=self.mostrar_ajuda)
        menu_bar.add_cascade(label="Ajuda", menu=ajuda_menu)
        self.root.config(menu=menu_bar)

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaAcompanhamento(root)
    root.mainloop()
