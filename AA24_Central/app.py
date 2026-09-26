import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Base de dados de teste dos técnicos (Mapeamento dos cartões/fobs RFID)
TECNICOS_RFID = {
    "0008392104": {"nome": "Carlos Silva", "telemovel": "+351912345678", "veiculo": "Canter 01"},
    "0009123845": {"nome": "Miguel Rocha", "telemovel": "+351961234567", "veiculo": "Master 01"}
}

ocorrencias_pendentes = [
    {
        "id": 104,
        "cliente": "João Silva",
        "contacto": "912 345 678",
        "servico": "Reboque / Bateria",
        "local": "N125 km 90 (Faro)",
        "lat": 37.0194,
        "lng": -7.9304,
        "estado": "PENDENTE"
    }
]

@app.route('/')
def index():
    return render_template('index.html', ocorrencias=ocorrencias_pendentes)

@app.route('/processar_rfid', methods=['POST'])
def processar_rfid():
    data = request.json
    tag_rfid = data.get('rfid_tag', '').strip()
    modo = data.get('modo')
    id_servico = data.get('id_servico')

    tecnico = TECNICOS_RFID.get(tag_rfid)
    if not tecnico:
        return jsonify({"status": "error", "mensagem": "Cartão RFID Não Reconhecido!"}), 404

    if modo == 'PONTO':
        return jsonify({
            "status": "success",
            "mensagem": f"Ponto Registado: {tecnico['nome']} ({tecnico['veiculo']})"
        })

    elif modo == 'CHAMADO':
        servico = next((s for s in ocorrencias_pendentes if s["id"] == int(id_servico)), None)
        if not servico:
            return jsonify({"status": "error", "mensagem": "Serviço não encontrado!"}), 400

        maps_url = f"https://www.google.com/maps/dir/?api=1&destination={servico['lat']},{servico['lng']}&travelmode=driving"

        servico['estado'] = 'EM_TRANSITO'
        servico['tecnico'] = tecnico['nome']

        return jsonify({
            "status": "success", 
            "mensagem": f"Serviço #{servico['id']} atribuído a {tecnico['nome']}! Rota Maps: {maps_url}"
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
