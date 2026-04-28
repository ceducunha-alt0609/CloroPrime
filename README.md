# CloroPrime — PWA Nível Banco Completo

Pacote pronto para subir no GitHub Pages.

## Arquivos principais
- `index.html` — seu arquivo integrado e preservado.
- `backup_original_CloroPrime.html` — cópia de segurança do arquivo enviado.
- `manifest.json` — instalação real PWA.
- `sw.js` — cache/offline/atualização.
- `service-worker.js` — compatibilidade com versões anteriores.
- `offline.html` — tela offline premium.
- `icons/` — pacote completo de ícones.

## Como subir no GitHub
1. Envie todos os arquivos para a raiz do repositório.
2. Ative GitHub Pages em Settings > Pages.
3. Abra o site por `https://...github.io/.../`.
4. No Chrome/Edge, aguarde alguns segundos e use o botão Instalar.

## Observação importante
PWA real não instala corretamente abrindo por `file://`. Precisa rodar por HTTPS, como GitHub Pages.
