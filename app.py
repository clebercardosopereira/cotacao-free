from flask import Flask, render_template, request, jsonify, url_for, redirect
from uuid import uuid4
from datetime import datetime

app = Flask(__name__)

cotacoes = {}
ofertas = {}

@app.route('/')
def landing_page():
    return render_template('landing_page.html')

@app.route('/home')
def home():
    return render_template('index.html')



@app.route('/gerar_cotacao', methods=['POST'])
def gerar_cotacao():
    dados = request.json
    cotacao_id = str(uuid4())
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cotacoes[cotacao_id] = {
        'nome': dados['nome'],
        'itens': dados['itens'],
        'data_hora': data_hora
    }
    
    link_fornecedor = url_for('pagina_fornecedor', cotacao_id=cotacao_id, _external=False)
    link_acompanhamento = url_for('pagina_acompanhamento', cotacao_id=cotacao_id, _external=False)
    
    return jsonify({
        "link_fornecedor": link_fornecedor,
        "link_acompanhamento": link_acompanhamento
    })

@app.route('/fornecedor/<cotacao_id>')
def pagina_fornecedor(cotacao_id):
    if cotacao_id not in cotacoes:
        return "Cotação não encontrada", 404
    return render_template('fornecedor.html', cotacao_id=cotacao_id, cotacao=cotacoes[cotacao_id])

@app.route('/salvar_oferta/<cotacao_id>', methods=['POST'])
def salvar_oferta(cotacao_id):
    if cotacao_id not in cotacoes:
        return "Cotação não encontrada", 404
    
    dados = request.form
    fornecedor_id = str(uuid4())
    
    if cotacao_id not in ofertas:
        ofertas[cotacao_id] = {}
    
    ofertas[cotacao_id][fornecedor_id] = {
        'info': {
            'cpf_cnpj': dados['cpf_cnpj'],
            'nome_fantasia': dados['nome_fantasia'],
            'nome_vendedor': dados['nome_vendedor'],
            'contato_vendedor': dados.get('contato_vendedor', '')
        },
        'itens': {}
    }
    
    for item in cotacoes[cotacao_id]['itens']:
        item_nome = item['nome']
        nao_disponivel = f'nao_disponivel_{item_nome}' in dados
        preco = dados.get(f'preco_{item_nome}', '')
        if preco and not nao_disponivel:
            # Remove o 'R$ ' e converte para float
            preco = float(preco.replace('R$ ', '').replace('.', '').replace(',', '.'))
        ofertas[cotacao_id][fornecedor_id]['itens'][item_nome] = {
            'preco': preco if not nao_disponivel else 'Não disponível',
            'observacao': dados.get(f'obs_{item_nome}', ''),
            'disponivel': not nao_disponivel
        }
    
    return redirect(url_for('oferta_salva', cotacao_id=cotacao_id, fornecedor_id=fornecedor_id))

@app.route('/oferta_salva/<cotacao_id>/<fornecedor_id>')
def oferta_salva(cotacao_id, fornecedor_id):
    return render_template('oferta_salva.html', cotacao_id=cotacao_id, fornecedor_id=fornecedor_id)

@app.route('/acompanhamento/<cotacao_id>')
def pagina_acompanhamento(cotacao_id):
    if cotacao_id not in cotacoes:
        return "Cotação não encontrada", 404
    return render_template('acompanhamento.html', cotacao_id=cotacao_id, cotacao=cotacoes[cotacao_id], ofertas=ofertas.get(cotacao_id, {}))

@app.route('/atualizar_acompanhamento/<cotacao_id>')
def atualizar_acompanhamento(cotacao_id):
    if cotacao_id not in cotacoes:
        return jsonify({"error": "Cotação não encontrada"}), 404
    
    html = render_template('itens_acompanhamento.html', 
                           cotacao=cotacoes[cotacao_id], 
                           ofertas=ofertas.get(cotacao_id, {}))
    
    return jsonify({"html": html})


if __name__ == '__main__':
    app.run(debug=True)
