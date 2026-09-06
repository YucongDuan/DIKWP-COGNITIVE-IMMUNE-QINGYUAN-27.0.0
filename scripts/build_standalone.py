from pathlib import Path
root=Path(__file__).resolve().parents[1]
html=(root/'app/index.html').read_text(encoding='utf-8')
css=(root/'app/styles.css').read_text(encoding='utf-8')
rules=(root/'app/rules.js').read_text(encoding='utf-8')
app=(root/'app/app.js').read_text(encoding='utf-8')
html=html.replace('<link rel="stylesheet" href="styles.css">',f'<style>\n{css}\n</style>')
html=html.replace('<script src="rules.js"></script><script src="app.js"></script>',f'<script>\n{rules}\n</script><script>\n{app}\n</script>')
out=root/'release/QINGYUAN_Personal_Cognitive_Immunity_Client_27.0.0.html'
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(html,encoding='utf-8')
print(out)
