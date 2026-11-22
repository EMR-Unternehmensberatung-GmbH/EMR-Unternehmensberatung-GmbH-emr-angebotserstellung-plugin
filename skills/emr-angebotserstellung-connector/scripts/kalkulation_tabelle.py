#!/usr/bin/env python3
"""
Bearbeitbare Kalkulationstabelle (HTML) – zum Feinjustieren wie in Mendato.

Erzeugt aus angebot.json + firma.yaml eine Tabelle, in der Leistungswerte, Flächen/Mengen, Turnus,
Stunden, Material und Stundensatz direkt geändert werden können. Stunden und Preise rechnen sofort neu
(gleiche Formeln und Rundung wie kalkulation.py). Unten entsteht ein Änderungsblock, den der Nutzer in den
Chat kopiert; Claude übernimmt die Werte in angebot.json und rechnet verbindlich mit kalkulation.py.

Aufruf:
  python3 kalkulation_tabelle.py --angebot angebot.json --firma firma.yaml --out Kalkulation_<Kunde>.html
"""
import argparse
import json
import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import kalkulation as K  # noqa: E402
except ImportError:  # Connector-Paket: gerechnet wird auf dem EMR-Server
    import ausgabe as K  # noqa: E402


def turnus_liste(lade=None):
    t = (lade or K.lade_json)("turnus.json")
    wpm = float(t["wochen_pro_monat"])
    out = []
    for e in t["turnusse"]:
        f = e["pro_woche"] * wpm if "pro_woche" in e else e["pro_jahr"] / 12
        out.append({"id": e["id"], "label": e["label"], "faktor": round(f, 6)})
    return out


def daten_ur(angebot, erg, lade=None):
    lw = (lade or K.lade_json)("leistungswerte_unterhaltsreinigung.json")
    zeilen = []
    for p, z in zip(angebot.get("positionen") or [], erg["zeilen"]):
        zu = z.get("zuschlag") or {}
        direkt = z.get("leistungswert") is None
        zeilen.append({
            "bez": z["raum"], "raumtyp": z["raumtyp"] or ("Zeitansatz" if direkt else ""),
            "menge": z["flaeche"] if not direkt else None, "einheit": "m²",
            "turnus": z["turnus_id"], "lw": z["leistungswert"],
            "std_direkt": z.get("std_exakt", z["std_je_reinigung"]) if direkt else None,
            "faktor_ov": float(p["monatsfaktor"]) if p.get("monatsfaktor") is not None else None,
            "zs": zu.get("je_std"), "za": zu.get("anteil"),
            "std_lw": (lw["werte"].get(z["raumtyp"]) or {}).get(erg["objektart"]) if z["raumtyp"] else None,
            "tage": " ".join(z["tage"]), "begruendung": p.get("begruendung") or "",
        })
    return {"modus": "monatlich", "turnusse": turnus_liste(lade), "zeilen": zeilen, "fix": erg.get("material_monat") or 0}


def daten_hm(angebot, erg, lade=None):
    zeilen = []
    for p, z in zip(angebot.get("positionen") or [], erg["zeilen"]):
        zeilen.append({"bez": z["taetigkeit"], "raumtyp": "Tätigkeit", "menge": None, "einheit": "",
                       "turnus": z["turnus_id"], "lw": None, "std_direkt": z.get("std_exakt", z["std_je_einsatz"]), "faktor_ov": None,
                       "zs": None, "za": None, "std_lw": None, "tage": " ".join(z.get("tage") or []),
                       "begruendung": p.get("begruendung") or ""})
    return {"modus": "monatlich", "turnusse": turnus_liste(lade), "zeilen": zeilen}


def daten_einmal(angebot, erg):
    zeilen = []
    for p, z in zip(angebot.get("positionen") or [], erg["zeilen"]):
        direkt = p.get("stunden") is not None
        ep = p.get("einheitspreis")
        lz = z.get("lz") or {}
        menge = p.get("menge", p.get("flaeche"))
        zeilen.append({
            "bez": z["bezeichnung"] or "", "gruppe": z.get("gruppe") or "",
            "menge": None if direkt else menge,
            "einheit": lz.get("einheit") or p.get("einheit") or "m²",
            "lw": None if (direkt or ep is not None) else (lz.get("lw_exakt") or p.get("leistungswert")
                                                            or z.get("lw_exakt")),
            "std_lw": lz.get("lw_exakt") if lz and not p.get("leistungswert") else None,
            "stunden": float(p["stunden"]) if direkt else None,
            "ep": float(ep) if ep is not None else None,
            "bedarf": bool(p.get("bedarfsposition")),
            "material": float(p.get("material") or 0),
            "satz": float(p["stundensatz"]) if p.get("stundensatz") is not None else None,
            "begruendung": p.get("begruendung") or "",
        })
    zusatz = [{"bez": x["bezeichnung"], "preis": x["preis"]} for x in erg.get("zusatz", [])]
    return {"modus": "einmalig", "zeilen": zeilen, "zusatz": zusatz}


