# 📋 Minhas Contas

Aplicativo leve de área de trabalho para controle de vencimento de contas, desenvolvido com interface acessível para a terceira idade (letras grandes, cores intuitivas e foco em tranquilidade).

---

## 🚀 Guia de Instalação no Computador Novo (Passo a Passo)

Siga este roteiro no laptop (leva cerca de 5 minutos).

---

### Passo 1: Instalar o Python

1. Abra o navegador no laptop e acesse: [python.org/downloads](https://www.python.org/downloads/)
2. Clique no botão amarelo **"Download Python 3.x.x"**.
3. Abra o instalador baixado.
4. ⚠️ **MUITO IMPORTANTE NA PRIMEIRA TELA:**
   * Marque a caixinha: **☑️ "Add python.exe to PATH"** (na parte inferior da janela).
   * Depois clique em **Install Now**.
5. Aguarde finalizar e clique em **Close**.
6. Execute pip install pystray pillow

---

### Passo 2: Baixar o Programa do GitHub

*(Como o computador dele não tem Git instalado, o método mais rápido é baixar o arquivo compactado)*

1. Acesse o link deste repositório no GitHub.
2. Clique no botão verde **`<> Code`** e depois em **`Download ZIP`**.
3. Abra a pasta de *Downloads* do computador dele.
4. Clique com o botão direito no arquivo `.zip` baixado ➔ **Extrair Tudo...**.
5. Copie a pasta extraída para um local permanente e seguro, por exemplo:
   * `C:\Programas\MinhasContas\`  
   *(ou dentro de `Documentos\MinhasContas\`)*

---

### Passo 3: Configurar o Programa (Sem Tela Preta de Terminal)

Para que seu pai nunca veja telas pretas de código ao usar o programa:

1. Abra a pasta onde o programa foi colocado.
2. Localize o arquivo `contas.py`.
3. Mude a extensão dele de `.py` para `.pyw` (ficando **`contas.pyw`**).
   > *Nota: No Windows, arquivos com terminação `.pyw` abrem direto a janela visual, ocultando o terminal automaticamente.*
   > *(Se o Windows não estiver mostrando a extensão `.py`, abra o Explorador de Arquivos ➔ menu **Exibir** ➔ marque a caixa **"Extensões de nomes de arquivos"**).*

---

### Passo 4: Criar o Atalho na Área de Trabalho

1. Clique com o **botão direito** sobre o arquivo **`contas.pyw`**.
2. Vá em **Enviar para** ➔ **Área de trabalho (criar atalho)**.
3. Vá até a Área de Trabalho dele:
   * Clique com o botão direito no novo atalho ➔ **Renomear**.
   * Dê o nome amigável: **`Minhas Contas`**.

---

### Passo 5: Inicialização Silenciosa

Como colocar na Inicialização Silenciosa do Windows:
1. Pressione Windows + R e digite shell:startup.
2. Crie um atalho para o arquivo contas.pyw nessa pasta.
3. Clique com o botão direito no atalho ➔ Propriedades.
4. No campo Destino, no final do texto, dê um espaço e escreva --silencioso.
    (Exemplo: C:\Programas\MinhasContas\contas.pyw --silencioso)

---

### Passo 6 (Opcional): Colocar um Ícone Amigável

Para facilitar a identificação visual:

1. Clique com o botão direito no atalho **Minhas Contas** na Área de Trabalho ➔ **Propriedades**.
2. Clique no botão **Alterar Ícone...**.
3. Você pode escolher um ícone padrão do Windows (como uma pastinha ou folha com visto) ou colocar um arquivo `.ico` de sua preferência.
4. Clique em **OK** e depois em **Aplicar**.



## 📁 Estrutura de Arquivos Criados Automaticamente

Na pasta do programa, os seguintes arquivos serão gerados pelo próprio aplicativo:

* `contas.pyw`: Código-fonte da aplicação.
* `contas.json`: Onde os nomes das contas e os pagamentos ficam salvos.
* `contas_backup.json`: Cópia de segurança gerada automaticamente a cada alteração para garantir que nada se perca.

---

## 💡 Dica Bônus: Abrir Sozinho ao Ligar o PC

Se você quiser que o programa abra sozinho toda vez que ele ligar o notebook:

1. Pressione as teclas `Windows + R` no teclado.
2. Digite `shell:startup` e aperte **Enter** (vai abrir a pasta de Inicialização do Windows).
3. Cole uma cópia do atalho **"Minhas Contas"** dentro dessa pasta.