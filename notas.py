import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import re

# Diretório onde as notas serão salvas
diretorio_notas = "notas_markdown"
os.makedirs(diretorio_notas, exist_ok=True)

# Função para carregar notas do diretório de arquivos Markdown
def carregar_notas():
    notas_carregadas = {}
    if os.path.exists(diretorio_notas):
        for nome_arquivo in os.listdir(diretorio_notas):
            if nome_arquivo.endswith(".md"):
                titulo = os.path.splitext(nome_arquivo)[0]
                with open(os.path.join(diretorio_notas, nome_arquivo), "r", encoding="utf-8") as f:
                    linhas = f.readlines()
                    categoria = linhas[0].strip()
                    conteudo = "".join(linhas[1:])
                notas_carregadas[titulo] = {"categoria": categoria, "conteudo": conteudo}
    return notas_carregadas

# Função para salvar uma nota em um arquivo Markdown
def salvar_nota(titulo, categoria, conteudo):
    nome_arquivo = os.path.join(diretorio_notas, f"{titulo}.md")
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(f"{categoria}\n{conteudo}")

# Função para excluir uma nota do diretório de arquivos Markdown
def excluir_arquivo_nota(titulo):
    nome_arquivo = os.path.join(diretorio_notas, f"{titulo}.md")
    if os.path.exists(nome_arquivo):
        os.remove(nome_arquivo)

# Função para validar o título da nota
def validar_titulo(titulo):
    if not titulo or re.search(r'[\/\\\:\*\?"<>\|]', titulo):
        return False
    return True

notas = carregar_notas()

def adicionar_nota():
    titulo = entry_titulo.get()
    categoria = entry_categoria.get()
    conteudo = entry_conteudo.get("1.0", tk.END).strip()
    if not validar_titulo(titulo):
        messagebox.showwarning("Aviso", "Título inválido. Não deve conter caracteres especiais.")
        return
    if titulo and categoria and conteudo:
        if titulo in notas:
            messagebox.showwarning("Aviso", "Já existe uma nota com este título.")
        else:
            notas[titulo] = {"categoria": categoria, "conteudo": conteudo}
            atualizar_lista_notas()
            entry_titulo.delete(0, tk.END)
            entry_categoria.delete(0, tk.END)
            entry_conteudo.delete("1.0", tk.END)
            salvar_nota(titulo, categoria, conteudo)
    else:
        messagebox.showwarning("Aviso", "Título, Categoria e Conteúdo são obrigatórios.")

def editar_nota():
    try:
        titulo_selecionado = listbox_notas.get(listbox_notas.curselection())
        nova_categoria = entry_categoria.get()
        novo_conteudo = entry_conteudo.get("1.0", tk.END).strip()
        if nova_categoria and novo_conteudo:
            notas[titulo_selecionado] = {"categoria": nova_categoria, "conteudo": novo_conteudo}
            entry_conteudo.delete("1.0", tk.END)
            salvar_nota(titulo_selecionado, nova_categoria, novo_conteudo)
        else:
            messagebox.showwarning("Aviso", "Categoria e Conteúdo são obrigatórios.")
    except tk.TclError:
        messagebox.showwarning("Aviso", "Nenhuma nota selecionada.")

def excluir_nota():
    try:
        titulo_selecionado = listbox_notas.get(listbox_notas.curselection())
        del notas[titulo_selecionado]
        excluir_arquivo_nota(titulo_selecionado)
        atualizar_lista_notas()
    except tk.TclError:
        messagebox.showwarning("Aviso", "Nenhuma nota selecionada.")

def buscar_nota():
    busca = entry_busca.get()
    resultados = [titulo for titulo in notas if busca.lower() in titulo.lower()]
    atualizar_lista_notas(resultados)

def buscar_por_categoria():
    busca_categoria = entry_busca_categoria.get()
    resultados = [titulo for titulo, dados in notas.items() if busca_categoria.lower() in dados["categoria"].lower()]
    atualizar_lista_notas(resultados)

