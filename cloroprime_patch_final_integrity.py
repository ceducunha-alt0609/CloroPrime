from pathlib import Path
import re
p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Date-only values from <input type=date> must stay local, not UTC-shift to the previous day.
anchor="""function fmtBR(n, d=1) {
  return Number(n || 0).toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
}
"""
replacement=anchor+"""function parseLocalDate(value) {
  if(!value) return null;
  const m = String(value).match(/^(\\d{4})-(\\d{2})-(\\d{2})$/);
  if(!m) return new Date(value);
  return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
}
"""
assert anchor in s, 'fmt anchor not found'
s=s.replace(anchor,replacement,1)
s=s.replace('const ultima = new Date(troca);','const ultima = parseLocalDate(troca);',1)

# Configurable drum: don't leave hard-coded 100 L limits in the refill UI.
s=s.replace('<input type="number" id="ab-atual" placeholder="0" min="0" max="100" step="0.5" oninput="previewAbast()">','<input type="number" id="ab-atual" placeholder="0" min="0" step="0.5" oninput="previewAbast()">',1)
s=s.replace('<input type="number" id="ab-add" placeholder="Ex: 60" min="0" max="100" step="0.5" oninput="previewAbast()">','<input type="number" id="ab-add" placeholder="Ex: 60" min="0" step="0.5" oninput="previewAbast()">',1)
s=s.replace('<input type="number" id="nivel-manual" placeholder="Quanto tem agora?" min="0" max="100" step="0.5">','<input type="number" id="nivel-manual" placeholder="Quanto tem agora?" min="0" step="0.5">',1)

old_preview="""function previewAbast() {
  const atual = parseFloat(document.getElementById('ab-atual').value) || 0;
  const add = parseFloat(document.getElementById('ab-add').value) || 0;
  const total = Math.min(atual + add, state.config.tambor);
  const pct = Math.round((total / state.config.tambor) * 100);
"""
new_preview="""function previewAbast() {
  const atual = parseFloat(document.getElementById('ab-atual').value) || 0;
  const add = parseFloat(document.getElementById('ab-add').value) || 0;
  const capacidade = Number(state.config.tambor || 100);
  const total = Math.min(Math.max(0, atual + add), capacidade);
  const pct = capacidade > 0 ? Math.round((total / capacidade) * 100) : 0;
"""
assert old_preview in s, 'preview anchor not found'
s=s.replace(old_preview,new_preview,1)

old_reg="""  const atual = parseFloat(document.getElementById('ab-atual').value);
  const add = parseFloat(document.getElementById('ab-add').value);
  if(isNaN(atual) || isNaN(add) || add <= 0) { toast('Preencha o nível atual e o volume adicionado.','warn'); return; }
  const total = Math.min(atual + add, state.config.tambor);
"""
new_reg="""  const atual = parseFloat(document.getElementById('ab-atual').value);
  const add = parseFloat(document.getElementById('ab-add').value);
  const capacidade = Number(state.config.tambor || 100);
  if(!Number.isFinite(atual) || !Number.isFinite(add) || atual < 0 || add <= 0) { toast('Preencha o nível atual e o volume adicionado.','warn'); return; }
  if(atual > capacidade) { toast(`O nível atual não pode ultrapassar ${capacidade} L.`, 'warn'); return; }
  if(atual + add > capacidade) { toast(`O abastecimento ultrapassa a capacidade do tambor (${capacidade} L).`, 'warn'); return; }
  const total = atual + add;
"""
assert old_reg in s, 'register anchor not found'
s=s.replace(old_reg,new_reg,1)

