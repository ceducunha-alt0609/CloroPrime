from pathlib import Path
import re
p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="""const KEY = 'cloroprime_v1';
let state = {
  nivel: 50,
  hist: [],
  latestRead: { valor: '', ponto: 'ponta' },
  proximaVerif: null,
  custoTotal: 0,
  config: {
    reserv: 30000, reservSec: 9000, caixas: 8, volCaixa: 2000,
    unidades: 80, pessoas: 240, vazao: 1500,
    fce: 18, hipoct: 12, tambor: 100, bombaMax: 1.5,
    alvoDose: 1.0, alertaBaixo: 20, alertaCrit: 10,
    modeloBomba: '', filtroTroca: '', filtroIntervalo: 60,
    precoProduto: 0, volGalao: 20
  }
};

function load() {
  try { const d = JSON.parse(localStorage.getItem(KEY)); if(d) state = d; } catch(e){}
}
"""
new="""const KEY = 'cloroprime_v1';
const DEFAULT_STATE = {
  nivel: 50,
  hist: [],
  latestRead: { valor: '', ponto: 'ponta' },
  proximaVerif: null,
  custoTotal: 0,
  config: {
    reserv: 30000, reservSec: 9000, caixas: 8, volCaixa: 2000,
    unidades: 80, pessoas: 240, vazao: 1500,
    fce: 18, hipoct: 12, tambor: 100, bombaMax: 1.5,
    alvoDose: 1.0, alertaBaixo: 20, alertaCrit: 10,
    modeloBomba: '', filtroTroca: '', filtroIntervalo: 60,
    precoProduto: 0, volGalao: 20
  }
};
let state = JSON.parse(JSON.stringify(DEFAULT_STATE));

function normalizeState(d) {
  if(!d || typeof d !== 'object' || Array.isArray(d)) return JSON.parse(JSON.stringify(DEFAULT_STATE));
  return {
    ...JSON.parse(JSON.stringify(DEFAULT_STATE)),
    ...d,
    hist: Array.isArray(d.hist) ? d.hist : [],
    latestRead: { ...DEFAULT_STATE.latestRead, ...(d.latestRead && typeof d.latestRead === 'object' && !Array.isArray(d.latestRead) ? d.latestRead : {}) },
    config: { ...DEFAULT_STATE.config, ...(d.config && typeof d.config === 'object' && !Array.isArray(d.config) ? d.config : {}) }
  };
}
function load() {
  try { const d = JSON.parse(localStorage.getItem(KEY)); if(d) state = normalizeState(d); } catch(e){}
}
"""
assert old in s, 'state anchor not found'
s=s.replace(old,new,1)

old="""function calcMixLiters(targetMgL, waterLh, productPct, pumpLh) {
  if(!targetMgL || !waterLh || !productPct || !pumpLh) return 0;
  return (targetMgL * waterLh) / (100 * productPct * pumpLh);
}
"""
new="""function calcMixLiters(targetMgL, waterLh, productPct, pumpLh, drumL=100) {
  if(!targetMgL || !waterLh || !productPct || !pumpLh || !drumL) return 0;
  // mg/L × L/h = mg/h necessários. productPct% equivale a productPct×10.000 mg/L.
  // Escala a quantidade de produto para a capacidade real do tambor.
  return (targetMgL * waterLh * drumL) / (10000 * productPct * pumpLh);
}
"""
assert old in s, 'mix formula anchor not found'
s=s.replace(old,new,1)
s=s.replace('calcMixLiters(alvo, waterLh, productPct, Math.max(pumpLh, 0.001))','calcMixLiters(alvo, waterLh, productPct, Math.max(pumpLh, 0.001), cfg.tambor || 100)',1)
s=s.replace('const litrosProduto = calcMixLiters(alvo, vazao, pct, injReal);','const litrosProduto = calcMixLiters(alvo, vazao, pct, injReal, tambor);',1)
s=s.replace('Calcula quanto produto colocar no tambor de 100 L, com base na força do cloro, regulagem do FCE e dose alvo.','Calcula quanto produto colocar na capacidade configurada do tambor, com base na força do cloro, regulagem do FCE e dose alvo.',1)
s=s.replace('<span class="tag">Tambor 100 L</span>','<span class="tag">Tambor configurado</span>',1)
s=s.replace('Quanto tempo os 100 L devem render','Quanto tempo o tambor deve render',1)
s=s.replace("const aviso = litrosProduto > tambor ? ' ⚠️ forte demais p/ 100 L' : '';","const aviso = litrosProduto > tambor ? ' ⚠️ concentração insuficiente para esta regulagem/capacidade' : '';",1)

pattern=re.compile(r"      if\(!dados\.config \|\| !Array\.isArray\(dados\.hist\)\) \{\n        toast\('Arquivo inválido\. Selecione um backup gerado pelo CloroPrime\.', 'err', 5000\);\n        return;\n      \}\n      if\(!confirm\(`Importar backup de .*?\) return;\n      state = dados;", re.S)
replacement="""      if(!dados || typeof dados !== 'object' || Array.isArray(dados) ||
         !dados.config || typeof dados.config !== 'object' || Array.isArray(dados.config) ||
         !Array.isArray(dados.hist)) {
        toast('Arquivo inválido. Selecione um backup gerado pelo CloroPrime.', 'err', 5000);
        input.value = '';
        return;
      }
      if(!confirm(`Importar backup de ${dados.ultimoBackup ? new Date(dados.ultimoBackup).toLocaleString('pt-BR') : 'data desconhecida'}?\\n\\nISTO VAI SUBSTITUIR todos os dados atuais.`)) { input.value = ''; return; }
      state = normalizeState(dados);"""
s,n=pattern.subn(replacement,s,count=1)
assert n==1, 'backup import anchor not found'
p.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=t.replace("const CACHE_VERSION = 'cloroprime-bank-v1.0.0';","const CACHE_VERSION = 'cloroprime-bank-v1.1.0-audit-safety';",1)
old_sw="await Promise.all(keys.filter(k => ![STATIC_CACHE, RUNTIME_CACHE].includes(k)).map(k => caches.delete(k)));"
new_sw="await Promise.all(keys.filter(k => k.startsWith('cloroprime-') && ![STATIC_CACHE, RUNTIME_CACHE].includes(k)).map(k => caches.delete(k)));"
assert old_sw in t, 'sw cleanup anchor not found'
t=t.replace(old_sw,new_sw,1)
sw.write_text(t,encoding='utf-8')

s=p.read_text(encoding='utf-8')
assert 'const DEFAULT_STATE' in s
assert 'calcMixLiters(alvo, vazao, pct, injReal, tambor)' in s
assert 'state = normalizeState(dados);' in s
