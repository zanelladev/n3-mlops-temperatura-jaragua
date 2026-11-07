"""Etapa 5: eleição do vencedor do ciclo e regra de promoção contra o modelo vigente."""
import json

from src.ciclo import MANIFESTO


def eleger(candidatos, metrica, direcao):
    """candidatos = {papel: {metrica: valor}}. Em empate fica o primeiro (A, o mais simples)."""
    sinal = 1 if direcao == "minimizar" else -1
    return min(candidatos, key=lambda papel: sinal * candidatos[papel][metrica])


def decidir(desafiante, vigente, persistencia, cfg):
    """Devolve (promover, motivo). Os três valores são da métrica principal na mesma janela de validação."""
    limiar = cfg["promocao"]["limiar_melhoria"]
    sinal = 1 if cfg["avaliacao"]["direcao"] == "minimizar" else -1
    if cfg["promocao"]["exigir_bater_persistencia"] and sinal * desafiante >= sinal * persistencia:
        return False, "o desafiante não bate a persistência (amanhã = hoje)"
    if vigente is None:
        return True, "primeiro ciclo: ainda não havia modelo vigente"
    melhoria = sinal * (vigente - desafiante) / abs(vigente)
    if melhoria >= limiar:
        return True, f"melhora de {melhoria:.1%} sobre o vigente, acima do limiar de {limiar:.0%}"
    return False, f"melhora de {melhoria:.1%} sobre o vigente, abaixo do limiar de {limiar:.0%}"


def ler_manifesto():
    return json.loads(MANIFESTO.read_text(encoding="utf-8")) if MANIFESTO.exists() else None


def gravar_manifesto(manifesto):
    MANIFESTO.parent.mkdir(exist_ok=True)
    MANIFESTO.write_text(json.dumps(manifesto, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    cfg = {"promocao": {"limiar_melhoria": 0.02, "exigir_bater_persistencia": True},
           "avaliacao": {"direcao": "minimizar"}}
    assert decidir(1.8, None, 2.6, cfg)[0]          # primeiro ciclo promove
    assert not decidir(2.7, None, 2.6, cfg)[0]      # pior que a persistência, nunca
    assert decidir(1.70, 1.80, 2.6, cfg)[0]         # 5,6% melhor: promove
    assert not decidir(1.79, 1.80, 2.6, cfg)[0]     # 0,6% melhor: mantém
    assert eleger({"A": {"mae": 1.9}, "B": {"mae": 1.8}}, "mae", "minimizar") == "B"
    print("promoção ok")