def exportar_pdf():
    try:
        titulo_selecionado = listbox_notas.get(listbox_notas.curselection())
        categoria = notas[titulo_selecionado]["categoria"]
        conteudo = notas[titulo_selecionado]["conteudo"]
        
        arquivo_pdf = os.path.join(diretorio_notas, f"{titulo_selecionado}.pdf")
        c = canvas.Canvas(arquivo_pdf, pagesize=letter)
        largura, altura = letter

        c.drawString(100, altura - 100, f"Título: {titulo_selecionado}")
        y = altura - 120
        c.drawString(100, y, f"Categoria: {categoria}")
        y -= 20
        c.drawString(100, y, "Conteúdo:")
        y -= 20
        
        for linha in conteudo.split('\n'):
            if y < 50:  # Criar nova página se o conteúdo for muito longo
                c.showPage()
                y = altura - 50
            c.drawString(100, y, linha)
            y -= 20

        c.save()
        messagebox.showinfo("Sucesso", f"Nota exportada como {arquivo_pdf}")
    except tk.TclError:
        messagebox.showwarning("Aviso", "Nenhuma nota selecionada.")
    except PermissionError:
        messagebox.showerror("Erro", "Permissão negada para salvar o PDF.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao exportar PDF: {str(e)}")

def atualizar_lista_notas(novas_notas=None):
    listbox_notas.delete(0, tk.END)
    if novas_notas is None:
        novas_notas = [(titulo, dados["categoria"]) for titulo, dados in notas.items()]
    else:
        novas_notas = [(titulo, notas[titulo]["categoria"]) for titulo in novas_notas]
    
    for titulo, categoria in novas_notas:
        listbox_notas.insert(tk.END, f"{titulo:30} {categoria}")

def on_nota_select(event):
    try:
        item_selecionado = listbox_notas.get(listbox_notas.curselection())
        titulo_selecionado = item_selecionado.split()[0]
        entry_titulo.delete(0, tk.END)
        entry_titulo.insert(0, titulo_selecionado)
        entry_categoria.delete(0, tk.END)
        entry_categoria.insert(0, notas[titulo_selecionado]["categoria"])
        entry_conteudo.delete("1.0", tk.END)
        entry_conteudo.insert(tk.END, notas[titulo_selecionado]["conteudo"])
    except tk.TclError:
        pass

def aplicar_modo_claro():
    root.configure(bg='white')
    label_titulo.configure(bg='white', fg='black')
    entry_titulo.configure(bg='white', fg='black')
    label_categoria.configure(bg='white', fg='black')
    entry_categoria.configure(bg='white', fg='black')
    label_conteudo.configure(bg='white', fg='black')
    entry_conteudo.configure(bg='white', fg='black')
    listbox_notas.configure(bg='white', fg='black')
    btn_adicionar.configure(bg='lightgray', fg='black')
    btn_editar.configure(bg='lightgray', fg='black')
    btn_excluir.configure(bg='lightgray', fg='black')
    btn_buscar.configure(bg='lightgray', fg='black')
    btn_buscar_categoria.configure(bg='lightgray', fg='black')
    btn_exportar_pdf.configure(bg='lightgray', fg='black')
    entry_busca.configure(bg='white', fg='black')
    entry_busca_categoria.configure(bg='white', fg='black')

def aplicar_modo_escuro():
    root.configure(bg='#2e2e2e')
    label_titulo.configure(bg='#2e2e2e', fg='white')
    entry_titulo.configure(bg='#3c3c3c', fg='white')
    label_categoria.configure(bg='#2e2e2e', fg='white')
    entry_categoria.configure(bg='#3c3c3c', fg='white')
    label_conteudo.configure(bg='#2e2e2e', fg='white')
    entry_conteudo.configure(bg='#3c3c3c', fg='white')
    listbox_notas.configure(bg='#3c3c3c', fg='white')
    btn_adicionar.configure(bg='#4f4f4f', fg='white')
    btn_editar.configure(bg='#4f4f4f', fg='white')
    btn_excluir.configure(bg='#4f4f4f', fg='white')
    btn_buscar.configure(bg='#4f4f4f', fg='white')
    btn_buscar_categoria.configure(bg='#4f4f4f', fg='white')
    btn_exportar_pdf.configure(bg='#4f4f4f', fg='white')
    entry_busca.configure(bg='#3c3c3c', fg='white')
    entry_busca_categoria.configure(bg='#3c3c3c', fg='white')

def ativar_modo_claro():
    aplicar_modo_claro()
    btn_ativo_claro.configure(relief="sunken")
    btn_ativo_escuro.configure(relief="raised")

