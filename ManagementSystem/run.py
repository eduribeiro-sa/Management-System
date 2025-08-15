from flask import Flask, redirect, render_template, request, url_for
import os
import sqlite3

app = Flask(__name__)

# Configuração para uploads (não utilizada neste código, mas deixada por consistência)
UPLOAD = 'static/assets'
app.config['UPLOAD'] = UPLOAD
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'assets')
app.config['dados_login'] = []

# Rota inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        conexao = sqlite3.connect('models/management-system.db')
        cursor = conexao.cursor()

        sql = "SELECT * FROM tb_login WHERE usuario=? AND senha=?"
        cursor.execute(sql, (usuario, senha))
        login_usuario = cursor.fetchone()
        app.config['dados_login'] = login_usuario
        conexao.close()

        if login_usuario:
            
            app.config['dados_login'] = {
                "usuario_id": login_usuario[0],
                "usuario": login_usuario[1],
                "nome_usuario": login_usuario[3],
                "imagem": login_usuario[4]
            }
            
            return redirect('/home')
        else:
            return redirect('/')

    return render_template('index.html')

# Página inicial do sistema
# Página inicial do sistema
@app.route('/home')
def home():
    # Recupera os dados do usuário logado
    user = app.config.get('dados_login')
    
    # Verifica se o usuário está logado
    if not user:  # Caso não esteja logado, redireciona para a página de login
        return redirect('/login')
    
    # Verifica se o campo de imagem existe no usuário
    if 'imagem' in user and user['imagem']:
        imagem = url_for('static', filename=user['imagem'])  # Caminho correto da imagem no diretório estático
    else:
        imagem = url_for('static', filename='assets/exemplo_usuario.png')  # Imagem padrão

    # Renderiza o template com as informações do usuário
    return render_template('home.html', user=user, imagem=imagem)



# Cadastro de usuários

@app.route('/cadastro_usuario', methods=['GET', 'POST'])
def cadastro_usuario():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        nome_usuario = request.form['nome_usuario']
        imagem = request.files.get('imagem')

        nome_imagem = None
        if imagem and imagem.filename:
            extensao = imagem.filename.split('.')[-1]
            nome_imagem = f"{nome_usuario.strip().lower().replace(' ', '_')}.{extensao}"
            caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER'], nome_imagem)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            imagem.save(caminho_imagem)
            nome_imagem = f"assets/{nome_imagem}"

        conexao = sqlite3.connect('models/management-system.db')
        cursor = conexao.cursor()

        sql = '''INSERT INTO tb_login (usuario, senha, nome_usuario, imagem) VALUES (?, ?, ?, ?)'''
        try:
            cursor.execute(sql, (usuario, senha, nome_usuario, nome_imagem))
            conexao.commit()
        except sqlite3.IntegrityError:
            return "Usuário já cadastrado!"
        finally:
            conexao.close()

        return redirect('/login')

    # Exemplo de passagem de dados fictícios para user
    user = {"nome_usuario": "Visitante"}  # Ou pegue do banco de dados
    return render_template('cadastro_usuario.html', user=user)



