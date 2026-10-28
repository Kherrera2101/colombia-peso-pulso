"""Láminas analíticas del corte 2015–2025."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter
from .io import read_frame

BG, PANEL, WHITE, MUTED = "#0B1320","#142238","#F0F3F5","#9BAFC2"
TEAL, GOLD, CORAL, GRID = "#4CE0B3","#F3C66B","#F28179","#2C3B4E"


def number(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}".replace(",","_").replace(".",",").replace("_",".")


def canvas(title: str, subtitle: str, page: int):
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"text.color":WHITE,"axes.labelcolor":MUTED,"xtick.color":MUTED,"ytick.color":MUTED,"axes.edgecolor":GRID,"svg.fonttype":"none"})
    fig = plt.figure(figsize=(19.2,10.8),dpi=100,facecolor=BG)
    fig.text(.035,.949,"PESO & PULSO",fontsize=28,fontweight="bold")
    fig.text(.035,.916,"COLOMBIA  /  TASA DE CAMBIO Y ECONOMÍA REAL",fontsize=10,color=TEAL,fontweight="bold")
    for i,label in enumerate(["01  Pulso macro","02  Dólar y precios","03  Sector externo"],1):
        fig.text(.55+(i-1)*.145,.948,label,fontsize=11,color=TEAL if i==page else MUTED,fontweight="bold" if i==page else "normal")
    fig.text(.035,.855,title,fontsize=24,fontweight="bold")
    fig.text(.035,.817,subtitle,fontsize=12,color=MUTED)
    fig.add_artist(plt.Line2D([.035,.965],[.895,.895],transform=fig.transFigure,color=GRID,linewidth=1))
    fig.text(.035,.028,"Fuentes: SFC · Portal de Datos Abiertos www.datos.gov.co | DANE · DIAN | EIA. Corte: 28 oct 2026.",fontsize=9,color=MUTED)
    fig.text(.965,.028,"2015–2025  ·  Referencia visual elaborada con Python",fontsize=9,color=MUTED,ha="right")
    return fig


def panel(fig,box,title,unit):
    ax = fig.add_axes(box,facecolor=PANEL)
    ax.set_title(title,loc="left",pad=32,color=WHITE,fontsize=14,fontweight="bold")
    ax.text(0,1.04,unit,transform=ax.transAxes,color=MUTED,fontsize=10)
    ax.grid(axis="y",color=GRID,linewidth=.7,alpha=.6)
    ax.set_axisbelow(True)
    ax.spines[["top","right"]].set_visible(False)
    ax.tick_params(axis="both",length=0,pad=8,labelsize=10)
    return ax


def dates(ax):
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.margins(x=.01)


def kpi(fig,x,label,value,detail,color=TEAL,width=.22):
    fig.add_artist(Rectangle((x,.645),width,.12,transform=fig.transFigure,facecolor=PANEL,edgecolor="none"))
    fig.text(x+.014,.735,label,fontsize=10,color=MUTED,fontweight="bold")
    fig.text(x+.014,.688,value,fontsize=28,fontweight="bold",color=color)
    fig.text(x+.014,.663,detail,fontsize=9,color=MUTED)


def save(fig,path):
    fig.savefig(path,facecolor=BG,dpi=140)
    plt.close(fig)


def render(root: Path) -> None:
    m = read_frame(root,"monthly").query("is_main_sample == 1")
    q = read_frame(root,"quarterly").query("is_main_sample == 1")
    summary = json.loads((root/"reports/summary.json").read_text(encoding="utf-8"))
    annual = pd.read_csv(root/"reports/annual.csv")
    correlations = pd.read_csv(root/"reports/correlations.csv")
    coefficients = pd.read_csv(root/"reports/model_coefficients.csv")
    out = root/"reports/figures"
    out.mkdir(exist_ok=True,parents=True)

    fig = canvas("El dólar se mueve. La economía responde a más factores.","132 meses y 44 trimestres para examinar precios, actividad y comercio exterior.",1)
    kpi(fig,.035,"TRM PROMEDIO · DIC 2025",number(summary["trm_dec_cop_usd"],0)+" COP","Pesos colombianos por dólar estadounidense")
    kpi(fig,.27,"VARIACIÓN TRM · DIC / DIC",number(summary["trm_dec_yoy_pct"])+"%","Promedio mensual frente a diciembre de 2024")
    kpi(fig,.505,"INFLACIÓN · DIC 2025",number(summary["inflation_dec_yoy_pct"])+"%","Variación interanual del índice de precios",GOLD)
    kpi(fig,.74,"PIB REAL · AÑO 2025",number(summary["gdp_2025_growth_pct"])+"%","Crecimiento anual · cifras preliminares",GOLD)
    ax = panel(fig,[.06,.22,.56,.315],"El recorrido del dólar","TRM promedio mensual · COP por USD")
    ax.plot(m.date,m.trm_cop_usd,color=TEAL,lw=2.3)
    ax.fill_between(m.date,m.trm_cop_usd,1800,color=TEAL,alpha=.06)
    ax.set_ylim(1800,5200)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p:number(v,0)))
    dates(ax)
    ax.annotate("2020–2021",xy=(pd.Timestamp("2020-03-01"),4400),color=MUTED,fontsize=9)
    ax.axvspan(pd.Timestamp("2020-01-01"),pd.Timestamp("2021-12-31"),color=WHITE,alpha=.045)
    ax2 = panel(fig,[.71,.22,.25,.315],"PIB: caídas y recuperación","Crecimiento interanual del PIB real · %")
    colors = [CORAL if v<0 else GOLD for v in q.gdp_yoy_pct]
    ax2.bar(q.date,q.gdp_yoy_pct,width=65,color=colors)
    ax2.axhline(0,color=MUTED,lw=.8)
    dates(ax2)
    fig.text(.06,.119,"r = "+number(summary["gdp_yoy_correlation"],2),fontsize=26,color=TEAL,fontweight="bold")
    fig.text(.20,.131,"Correlación dólar–PIB entre variaciones interanuales: débil en la muestra completa.",fontsize=12)
    fig.text(.20,.105,"Al excluir 2020–2021 cambia a +0,24. La relación es sensible al periodo y no identifica causalidad.",fontsize=11,color=MUTED)
    save(fig,out/"01_pulso_macro.png")

    fig = canvas("Una apreciación no se traduce automáticamente en menor inflación.","Las variaciones cambiarias pueden transmitirse con rezagos; la relación observada depende del horizonte.",2)
    ax = panel(fig,[.06,.45,.55,.27],"Dólar e inflación: variaciones interanuales","Variación interanual · % · una misma escala")
    ax.plot(m.date,m.trm_yoy_pct,color=TEAL,lw=1.8,label="TRM")
    ax.plot(m.date,m.inflation_yoy_pct,color=GOLD,lw=2,label="IPC")
    ax.axhline(0,color=MUTED,lw=.6)
    ax.legend(frameon=False,loc="upper left",labelcolor=WHITE,ncol=2)
    dates(ax)
    ax2 = panel(fig,[.72,.45,.23,.27],"Asociación con rezagos","Pearson r · TRM(t−k) e inflación(t)")
    corr = correlations[(correlations.outcome=="inflation_yoy_pct")&(correlations["sample"]=="2015–2025")]
    ax2.barh([f"{int(k)} mes" if k==1 else f"{int(k)} meses" for k in corr.fx_lag_months],corr.pearson_r,color=TEAL,height=.5)
    ax2.axvline(0,color=MUTED,lw=.8)
    ax2.set_xlim(-.1,.6)
    ax2.invert_yaxis()
    ax2.grid(axis="x",color=GRID,alpha=.5)
    ax3 = panel(fig,[.11,.17,.50,.15],"Rezagos del dólar en el modelo de inflación mensual","Coeficiente e IC del 95% · puntos porcentuales por 1% de variación de TRM")
    terms = coefficients[(coefficients.model=="full")&coefficients.term.str.startswith("fx_mom_lag")]
    for y,(_,row) in enumerate(terms.iterrows()):
        ax3.errorbar(row.coefficient,y,xerr=[[row.coefficient-row.ci_lower_95],[row.ci_upper_95-row.coefficient]],fmt="o",color=GOLD,capsize=4)
    ax3.set_yticks(range(len(terms)),["Rezago 1 mes","Rezago 2 meses","Rezago 3 meses"])
    ax3.axvline(0,color=MUTED,ls="--",lw=1)
    ax3.invert_yaxis()
    model = summary["inflation_model"]
    fig.text(.70,.305,number(model["fx_lags_sum"],3)+" pp",fontsize=30,fontweight="bold",color=GOLD)
    fig.text(.70,.266,"Suma de tres coeficientes cambiarios",fontsize=11)
    low,high = model["fx_lags_sum_ci95"]
    fig.text(.70,.233,f"IC 95%: {number(low,3)} a {number(high,3)} pp",fontsize=11,color=MUTED)
    fig.text(.70,.196,"El intervalo incluye cero.",fontsize=11,color=MUTED)
    fig.text(.06,.087,"Modelo exploratorio: controles de estacionalidad, Brent rezagado, persistencia de inflación y periodo de pandemia; errores HAC(12).",fontsize=10,color=MUTED)
    fig.text(.06,.064,"ADF no rechaza raíz unitaria en inflación mensual (p = 0,36). Los coeficientes no establecen una relación causal ni estable de largo plazo.",fontsize=10,color=MUTED)
    save(fig,out/"02_dolar_precios.png")

    fig = canvas("El frente externo también depende del petróleo y la demanda.","Valores nominales de bienes. Una variación en dólares combina cambios de precios, cantidades y composición.",3)
    kpi(fig,.035,"EXPORTACIONES · 2025",number(summary["exports_2025_usd_m"]),"Millones de USD FOB · suma del año")
    kpi(fig,.27,"IMPORTACIONES · 2025",number(summary["imports_2025_usd_m"]),"Millones de USD FOB · suma del año",GOLD)
    kpi(fig,.505,"BALANZA DE BIENES · 2025",number(summary["trade_balance_2025_usd_m"]),"Millones de USD FOB · exportaciones − importaciones",CORAL)
    kpi(fig,.74,"TRM–BRENT · CORRELACIÓN",number(summary["monthly_correlations"]["brent_yoy_pct"],2),"Variaciones interanuales mensuales · 2015–2025",GOLD)
    ax = panel(fig,[.06,.22,.48,.315],"Comercio exterior por año","Miles de millones de USD FOB")
    years = annual.year.to_numpy()
    ax.bar(years-.18,annual.exports_usd_m/1000,width=.36,color=TEAL,label="Exportaciones")
    ax.bar(years+.18,annual.imports_usd_m/1000,width=.36,color=GOLD,label="Importaciones")
    ax.set_xticks(years)
    ax.legend(frameon=False,labelcolor=WHITE,loc="upper left",ncol=2,fontsize=10)
    ax2 = panel(fig,[.64,.22,.31,.315],"Dólar y Brent: trayectorias relativas","Índice: enero de 2015 = 100 · escalas comparables")
    ax2.plot(m.date,m.trm_cop_usd/m.trm_cop_usd.iloc[0]*100,color=TEAL,label="TRM",lw=2)
    ax2.plot(m.date,m.brent_usd_bbl/m.brent_usd_bbl.iloc[0]*100,color=GOLD,label="Brent",lw=1.8)
    ax2.legend(frameon=False,labelcolor=WHITE,loc="upper left",ncol=2,fontsize=10)
    dates(ax2)
    fig.text(.06,.124,"FOB / FOB",fontsize=23,fontweight="bold",color=CORAL)
    fig.text(.23,.13,"La balanza compara ambas corrientes con la misma valoración.",fontsize=12)
    fig.text(.23,.102,"Los resultados no permiten atribuir el déficit comercial únicamente al nivel del dólar.",fontsize=11,color=MUTED)
    save(fig,out/"03_sector_externo.png")
    print("Tres láminas analíticas exportadas.")