def daten_wd(angebot, erg):
    zeilen = [{"bez": z["bezeichnung"], "menge": z["flaeche"], "pm2": z["preis_je_m2"]} for z in erg["zeilen"]]
    return {"modus": "winterdienst", "zeilen": zeilen, "einsaetze": erg["einsaetze_pauschal"],
            "bereitschaft": erg["bereitschaftspauschale"], "zusatzp": erg["zusatzeinsatz_prozent"],
            "variante": erg["variante"]}


def farbe(firma, assets=None):
    p = str((firma.get("farben") or {}).get("primaer") or "").strip()
    if p.startswith("#") and len(p) == 7:
        return p
    logo = (firma.get("logos") or {}).get("eigenes")
    if logo and assets:
        try:
            import angebot_pdf as P
            pfad = next((x for x in [logo, os.path.join(assets, logo)] if os.path.exists(x)), None)
            hexw = P.farben_aus_logo(pfad) if pfad else None
            if hexw:
                c = P.lesbar_dunkel(P.HexColor(hexw))
                return "#%02X%02X%02X" % (int(c.red * 255), int(c.green * 255), int(c.blue * 255))
        except Exception:
            pass
    return "#1B2A4A"


HTML = r"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kalkulation – __TITEL__</title>
<style>
:root{--p:__FARBE__;--text:#1f2328;--muted:#4a4f57;--line:#d8dce3;--bg:#ffffff;--soft:#f4f6f9;--warn:#b54708;--warnbg:#fff4e5}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--text:#e8eaee;--muted:#b6bcc6;--line:#3a3f48;--bg:#16181c;--soft:#1f2329;--warnbg:#3a2a15;--warn:#f5b26b}}
:root[data-theme=dark]{--text:#e8eaee;--muted:#b6bcc6;--line:#3a3f48;--bg:#16181c;--soft:#1f2329;--warnbg:#3a2a15;--warn:#f5b26b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px/1.45 -apple-system,Segoe UI,Roboto,Arial,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:20px 16px 40px}
h1{font-size:20px;margin:0 0 2px;color:var(--p)}.sub{color:var(--muted);margin:0 0 16px}
.bar{display:flex;flex-wrap:wrap;gap:12px;align-items:end;margin:0 0 14px}
.bar label{font-size:12px;color:var(--muted);display:flex;flex-direction:column;gap:3px}
.tbl{overflow-x:auto;border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;min-width:860px}
th{background:var(--p);color:#fff;font-weight:600;font-size:12px;text-align:left;padding:8px 8px;white-space:nowrap}
td{border-top:1px solid var(--line);padding:5px 8px;vertical-align:middle}
tr.grp td{background:var(--soft);font-weight:600;color:var(--p)}
td.r,th.r{text-align:right}td.num{font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}
input,select{font:inherit;color:var(--text);background:var(--bg);border:1px solid var(--line);border-radius:5px;padding:4px 6px;width:100%}
input.n{width:84px;text-align:right}input.t{min-width:150px}select{min-width:150px}
input.chg,select.chg{border-color:var(--p);box-shadow:0 0 0 1px var(--p) inset;font-weight:600}
.std{font-size:11px;color:var(--muted);display:block}
tr.abw td{background:var(--warnbg)}.abwtxt{color:var(--warn);font-size:11px}
.sum{display:flex;flex-wrap:wrap;gap:12px;margin:16px 0}
.k{background:var(--soft);border-radius:8px;padding:12px 16px;min-width:170px}
.k b{display:block;font-size:22px;color:var(--p);font-variant-numeric:tabular-nums}.k span{font-size:12px;color:var(--muted)}
.k.main{background:var(--p);color:#fff}.k.main b,.k.main span{color:#fff}
.out h2{font-size:15px;margin:22px 0 6px}textarea{width:100%;min-height:150px;font:12.5px/1.45 ui-monospace,Menlo,Consolas,monospace;
color:var(--text);background:var(--soft);border:1px solid var(--line);border-radius:8px;padding:10px}
button{font:inherit;font-weight:600;background:var(--p);color:#fff;border:0;border-radius:6px;padding:9px 16px;cursor:pointer}
button.sec{background:transparent;color:var(--p);border:1px solid var(--p)}
.hint{font-size:12px;color:var(--muted)}
</style></head><body><div class="wrap">
<h1>Kalkulation – __TITEL__</h1>
<p class="sub">Werte direkt in der Tabelle ändern. Geänderte Felder sind hervorgehoben, Abweichungen über __GRENZE__ % vom Standard-Leistungswert gelb markiert. Verbindlich ist erst die Neuberechnung im Chat.</p>
<div class="bar" id="bar"></div>
<div class="tbl"><table id="t"></table></div>
<div class="sum" id="sum"></div>
<div class="out"><h2>Änderungen für den Chat</h2>
<p class="hint">Text kopieren und im Chat einfügen – Claude übernimmt die Werte und rechnet mit dem Kalkulationsskript neu.</p>
<textarea id="out" readonly></textarea>
<p><button id="copy">Änderungen kopieren</button> <button class="sec" id="reset">Zurücksetzen</button> <span class="hint" id="msg"></span></p></div>
</div>
<script>
const D=__DATEN__;
const START=JSON.parse(JSON.stringify(D));
const eur=v=>v.toLocaleString('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2})+' €';
const eur0=v=>v.toLocaleString('de-DE',{maximumFractionDigits:0})+' €';
const zahl=(v,n=2)=>v==null||isNaN(v)?'–':v.toLocaleString('de-DE',{minimumFractionDigits:n,maximumFractionDigits:n});
const rund=v=>Math.round((v+1e-9)*1)/1; // kaufmännisch auf volle Euro
const num=s=>{if(s===''||s==null)return null;let t=String(s).trim();if(t.includes(','))t=t.replace(/\./g,'').replace(',','.');else if(/^\d{1,3}(\.\d{3})+$/.test(t))t=t.replace(/\./g,'');const v=parseFloat(t);return isNaN(v)?null:v};
const fmtIn=v=>v==null?'':String(v).replace('.',',');
function bar(){const b=document.getElementById('bar');
 if(D.modus==='winterdienst'){b.innerHTML=`<label>Einsätze in der Pauschale<input class="n" id="eins" value="${fmtIn(D.einsaetze)}"></label><label>Bereitschaftspauschale €<input class="n" id="ber" value="${fmtIn(D.bereitschaft)}"></label><label>Weitere Einsätze % der Pauschale<input class="n" id="zp" value="${fmtIn(D.zusatzp)}"></label>`;
  document.getElementById('eins').oninput=e=>{D.einsaetze=num(e.target.value);calc()};document.getElementById('ber').oninput=e=>{D.bereitschaft=num(e.target.value);calc()};document.getElementById('zp').oninput=e=>{D.zusatzp=num(e.target.value);calc()};return}
 b.innerHTML=`<label>Stundensatz €/h<input class="n" id="satz" value="${fmtIn(D.satz)}"></label>`+
 (D.modus==='einmalig'&&D.projektgroesse?`<label>Projektgröße<input class="n" value="${D.projektgroesse}" disabled></label>`:'');
 document.getElementById('satz').oninput=e=>{D.satz=num(e.target.value);calc()}}
function zeileUR(z,i){const f=(D.turnusse.find(t=>t.id===z.turnus)||{}).faktor||0;
 const opts=D.turnusse.map(t=>`<option value="${t.id}" ${t.id===z.turnus?'selected':''}>${t.label}</option>`).join('');
 return `<tr data-i="${i}"><td><input class="t" data-k="bez" value="${z.bez.replace(/"/g,'&quot;')}"></td><td>${z.raumtyp}</td>
 <td>${z.std_direkt!=null?'<span class="std">–</span>':`<input class="n" data-k="menge" value="${fmtIn(z.menge)}">`}</td><td><select data-k="turnus">${opts}</select>${z.faktor_ov!=null?`<span class="std">Faktor ${zahl(z.faktor_ov,4)} (Vorgabe)</span>`:''}</td>
 <td><input class="n" data-k="tage" value="${z.tage}" style="width:140px;text-align:left"></td>
 <td>${z.std_direkt!=null?`<input class="n" data-k="std_direkt" value="${fmtIn(z.std_direkt)}"><span class="std">Std. je Einsatz</span>`:`<input class="n" data-k="lw" value="${fmtIn(z.lw)}"><span class="std">Standard ${z.std_lw??'–'}</span>`}${z.zs?`<span class="std">+ Zuschlag ${zahl(z.zs)} €/h auf ${zahl(z.za*100,0)} %</span>`:''}</td>
 <td class="num" data-o="std"></td><td class="num" data-o="preis"></td>
 <td><input class="t" data-k="begruendung" value="${(z.begruendung||'').replace(/"/g,'&quot;')}" placeholder="Grund bei Abweichung"></td></tr>`}
function zeileEM(z,i){return `<tr data-i="${i}"><td>${z.bedarf?'<span class="std">Bedarfsposition (nicht in Summe)</span>':''}<input class="t" data-k="bez" value="${z.bez.replace(/"/g,'&quot;')}"></td>
 <td><input class="n" data-k="menge" value="${fmtIn(z.menge)}"> <span class="std">${z.einheit}</span></td>
 ${z.ep!=null?`<td><input class="n" data-k="ep" value="${fmtIn(z.ep)}"><span class="std">Einheitspreis €/${z.einheit}</span></td><td></td>`:
 `<td><input class="n" data-k="lw" value="${fmtIn(z.lw)}"><span class="std">${z.std_lw!=null?'Standard '+zahl(z.std_lw):(z.einheit+'/h')}</span></td>
 <td><input class="n" data-k="stunden" value="${fmtIn(z.stunden)}" placeholder="auto"></td>`}
 <td><input class="n" data-k="material" value="${fmtIn(z.material)}"></td>
 <td class="num" data-o="std"></td><td class="num" data-o="preis"></td>
 <td><input class="t" data-k="begruendung" value="${(z.begruendung||'').replace(/"/g,'&quot;')}" placeholder="Grund bei Abweichung"></td></tr>`}
function zeileWD(z,i){return `<tr data-i="${i}"><td><input class="t" data-k="bez" value="${z.bez.replace(/"/g,'&quot;')}"></td>
 <td><input class="n" data-k="menge" value="${fmtIn(z.menge)}"> <span class="std">m²</span></td>
 <td><input class="n" data-k="pm2" value="${fmtIn(z.pm2)}"><span class="std">€/m² je Einsatz</span></td>
 <td class="num" data-o="std"></td><td class="num" data-o="preis"></td></tr>`}
function tabelle(){const t=document.getElementById('t');let h='';
 if(D.modus==='winterdienst'){h='<tr><th>Fläche</th><th class="r">Aufmaß</th><th class="r">Preis</th><th class="r"></th><th class="r">je Einsatz</th></tr>';D.zeilen.forEach((z,i)=>h+=zeileWD(z,i))}
 else if(D.modus==='monatlich'){h='<tr><th>Bereich</th><th>Raumtyp</th><th class="r">Fläche m²</th><th>Turnus</th><th>Tage</th><th class="r">Leistungswert m²/h</th><th class="r">Std./Monat</th><th class="r">€/Monat</th><th>Begründung</th></tr>';
  D.zeilen.forEach((z,i)=>h+=zeileUR(z,i))}
 else{h='<tr><th>Position</th><th class="r">Menge</th><th class="r">Leistungswert</th><th class="r">Stunden direkt</th><th class="r">Material €</th><th class="r">Stunden</th><th class="r">Preis</th><th>Begründung</th></tr>';
  let g=null;D.zeilen.forEach((z,i)=>{if(z.gruppe&&z.gruppe!==g){g=z.gruppe;h+=`<tr class="grp"><td colspan="8">${g}</td></tr>`}h+=zeileEM(z,i)});
  (D.zusatz||[]).forEach(z=>h+=`<tr><td>${z.bez}</td><td colspan="5"></td><td class="num">${eur(z.preis)}</td><td></td></tr>`)}
 t.innerHTML=h;
 t.querySelectorAll('input,select').forEach(el=>el.addEventListener('input',e=>{const tr=e.target.closest('tr');const z=D.zeilen[+tr.dataset.i];const k=e.target.dataset.k;
  z[k]=(k==='bez'||k==='turnus'||k==='tage'||k==='begruendung')?e.target.value:num(e.target.value);calc()}))}
function calcWD(){let je=0;const t=document.getElementById('t');
 D.zeilen.forEach((z,i)=>{const tr=t.querySelector(`tr[data-i="${i}"]`);const p=rund((z.menge||0)*(z.pm2||0));je+=p;
  tr.querySelector('[data-o=std]').textContent='';tr.querySelector('[data-o=preis]').textContent=eur(p);
  const s=START.zeilen[i];tr.querySelectorAll('[data-k]').forEach(el=>{const k=el.dataset.k;el.classList.toggle('chg',String(z[k]??'')!==String(s[k]??''))})});
 const saison=je*(D.einsaetze||0);const ges=(D.variante==='saison'?saison:0)+rund(D.bereitschaft||0);
 document.getElementById('sum').innerHTML=`<div class="k main"><span>${D.variante==='saison'?'Saison gesamt':'Bereitschaft'}</span><b>${eur0(ges)}</b></div><div class="k"><span>Preis je Einsatz</span><b>${eur0(je)}</b></div><div class="k"><span>Weiterer Einsatz</span><b>${eur0(D.variante==='saison'?rund(saison*(D.zusatzp||0)/100):je)}</b></div><div class="k"><span>Ursprünglich</span><b>${eur0(D.preis_start)}</b></div>`;aenderungen()}
function calc(){if(D.modus==='winterdienst')return calcWD();let sumStd=0,sumPreis=0,sumFl=0;const t=document.getElementById('t');
 D.zeilen.forEach((z,i)=>{const tr=t.querySelector(`tr[data-i="${i}"]`);const satz=(z.satz??D.satz)||0;let std=0,preis=0;
  if(D.modus==='monatlich'){const f=z.faktor_ov??((D.turnusse.find(x=>x.id===z.turnus)||{}).faktor||0);
   std=z.std_direkt!=null?z.std_direkt*f:((z.menge&&z.lw)?z.menge*f/z.lw:0);preis=std*satz+(z.zs?std*(z.za||0)*z.zs:0);if(f>0&&z.std_direkt==null)sumFl+=z.menge||0}
  else if(z.ep!=null){std=0;preis=rund((z.menge||0)*z.ep+(z.material||0));}
  else{std=z.stunden!=null?z.stunden:((z.menge&&z.lw)?z.menge/z.lw:0);preis=rund(std*satz+(z.material||0));}
  if(!z.bedarf){sumStd+=std;sumPreis+=preis;}
  tr.querySelector('[data-o=std]').textContent=zahl(std);tr.querySelector('[data-o=preis]').textContent=eur(preis);
  const abw=z.std_lw&&z.lw?Math.abs(z.lw-z.std_lw)/z.std_lw*100:0;tr.classList.toggle('abw',abw>D.grenze);
  const s=START.zeilen[i];tr.querySelectorAll('[data-k]').forEach(el=>{const k=el.dataset.k;el.classList.toggle('chg',String(z[k]??'')!==String(s[k]??''))})});
 const sumZ=(D.zusatz||[]).reduce((a,x)=>a+x.preis,0);let html='';
 if(D.modus==='monatlich'){const p=rund(sumPreis+(D.fix||0));
  html=`<div class="k main"><span>Monatliche Pauschale</span><b>${eur0(p)}</b></div><div class="k"><span>Stunden / Monat</span><b>${zahl(sumStd)}</b></div><div class="k"><span>Preis je m² / Monat</span><b>${sumFl?zahl(p/sumFl,3)+' €':'–'}</b></div><div class="k"><span>Ursprünglich</span><b>${eur0(D.preis_start)}</b></div>`}
 else{const p=sumPreis+sumZ;html=`<div class="k main"><span>Gesamt netto</span><b>${eur0(p)}</b></div><div class="k"><span>Stunden gesamt</span><b>${zahl(sumStd)}</b></div><div class="k"><span>Ursprünglich</span><b>${eur0(D.preis_start)}</b></div>`}
 document.getElementById('sum').innerHTML=html;aenderungen()}
function aenderungen(){const z=[];const fmt=v=>v==null?'leer':String(v).replace('.',',');
 if(D.satz!==START.satz)z.push(`- Stundensatz: ${fmt(START.satz)} → ${fmt(D.satz)} €/h`);
 [['einsaetze','Einsätze in der Saisonpauschale'],['bereitschaft','Bereitschaftspauschale'],['zusatzp','Weitere Einsätze %']].forEach(([k,l])=>{if(k in D&&D[k]!==START[k])z.push(`- ${l}: ${fmt(START[k])} → ${fmt(D[k])}`)});
 D.zeilen.forEach((r,i)=>{const s=START.zeilen[i];const n=[];
  const lab={bez:'Bezeichnung',menge:'Menge',turnus:'Turnus',tage:'Tage',lw:'Leistungswert',std_direkt:'Std. je Einsatz',stunden:'Stunden',ep:'Einheitspreis',pm2:'€/m² je Einsatz',material:'Material',begruendung:'Begründung'};
  Object.keys(lab).forEach(k=>{if(k in r&&String(r[k]??'')!==String(s[k]??''))n.push(`${lab[k]} ${fmt(s[k])} → ${fmt(r[k])}`)});
  if(n.length)z.push(`- Pos. ${i+1} „${s.bez}“: ${n.join('; ')}`)});
 const o=document.getElementById('out');
 o.value=z.length?`Kalkulation anpassen (aus der Tabelle):\n${z.join('\n')}\nBitte übernehmen und mit dem Kalkulationsskript neu rechnen.`:'Noch keine Änderungen.'}
document.getElementById('copy').onclick=async()=>{const o=document.getElementById('out');const m=document.getElementById('msg');
 try{await navigator.clipboard.writeText(o.value);m.textContent='Kopiert.'}catch(e){o.select();m.textContent='Text markiert – mit Strg/Cmd+C kopieren.'}};
document.getElementById('reset').onclick=()=>{Object.assign(D,JSON.parse(JSON.stringify(START)));bar();tabelle();calc()};
bar();tabelle();calc();
</script></body></html>"""


def tabellen_daten(angebot, firma, erg, lade=None):
    """Daten der Tabelle. Läuft im Skill oder auf dem EMR-Server (dort mit lade aus Neon)."""
    la = erg["leistungsart"]
    if la == "hausmeisterservice" and not erg.get("zeilen"):
        raise K.KalkulationsFehler("Hausmeisterservice nur mit Monatsstunden – Änderung direkt im Chat nennen.")
    if la == "unterhaltsreinigung":
        d = daten_ur(angebot, erg, lade)
    elif la == "hausmeisterservice":
        d = daten_hm(angebot, erg, lade)
    elif la == "winterdienst":
        d = daten_wd(angebot, erg)
    else:
        d = daten_einmal(angebot, erg)
    d["satz"] = erg.get("stundensatz") or (d["zeilen"][0].get("satz") if d["zeilen"] else None)
    d["preis_start"] = erg.get("pauschale") if erg["abrechnung"] == "monatlich" else erg.get("gesamt")
    d["grenze"] = float((firma.get("pruefung") or {}).get("lw_abweichung_prozent", 20))
    d["projektgroesse"] = angebot.get("projektgroesse")
    return d


def erzeuge(angebot, firma, out, assets=None, paket=None):
    if paket is not None:
        erg = paket["ergebnis"]
        d = paket.get("tabelle")
        if d is None:
            raise K.KalkulationsFehler(paket.get("tabelle_fehler") or "Für diesen Auftrag gibt es keine Tabelle.")
    else:
        erg = K.berechne(angebot, firma)
        d = tabellen_daten(angebot, firma, erg)
    k = angebot.get("kunde") or {}
    titel = f"{erg['leistungsart'].capitalize()} · {k.get('firma', '')}"
    html = (HTML.replace("__DATEN__", json.dumps(d, ensure_ascii=False))
            .replace("__TITEL__", escape(titel)).replace("__FARBE__", farbe(firma, assets))
            .replace("__GRENZE__", str(int(d["grenze"]))))
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return erg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--angebot", required=True)
    ap.add_argument("--firma", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--assets", default=".", help="Ordner mit dem Logo (für die Farbe, wenn firma.yaml 'auto' hat)")
    ap.add_argument("--paket", help="Paket vom EMR-Server (Connector). Dann rechnet nicht dieses Skript.")
    a = ap.parse_args()
    with open(a.angebot, encoding="utf-8") as f:
        angebot = json.load(f)
    try:
        paket = None
        if a.paket:
            import ausgabe
            paket = ausgabe.lade_paket(a.paket)
        elif not hasattr(K, "berechne"):
            raise K.KalkulationsFehler("--paket fehlt: In diesem Skill rechnet der EMR-Server. Erst die Funktion "
                                       "kalkulation des Connectors aufrufen und ihr Feld \"paket\" als Datei speichern.")
        erzeuge(angebot, K.lade_firma(a.firma), a.out, a.assets, paket)
    except K.KalkulationsFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"Tabelle erstellt: {a.out}")


if __name__ == "__main__":
    main()