# Cadastro de clientes
@app.route('/cadastro_cliente', methods=['GET', 'POST'])
def cadastro_cliente():
    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        email_cliente = request.form['email_cliente']
        telefone_cliente = request.form['telefone_cliente']
        cpf_cliente = request.form['cpf_cliente']
        end_rua_cliente = request.form['end_rua_cliente']
        end_numero_cliente = request.form['end_numero_cliente']
        cidade_cliente = request.form['cidade_cliente']
        estado_cliente = request.form['estado_cliente']
        cep_cliente = request.form['cep_cliente']

        conexao = sqlite3.connect('models/management-system.db')
        cursor = conexao.cursor()
        sql = '''INSERT INTO tb_clientes (nome, email, telefone, cpf, endereco, numero, cidade, estado, cep) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        cursor.execute(sql, (nome_cliente, email_cliente, telefone_cliente, cpf_cliente, end_rua_cliente, end_numero_cliente, cidade_cliente, estado_cliente, cep_cliente))
        conexao.commit()
        conexao.close()

        return redirect('/consulta_cliente')

    return render_template('cadastro_clientes.html')

# Consulta de clientes
@app.route('/consulta_cliente')
def consulta_cliente():
    
    if not app.config['dados_login']:
        return redirect('/')

    conexao = sqlite3.connect('models/management-system.db')
    cursor = conexao.cursor()
    sql = 'SELECT * FROM tb_clientes'
    cursor.execute(sql)
    clientes = cursor.fetchall()
    conexao.close()

    return render_template('consulta_clientes.html', clientes=clientes)

# Editar cliente
@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    conexao = sqlite3.connect('models/management-system.db')
    cursor = conexao.cursor()

    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        email_cliente = request.form['email_cliente']
        telefone_cliente = request.form['telefone_cliente']
        cpf_cliente = request.form['cpf_cliente']
        end_rua_cliente = request.form['end_rua_cliente']
        end_numero_cliente = request.form['end_numero_cliente']
        cidade_cliente = request.form['cidade_cliente']
        estado_cliente = request.form['estado_cliente']
        cep_cliente = request.form['cep_cliente']

        sql = '''UPDATE tb_clientes 
                 SET nome=?, email=?, telefone=?, cpf=?, endereco=?, numero=?, cidade=?, estado=?, cep=? 
                 WHERE cliente_id=?'''
        cursor.execute(sql, (nome_cliente, email_cliente, telefone_cliente, cpf_cliente, end_rua_cliente, end_numero_cliente, cidade_cliente, estado_cliente, cep_cliente, id))
        conexao.commit()
        conexao.close()

        return redirect('/consulta_cliente')

    else:
        cursor.execute("SELECT * FROM tb_clientes WHERE cliente_id = ?", (id,))
        cliente = cursor.fetchone()
        conexao.close()

        return render_template('editar_clientes.html', cliente=cliente)

# Excluir cliente
@app.route('/excluir_cliente/<int:id>', methods=['GET'])
def excluir_cliente(id):
    conexao = sqlite3.connect('models/management-system.db')
    cursor = conexao.cursor()
    sql = 'DELETE FROM tb_clientes WHERE cliente_id = ?'
    cursor.execute(sql, (id,))
    conexao.commit()
    conexao.close()

    return redirect('/consulta_cliente')

@app.route('/ver_mais_cliente/<int:cliente_id>')
def ver_mais_cliente(cliente_id):
    # Verificar se o usuário está logado
    if not app.config['dados_login']:
        return redirect('/')

    # Conectar ao banco de dados
    conexao = sqlite3.connect('models/management-system.db')
    cursor = conexao.cursor()
    
    # Consultar os detalhes do cliente específico pelo ID
    sql = 'SELECT * FROM tb_clientes WHERE cliente_id = ?'
    cursor.execute(sql, (cliente_id,))
    cliente = cursor.fetchone()  # Busca um único cliente
    conexao.close()

    # Renderizar o template com os dados do cliente, ou retornar erro 404 se não encontrado
    if cliente:
        return render_template('ver-mais_clientes.html', cliente=cliente)
    else:
        return "Cliente não encontrado", 404


# Cadastro de fornecedores
@app.route('/cadastro_fornecedor', methods=['GET', 'POST'])
def cadastro_fornecedor():
    if request.method == 'POST':
        nome_fornecedor = request.form['nome_fornecedor']
        email_fornecedor = request.form['email_fornecedor']
        site_fornecedor = request.form['site_fornecedor']
        telefone_fornecedor = request.form['telefone_fornecedor']
        cnpj = request.form['cnpj']
        end_rua_fornecedor = request.form['end_rua_fornecedor']
        end_numero_fornecedor = request.form['end_numero_fornecedor']
        cidade_fornecedor = request.form['cidade_fornecedor']
        estado_fornecedor = request.form['estado_fornecedor']
        cep_fornecedor = request.form['cep_fornecedor']

        conexao = sqlite3.connect('models/management-system.db')
        cursor = conexao.cursor()
        sql = '''INSERT INTO tb_fornecedores (nome, email, site, telefone, cnpj, endereco, numero, cidade, estado, cep) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        cursor.execute(sql, (nome_fornecedor, email_fornecedor, site_fornecedor, telefone_fornecedor, cnpj, end_rua_fornecedor, end_numero_fornecedor, cidade_fornecedor, estado_fornecedor, cep_fornecedor))
        conexao.commit()
        conexao.close()

        return redirect('/consulta_fornecedor')

    return render_template('cadastro_fornecedor.html')

# Consulta de fornecedores
@app.route('/consulta_fornecedor')
def consulta_fornecedor():
    conexao = sqlite3.connect('models/management-system.db')
    cursor = conexao.cursor()
    sql = 'SELECT * FROM tb_fornecedores'
    cursor.execute(sql)
    fornecedores = cursor.fetchall()
    conexao.close()

    return render_template('consulta_fornecedor.html', fornecedores=fornecedores)

# Editar fornecedor
@app.route('/editar_fornecedor/<int:fornecedor_id>', methods=['GET', 'POST'])
def editar_fornecedor(fornecedor_id):
    conexao = sqlite3.connect('models/management-system.db')
    cursor = conexao.cursor()

    if request.method == 'POST':
        nome_fornecedor = request.form['nome_fornecedor']

        # Atualizando o registro no banco de dados
        sql = '''UPDATE tb_fornecedores 
                 SET nome = ? 
                 WHERE fornecedor_id = ?'''
        cursor.execute(sql, (nome_fornecedor, fornecedor_id))
        conexao.commit()
        conexao.close()

        return redirect('/consulta_fornecedor')

    # Buscando o registro atual do fornecedor
    sql = 'SELECT * FROM tb_fornecedores WHERE fornecedor_id = ?'
    cursor.execute(sql, (fornecedor_id,))
    fornecedor = cursor.fetchone()
    conexao.close()

    return render_template('editar_fornecedor.html', fornecedor=fornecedor)