def ativar_modo_escuro():
    aplicar_modo_escuro()
    btn_ativo_claro.configure(relief="raised")
    btn_ativo_escuro.configure(relief="sunken")

# Tela Inicial
def tela_inicial():
    inicial = tk.Toplevel()
    inicial.title("Bem-vindo ao Zettelkasten")
    inicial.geometry("400x200")
    
    label_nome = tk.Label(inicial, text="Zettelkasten", font=("Helvetica", 24))
    label_nome.pack(pady=20)

    label_descricao = tk.Label(inicial, text="Gerenciador de Notas")
    label_descricao.pack(pady=10)

    btn_inicio = tk.Button(inicial, text="Começar", command=lambda: [inicial.destroy(), root.deiconify()])
    btn_inicio.pack(pady=20)

    inicial.protocol("WM_DELETE_WINDOW", lambda: [inicial.destroy(), root.deiconify()])
    inicial.grab_set()
    inicial.wait_window()

root = tk.Tk()
root.title("Zettelkasten")
root.geometry("800x600")
root.withdraw()  # Oculta a janela principal inicialmente

# Exibe a tela inicial
tela_inicial()

# Cria e configura a janela principal
label_titulo = tk.Label(root, text="Título")
label_titulo.grid(row=0, column=0, sticky="w")
entry_titulo = tk.Entry(root)
entry_titulo.grid(row=0, column=1, columnspan=3, sticky="ew")

label_categoria = tk.Label(root, text="Categoria")
label_categoria.grid(row=1, column=0, sticky="w")
entry_categoria = tk.Entry(root)
entry_categoria.grid(row=1, column=1, columnspan=3, sticky="ew")

label_conteudo = tk.Label(root, text="Conteúdo")
label_conteudo.grid(row=2, column=0, sticky="w")
entry_conteudo = scrolledtext.ScrolledText(root, width=80, height=15)
entry_conteudo.grid(row=2, column=1, columnspan=3, sticky="ew")

btn_adicionar = tk.Button(root, text="Adicionar Nota", command=adicionar_nota)
btn_adicionar.grid(row=3, column=1, sticky="ew")

btn_editar = tk.Button(root, text="Editar Nota", command=editar_nota)
btn_editar.grid(row=3, column=2, sticky="ew")

btn_excluir = tk.Button(root, text="Excluir Nota", command=excluir_nota)
btn_excluir.grid(row=3, column=3, sticky="ew")

tk.Label(root, text="Buscar Nota").grid(row=4, column=0, sticky="w")
entry_busca = tk.Entry(root)
entry_busca.grid(row=4, column=1, columnspan=2, sticky="ew")

btn_buscar = tk.Button(root, text="Buscar", command=buscar_nota)
btn_buscar.grid(row=4, column=3, sticky="ew")

tk.Label(root, text="Buscar por Categoria").grid(row=5, column=0, sticky="w")
entry_busca_categoria = tk.Entry(root)
entry_busca_categoria.grid(row=5, column=1, columnspan=2, sticky="ew")

btn_buscar_categoria = tk.Button(root, text="Buscar Categoria", command=buscar_por_categoria)
btn_buscar_categoria.grid(row=5, column=3, sticky="ew")

listbox_notas = tk.Listbox(root, width=80, height=15, borderwidth=2, relief="sunken")
listbox_notas.grid(row=6, column=0, columnspan=4, sticky="nsew")
listbox_notas.bind("<<ListboxSelect>>", on_nota_select)

btn_exportar_pdf = tk.Button(root, text="Exportar PDF", command=exportar_pdf)
btn_exportar_pdf.grid(row=7, column=0, columnspan=4, sticky="ew")

btn_ativo_claro = tk.Button(root, text="Modo Claro", command=ativar_modo_claro)
btn_ativo_claro.grid(row=8, column=0, columnspan=2, sticky="ew")

btn_ativo_escuro = tk.Button(root, text="Modo Escuro", command=ativar_modo_escuro)
btn_ativo_escuro.grid(row=8, column=2, columnspan=2, sticky="ew")

# Configurar redimensionamento automático
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)

# Carregar notas ao iniciar o aplicativo
atualizar_lista_notas()

# Aplica o tema claro por padrão
ativar_modo_claro()

root.deiconify()  # Exibe a janela principal após a tela inicial
root.mainloop()