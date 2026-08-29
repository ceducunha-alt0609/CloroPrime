from pathlib import Path
import re
p=Path('index.html')
s=p.read_text(encoding='utf-8')
# Use one source of truth for collection-point bands.
old="""function getFitaBand(ponto) {
  if(ponto === 'principal') return { min: 0.3, max: 0.8, alvo: '0,3 a 0,8 mg/L' };
  if(ponto === 'secundario') return { min: 0.2, max: 0.6, alvo: '0,2 a 0,6 mg/L' };
  return { min: 0.2, max: 0.5, alvo: '0,2 a 0,5 mg/L' };
}
"""
new="""function getFitaBand(ponto) {
  return getOperationalTargets(ponto);
}
"""
assert old in s, 'fita band anchor not found'
s=s.replace(old,new,1)
# Preserve drum capacity in quick strip-adjustment calculation.
s=s.replace('calcMixLiters(alvo, vazao, produto, injReal))','calcMixLiters(alvo, vazao, produto, injReal, tambor))',1)
# Clarify that the top direct-concentration result is a pure-product theoretical reference,
# not the expected residual after dilution/distribution.
s=s.replace('<span class="result-label">Cloro ativo injetado</span>','<span class="result-label">Dose teórica com produto sem diluição</span>',1)
s=s.replace("const note = `Com ${conc}% de concentração, vazão de ${vazao} L/h e bomba ${fmtBR(maxFlowLH,1)} L/h @100%`;","const note = `Referência teórica sem diluir o produto no tambor · ${conc}% · vazão ${vazao} L/h · bomba ${fmtBR(maxFlowLH,1)} L/h @100%`;",1)
# Replace safety-style interpretation of the pure-stock theoretical number with an explanatory note.
old_alert="""  // Alertas na calculadora
  const da = document.getElementById('dose-alerta');
  da.style.display = 'block';
  da.innerHTML = '';
  if(cAtivo_mgL < 0.2) {
    da.innerHTML = '<div class="alert alert-danger">🚨 Abaixo do mínimo ANVISA (0,2 mg/L). Aumente o percentual do FCE.</div>';
  } else if(cAtivo_mgL < meta) {
    da.innerHTML = `<div class="alert alert-warn">⚠️ Abaixo da meta de ${meta} mg/L. Considere aumentar para atingir o objetivo.</div>`;
  } else if(cAtivo_mgL > 5) {
    da.innerHTML = '<div class="alert alert-danger">🚨 Supercloramento! Acima de 5 mg/L é prejudicial à saúde. Reduza o FCE.</div>';
  } else {
    da.innerHTML = `<div class="alert alert-info">✅ Dosagem adequada (${cAtivo_mgL.toFixed(2)} mg/L). Confirme com medição real.</div>`;
  }
"""
new_alert="""  // Este valor usa a concentração do produto puro e serve apenas como referência dimensional.
  // A operação real usa produto diluído no tambor e deve ser ajustada pela mistura e pela leitura de campo.
  const da = document.getElementById('dose-alerta');
  da.style.display = 'block';
  da.innerHTML = `<div class="alert alert-info">ℹ️ Referência teórica com produto sem diluição: ${cAtivo_mgL.toFixed(2)} mg/L. Para operação, use a mistura do tambor abaixo e confirme pela leitura real no ponto de coleta.</div>`;
"""
assert old_alert in s, 'calculator alert anchor not found'
s=s.replace(old_alert,new_alert,1)
p.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t,n=re.subn(r"const CACHE_VERSION = '[^']+';", "const CACHE_VERSION = 'cloroprime-bank-v1.2.0-consistency';", t, count=1)
assert n==1
sw.write_text(t,encoding='utf-8')

s=p.read_text(encoding='utf-8')
assert 'return getOperationalTargets(ponto);' in s
assert 'calcMixLiters(alvo, vazao, produto, injReal, tambor)' in s
assert 'Referência teórica com produto sem diluição' in s