# Excluir fornecedor
@app.route('/excluir_fornecedor/<int:fornecedor_id>', methods=['GET'])
def excluir_fornecedor(fornecedor_id):
    conexao = sqlite3.connect('models/management-system.db')
    cursor = conexao.cursor()

    # Usando a coluna correta no SQL
    sql = 'DELETE FROM tb_fornecedores WHERE fornecedor_id = ?'
    cursor.execute(sql, (fornecedor_id,))

    conexao.commit()
    conexao.close()

    return redirect('/consulta_fornecedor')

@app.route('/ver_mais_fornecedor/<int:fornecedor_id>')
def ver_mais_fornecedor(fornecedor_id):
    conexao = sqlite3.connect('models/management-system.db')
    cursor = conexao.cursor()
    sql = 'SELECT * FROM tb_fornecedores'
    cursor.execute(sql)
    fornecedores = cursor.fetchall()

    # Atualize a consulta com 'fornecedor_id'
    sql = 'SELECT * FROM tb_fornecedores WHERE fornecedor_id = ?'
    cursor.execute(sql, (fornecedor_id,))
    fornecedor = cursor.fetchone()
    conexao.close()

    if fornecedor:
        return render_template('ver-mais_fornecedor.html', fornecedor=fornecedor)
    else:
        return "Fornecedor não encontrado", 404



# Consulta de usuários
@app.route('/consulta_usuario')
def consulta_usuario():
    # Verifica se o usuário está logado
    if not app.config.get('dados_login'):  # Use .get() para evitar KeyError
        return redirect('/')

    # Conexão com o banco de dados para buscar os dados da tabela tb_login
    conexao = sqlite3.connect('models/management-system.db')
    cursor = conexao.cursor()

    try:
        # Consulta todos os usuários na tabela tb_login
        sql = 'SELECT usuario_id, nome_usuario, usuario, imagem FROM tb_login'
        cursor.execute(sql)
        usuarios = cursor.fetchall()  # Retorna os dados dos usuários
    except sqlite3.Error as e:
        print(f"Erro ao acessar o banco de dados: {e}")
        usuarios = []
    finally:
        conexao.close()

    # Renderiza o template com os dados dos usuários
    return render_template('consulta_usuario.html', usuarios=usuarios)

@app.route('/editar_usuario/<int:usuario_id>')
def editar_usuario(usuario_id):
    # Conectar ao banco de dados
    conexao = sqlite3.connect('models/management-system.db')
    cursor = conexao.cursor()

    try:
        # Consultar os dados do usuário pelo ID
        sql = 'SELECT usuario_id, nome_usuario, usuario, imagem FROM tb_login WHERE usuario_id = ?'
        cursor.execute(sql, (usuario_id,))
        usuario = cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Erro ao acessar o banco de dados: {e}")
        usuario = None
    finally:
        conexao.close()

    if not usuario:
        return "Usuário não encontrado", 404

    # Renderizar a página de edição com os dados do usuário
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/salvar_edicao_usuario/<int:usuario_id>', methods=['POST'])
def salvar_edicao_usuario(usuario_id):
    # Obter dados do formulário
    nome_usuario = request.form.get('nome_usuario')
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    imagem = request.files.get('imagem')

    # Diretório onde as imagens serão salvas
    diretorio_imagens = 'static/images/'

    # Garantir que o diretório existe
    os.makedirs(diretorio_imagens, exist_ok=True)

    # Conectar ao banco de dados
    conexao = sqlite3.connect('models/management-system.db')
    cursor = conexao.cursor()

    try:
        # Atualizar dados do usuário
        sql = 'UPDATE tb_login SET nome_usuario = ?, usuario = ?'
        params = [nome_usuario, usuario]

        if senha:
            sql += ', senha = ?'
            params.append(senha)

        if imagem and imagem.filename:
            # Salvar a nova imagem no diretório
            caminho_imagem = os.path.join(diretorio_imagens, imagem.filename)
            imagem.save(caminho_imagem)

            # Armazenar o caminho relativo no banco de dados
            caminho_imagem_relativo = f"images/{imagem.filename}"
            sql += ', imagem = ?'
            params.append(caminho_imagem_relativo)

        sql += ' WHERE usuario_id = ?'
        params.append(usuario_id)

        cursor.execute(sql, params)
        conexao.commit()
    except sqlite3.Error as e:
        print(f"Erro ao atualizar o banco de dados: {e}")
    finally:
        conexao.close()

    return redirect('/consulta_usuario')


# Excluir usuário
@app.route('/excluir_usuario/<int:usuario_id>')
def excluir_usuario(usuario_id):
    # Aqui você pode implementar a exclusão do banco de dados
    conexao = sqlite3.connect('models/management-system.db')
    cursor = conexao.cursor()
    try:
        cursor.execute('DELETE FROM tb_login WHERE usuario_id = ?', (usuario_id,))
        conexao.commit()
    except sqlite3.Error as e:
        print(f"Erro ao excluir usuário: {e}")
    finally:
        conexao.close()
    return redirect('/consulta_usuario')

# Executa a aplicação
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=80, debug=True)