# Cost must reflect concentrated product consumed, not every liter of diluted solution pumped.
old_cost="""  const custoPorL = preco / vol;
  const cfg = state.config;
  const bomba = parseFloat(cfg.bombaMax || 1.5);
  const consumoDia = getPumpFlowLH(cfg.fce, bomba) * 24;
  const custoDia = consumoDia * custoPorL;
  const custoMes = custoDia * 30;
  infoEl.textContent = `R$ ${custoPorL.toFixed(2)}/L · ~R$ ${custoDia.toFixed(2)}/dia · ~R$ ${custoMes.toFixed(2)}/mês`;
"""
new_cost="""  const custoPorL = preco / vol;
  const cfg = state.config;
  const bomba = parseFloat(cfg.bombaMax || 1.5);
  const consumoSolucaoDia = getPumpFlowLH(cfg.fce, bomba) * 24;
  const mix = getMixPlan(cfg.fce, cfg.hipoct);
  const fracaoProduto = Number(cfg.tambor || 0) > 0 ? Math.min(1, Math.max(0, mix.product / Number(cfg.tambor))) : 0;
  const consumoProdutoDia = consumoSolucaoDia * fracaoProduto;
  const custoDia = consumoProdutoDia * custoPorL;
  const custoMes = custoDia * 30;
  infoEl.textContent = `R$ ${custoPorL.toFixed(2)}/L de produto · ~${consumoProdutoDia.toFixed(2)} L produto/dia · ~R$ ${custoMes.toFixed(2)}/mês`;
"""
assert old_cost in s, 'cost info anchor not found'
s=s.replace(old_cost,new_cost,1)

old_chart="""  const bomba = parseFloat(cfg.bombaMax || 1.5);
  const consumoDia = getPumpFlowLH(cfg.fce, bomba) * 24;
  const custoPorL = preco > 0 && vol > 0 ? preco / vol : 0;
  const custoDia = consumoDia * custoPorL;
"""
new_chart="""  const bomba = parseFloat(cfg.bombaMax || 1.5);
  const consumoSolucaoDia = getPumpFlowLH(cfg.fce, bomba) * 24;
  const mix = getMixPlan(cfg.fce, cfg.hipoct);
  const fracaoProduto = Number(cfg.tambor || 0) > 0 ? Math.min(1, Math.max(0, mix.product / Number(cfg.tambor))) : 0;
  const consumoProdutoDia = consumoSolucaoDia * fracaoProduto;
  const custoPorL = preco > 0 && vol > 0 ? preco / vol : 0;
  const custoDia = consumoProdutoDia * custoPorL;
"""
assert old_chart in s, 'chart cost anchor not found'
s=s.replace(old_chart,new_chart,1)
s=s.replace("if(elSub) elSub.textContent = custoPorL > 0 ? `R$ ${custoPorL.toFixed(2)}/L · ${consumoDia.toFixed(2)} L/dia` : 'Configure preço em Config';","if(elSub) elSub.textContent = custoPorL > 0 ? `R$ ${custoPorL.toFixed(2)}/L produto · ${consumoProdutoDia.toFixed(2)} L produto/dia` : 'Configure preço em Config';",1)

# Reset only CloroPrime-owned keys, but make "TODOS os dados" true for this app.
old_reset="""function resetApp() {
  if(confirm('Isso apagará TODOS os dados. Confirma?')) {
    localStorage.removeItem(KEY);
    location.reload();
  }
}
"""
new_reset="""function resetApp() {
  if(confirm('Isso apagará TODOS os dados do CloroPrime neste navegador. Confirma?')) {
    localStorage.removeItem(KEY);
    localStorage.removeItem('cloroprime.sideGroups');
    localStorage.removeItem('cp_install_dismissed');
    location.reload();
  }
}
"""
assert old_reset in s, 'reset anchor not found'
s=s.replace(old_reset,new_reset,1)

p.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t,n=re.subn(r"const CACHE_VERSION = '[^']+';", "const CACHE_VERSION = 'cloroprime-bank-v1.3.0-final-integrity';", t, count=1)
assert n==1
sw.write_text(t,encoding='utf-8')

s=p.read_text(encoding='utf-8')
assert 'consumoProdutoDia' in s
assert 'parseLocalDate(troca)' in s
assert "localStorage.removeItem('cloroprime.sideGroups')" in s
assert 'O abastecimento ultrapassa a capacidade do tambor' in s
