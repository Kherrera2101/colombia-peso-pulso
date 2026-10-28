"""Definiciones editables PBIP, PBIR y TMSL del informe."""
from pathlib import Path
import uuid
import pandas as pd
from .io import read_frame, write_json

SCHEMA = "https://developer.microsoft.com/json-schemas/"
BG, PANEL, WHITE, MUTED, TEAL, GOLD = "#0B1320","#142238","#F0F3F5","#9BAFC2","#4CE0B3","#F3C66B"

MEASURES = [
    ("TRM promedio", "DIVIDE(SUMX(Monthly, Monthly[trm_cop_usd] * Monthly[fx_days]), SUM(Monthly[fx_days]))", "#,0.00", "TRM ponderada por días calendario dentro de la selección."),
    ("TRM último mes", "VAR D = MAX(Monthly[date]) RETURN CALCULATE(MAX(Monthly[trm_cop_usd]), KEEPFILTERS(Monthly[date] = D))", "#,0.00", "Promedio de TRM del último mes de la selección."),
    ("Cambio TRM interanual", "DIVIDE(AVERAGE(Monthly[trm_yoy_pct]), 100)", "0.0%;-0.0%;0.0%", "Media de variaciones interanuales; no es la variación de la TRM media anual."),
    ("Cambio TRM último mes", "VAR D = MAX(Monthly[date]) RETURN CALCULATE(DIVIDE(MAX(Monthly[trm_yoy_pct]), 100), KEEPFILTERS(Monthly[date] = D))", "0.0%;-0.0%;0.0%", "Variación interanual del promedio mensual de TRM en el último mes."),
    ("Inflación interanual", "DIVIDE(AVERAGE(Monthly[inflation_yoy_pct]), 100)", "0.0%", "Media de inflación interanual de los meses seleccionados."),
    ("Inflación último mes", "VAR D = MAX(Monthly[date]) RETURN CALCULATE(DIVIDE(MAX(Monthly[inflation_yoy_pct]), 100), KEEPFILTERS(Monthly[date] = D))", "0.0%", "Inflación interanual del último mes seleccionado."),
    ("Inflación mensual", "DIVIDE(AVERAGE(Monthly[inflation_mom_pct]), 100)", "0.00%", "Variación mensual del índice IPC."),
    ("Exportaciones FOB", "SUM(Monthly[exports_usd_m])", "#,0.0", "Exportaciones de bienes en millones de USD FOB."),
    ("Importaciones FOB", "SUM(Monthly[imports_usd_m])", "#,0.0", "Importaciones de bienes en millones de USD FOB."),
    ("Balanza de bienes", "[Exportaciones FOB] - [Importaciones FOB]", "#,0.0;-#,0.0;0", "Exportaciones menos importaciones, ambas FOB; millones de USD."),
    ("Brent promedio", "DIVIDE(SUMX(Monthly, Monthly[brent_usd_bbl] * Monthly[brent_days]), SUM(Monthly[brent_days]))", "0.00", "Precio Brent ponderado por observaciones hábiles, USD por barril."),
    ("Cambio exportaciones interanual", "DIVIDE(AVERAGE(Monthly[exports_yoy_pct]), 100)", "0.0%;-0.0%;0.0%", "Media de variaciones interanuales nominales de exportaciones."),
    ("Cambio importaciones interanual", "DIVIDE(AVERAGE(Monthly[imports_yoy_pct]), 100)", "0.0%;-0.0%;0.0%", "Media de variaciones interanuales nominales de importaciones."),
    ("Meses observados", "COUNTROWS(Monthly)", "0", "Cantidad de meses en el contexto de filtro."),
    ("PIB crecimiento interanual", "DIVIDE(AVERAGE(Quarterly[gdp_yoy_pct]), 100)", "0.0%;-0.0%;0.0%", "Crecimiento real interanual; en más de un trimestre muestra la media."),
    ("PIB último trimestre", "VAR D = MAX(Quarterly[date]) RETURN CALCULATE(DIVIDE(MAX(Quarterly[gdp_yoy_pct]), 100), KEEPFILTERS(Quarterly[date] = D))", "0.0%;-0.0%;0.0%", "Crecimiento real interanual del último trimestre seleccionado, no del año completo."),
    ("PIB variación trimestral SA", "DIVIDE(AVERAGE(Quarterly[gdp_qoq_sa_pct]), 100)", "0.0%;-0.0%;0.0%", "Variación trimestral del PIB ajustado por estacionalidad y calendario."),
    ("Índice TRM", "VAR D = MINX(ALLSELECTED(Calendar), Calendar[date]) VAR B = CALCULATE([TRM promedio], REMOVEFILTERS(Calendar), Calendar[date] = D) RETURN 100 * DIVIDE([TRM promedio], B)", "0.0", "Primer mes de la selección = 100."),
    ("Índice Brent", "VAR D = MINX(ALLSELECTED(Calendar), Calendar[date]) VAR B = CALCULATE([Brent promedio], REMOVEFILTERS(Calendar), Calendar[date] = D) RETURN 100 * DIVIDE([Brent promedio], B)", "0.0", "Primer mes de la selección = 100."),
    ("Correlación TRM inflación", "VAR S = FILTER(ADDCOLUMNS(VALUES(Calendar[month_label]), \"X\", CALCULATE(AVERAGE(Monthly[trm_yoy_pct])), \"Y\", CALCULATE(AVERAGE(Monthly[inflation_yoy_pct]))), NOT ISBLANK([X]) && NOT ISBLANK([Y])) VAR N = COUNTROWS(S) VAR SX = SUMX(S, [X]) VAR SY = SUMX(S, [Y]) VAR SXX = SUMX(S, [X] * [X]) VAR SYY = SUMX(S, [Y] * [Y]) VAR SXY = SUMX(S, [X] * [Y]) RETURN IF(N > 2, DIVIDE(N * SXY - SX * SY, SQRT(MAX(0, (N * SXX - SX * SX) * (N * SYY - SY * SY)))))", "0.00;-0.00;0.00", "Pearson r contemporáneo sobre pares de meses, recalculado al filtrar."),
]


def lit(value):
    if isinstance(value,bool): token = "true" if value else "false"
    elif isinstance(value,(int,float)): token = str(value)+"D"
    else: token = "'"+str(value).replace("'","''")+"'"
    return {"expr":{"Literal":{"Value":token}}}


def color(value):
    return {"solid":{"color":lit(value)}}


def column(table,name):
    return {"Column":{"Expression":{"SourceRef":{"Entity":table}},"Property":name}}


def measure(name):
    return {"Measure":{"Expression":{"SourceRef":{"Entity":"Monthly"}},"Property":name}}


def projection(field,label):
    return {"field":field,"queryRef":label,"nativeQueryRef":label}


def visual(name,kind,position,title="",roles=None,objects=None):
    value = {"$schema":SCHEMA+"fabric/item/report/definition/visualContainer/2.13.0/schema.json","name":name,"position":dict(zip(["x","y","width","height"],position)),"visual":{"visualType":kind,"visualContainerObjects":{"title":[{"properties":{"show":lit(bool(title)),"text":lit(title),"fontColor":color(WHITE),"fontSize":lit(14),"fontFamily":lit("Segoe UI Semibold")}}],"background":[{"properties":{"show":lit(True),"color":color(PANEL),"transparency":lit(0)}}],"border":[{"properties":{"show":lit(False)}}]},"objects":objects or {}}}
    if roles:
        value["visual"]["query"]={"queryState":{key:{"projections":items} for key,items in roles.items()}}
        if "Category" in roles:
            value["visual"]["query"]["sortDefinition"]={"sort":[{"field":roles["Category"][0]["field"],"direction":"Ascending"}],"isDefaultSort":False}
    return value


def textbox(name,text,position,size=14,ink=WHITE):
    value=visual(name,"textbox",position)
    value["visual"]["objects"]={"general":[{"properties":{"paragraphs":[{"textRuns":[{"value":text,"textStyle":{"fontFamily":"Segoe UI","fontSize":str(size)+"pt","color":ink}}]}]}}]}
    value["visual"]["visualContainerObjects"]["background"][0]["properties"]["color"]=color(BG)
    return value


def chart(name,kind,position,title,category,measures):
    table,col=category
    roles={"Category":[projection(column(table,col),table+"."+col)],"Y":[projection(measure(m),"Monthly."+m) for m in measures]}
    objects={
        "categoryAxis":[{"properties":{"labelColor":color(MUTED),"fontSize":lit(10),"showAxisTitle":lit(False)}}],
        "valueAxis":[{"properties":{"labelColor":color(MUTED),"fontSize":lit(10),"showAxisTitle":lit(False),"gridlineColor":color("#2C3B4E")}}],
        "legend":[{"properties":{"show":lit(len(measures)>1),"labelColor":color(WHITE),"fontSize":lit(11)}}],
        "dataPoint":[{"properties":{"defaultColor":color(TEAL)}}]+[{"selector":{"metadata":"Monthly."+m},"properties":{"fill":color(TEAL if i==0 else GOLD)}} for i,m in enumerate(measures)],
    }
    return visual(name,kind,position,title,roles,objects)


def create(root: Path) -> None:
    dest=root/"powerbi"
    model_dir=dest/"PesoPulso.SemanticModel"
    report_dir=dest/"PesoPulso.Report"
    model_dir.mkdir(exist_ok=True,parents=True)
    report_dir.mkdir(exist_ok=True,parents=True)
    tables=[]
    layouts={
        "Calendar":("calendar","calendar_main",["date","year","month","month_label","quarter_label"]),
        "Monthly":("monthly","monthly_main",["date","trm_cop_usd","fx_days","cpi_index","inflation_mom_pct","inflation_yoy_pct","trm_yoy_pct","exports_usd_m","imports_usd_m","exports_yoy_pct","imports_yoy_pct","trade_balance_usd_m","brent_usd_bbl","brent_days","regime"]),
        "Quarterly":("quarterly","quarterly_main",["date","gdp_real_original","gdp_real_sa","gdp_yoy_pct","gdp_qoq_sa_pct","trm_yoy_pct","revision"]),
    }
    for name,(filename,view,fields) in layouts.items():
        frame=read_frame(root,filename)
        columns=[]
        for field in fields:
            dtype="dateTime" if field=="date" else "int64" if field in ["year","month","fx_days","brent_days"] else "string" if field in ["month_label","quarter_label","regime","revision"] else "double"
            col={"name":field,"dataType":dtype,"sourceColumn":field,"summarizeBy":"none","isHidden":name!="Calendar" and dtype!="string"}
            if field=="date":col.update(formatString="yyyy-MM-dd",annotations=[{"name":"UnderlyingDateTimeDataType","value":"Date"}])
            columns.append(col)
        partition={"name":name,"mode":"import","source":{"type":"m","expression":["let","    Source = PostgreSQL.Database(Server, Database, [CreateNavigationProperties = false]),",f'    Data = Source{{[Schema="pp_mart", Item="{view}"]}}[Data]',"in","    Data"]}}
        table={"name":name,"columns":columns,"partitions":[partition]}
        if name=="Calendar":
            table["columns"][0]["isKey"]=True
            table["dataCategory"]="Time"
        if name=="Monthly":
            table["measures"]=[{"name":n,"expression":e,"formatString":f,"description":d,"displayFolder":"Indicadores"} for n,e,f,d in MEASURES]
        tables.append(table)
    relationships=[{"name":str(uuid.uuid5(uuid.NAMESPACE_DNS,"peso-pulso-"+table)),"fromTable":table,"fromColumn":"date","toTable":"Calendar","toColumn":"date","fromCardinality":"many","toCardinality":"one","crossFilteringBehavior":"oneDirection","isActive":True} for table in ["Monthly","Quarterly"]]
    expressions=[{"name":"Server","kind":"m","expression":'"127.0.0.1:5433" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'},{"name":"Database","kind":"m","expression":'"peso_pulso" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'}]
    write_json(model_dir/"model.bim",{"name":"PesoPulso","compatibilityLevel":1567,"model":{"culture":"es-CO","defaultPowerBIDataSourceVersion":"powerBI_V3","sourceQueryCulture":"en-US","tables":tables,"relationships":relationships,"expressions":expressions,"annotations":[{"name":"PBI_TimeIntelligenceEnabled","value":"0"}]}})
    write_json(model_dir/"definition.pbism",{"$schema":SCHEMA+"fabric/item/semanticModel/definitionProperties/1.0.0/schema.json","version":"1.0","settings":{}})
    write_json(dest/"PesoPulso.pbip",{"$schema":SCHEMA+"fabric/pbip/pbipProperties/1.0.0/schema.json","version":"1.0","artifacts":[{"report":{"path":"PesoPulso.Report"}}],"settings":{"enableAutoRecovery":True}})
    write_json(report_dir/"definition.pbir",{"$schema":SCHEMA+"fabric/item/report/definitionProperties/2.0.0/schema.json","version":"4.0","datasetReference":{"byPath":{"path":"../PesoPulso.SemanticModel"}}})
    definition=report_dir/"definition"
    write_json(definition/"version.json",{"$schema":SCHEMA+"fabric/item/report/definition/versionMetadata/1.0.0/schema.json","version":"2.0.0"})
    write_json(definition/"report.json",{"$schema":SCHEMA+"fabric/item/report/definition/report/3.3.0/schema.json","themeCollection":{"baseTheme":{"name":"CY24SU06","reportVersionAtImport":{"visual":"1.8.0","page":"1.3.0","report":"2.0.0"},"type":"SharedResources"}},"settings":{"useStylableVisualContainerHeader":True}})
    pages=[("01_pulso_macro","Pulso macro"),("02_dolar_precios","Dólar y precios"),("03_sector_externo","Sector externo")]
    write_json(definition/"pages/pages.json",{"$schema":SCHEMA+"fabric/item/report/definition/pagesMetadata/1.1.0/schema.json","pageOrder":[p[0] for p in pages],"activePageName":pages[0][0]})
    for page_name,label in pages:
        folder=definition/"pages"/page_name
        write_json(folder/"page.json",{"$schema":SCHEMA+"fabric/item/report/definition/page/2.1.0/schema.json","name":page_name,"displayName":label,"displayOption":"FitToPage","width":1440,"height":900,"objects":{"background":[{"properties":{"color":color(BG),"transparency":lit(0)}}]}})
        visuals=[textbox("brand","PESO & PULSO",[36,20,800,48],28),textbox("subtitle",label.upper()+"  /  COLOMBIA · 2015–2025",[38,76,1000,32],13,TEAL),textbox("footer","SFC · Portal de Datos Abiertos www.datos.gov.co | DIAN–DANE | EIA · Corte: 28 oct 2026. Asociaciones observadas; sin identificación causal.",[36,856,1360,28],9,MUTED)]
        slicer=visual("year_filter","slicer",[1140,24,260,86],"Año",{"Values":[projection(column("Calendar","year"),"Calendar.year")]},{"data":[{"properties":{"mode":lit("Dropdown")}}],"items":[{"properties":{"fontColor":color(WHITE),"background":color(PANEL)}}],"header":[{"properties":{"fontColor":color(WHITE)}}]})
        slicer["visual"]["syncGroup"]={"groupName":"Year","fieldChanges":True,"filterChanges":True}
        visuals.append(slicer)
        if page_name=="01_pulso_macro":
            cards=[("TRM último mes","TRM último mes · COP/USD"),("Cambio TRM último mes","TRM último mes · variación a/a"),("Inflación último mes","IPC último mes · variación a/a"),("PIB último trimestre","PIB último trimestre · variación a/a")]
            for i,(m,title) in enumerate(cards):
                visuals.append(visual("kpi_"+str(i),"card",[36+i*347,132,330,116],title,{"Values":[projection(measure(m),"Monthly."+m)]},{"labels":[{"properties":{"color":color(TEAL if i<2 else GOLD),"fontSize":lit(30)}}],"categoryLabels":[{"properties":{"show":lit(False)}}]}))
            visuals += [chart("fx_history","lineChart",[36,280,850,430],"TRM promedio mensual · COP/USD",("Calendar","month_label"),["TRM promedio"]),chart("gdp_growth","clusteredColumnChart",[912,280,490,430],"PIB real · crecimiento interanual",("Calendar","quarter_label"),["PIB crecimiento interanual"]),textbox("interpretation","La asociación dólar–PIB es sensible al periodo. El PIB conserva su frecuencia trimestral; la TRM conserva el peso de cada día calendario.",[36,750,1366,64],16,MUTED)]
        elif page_name=="02_dolar_precios":
            visuals += [chart("fx_inflation","lineChart",[36,136,1366,360],"Dólar e inflación · variaciones interanuales",("Calendar","month_label"),["Cambio TRM interanual","Inflación interanual"]),chart("regime_inflation","clusteredColumnChart",[36,526,850,260],"Inflación interanual media por régimen cambiario",("Monthly","regime"),["Inflación interanual"]),visual("correlation","card",[912,526,490,132],"Pearson r · dólar e inflación",{"Values":[projection(measure("Correlación TRM inflación"),"Monthly.Correlación TRM inflación")]},{"labels":[{"properties":{"color":color(TEAL),"fontSize":lit(32)}}]}),textbox("model_note","Modelo exploratorio: tres rezagos de TRM, Brent, persistencia del IPC, efectos mensuales y pandemia. HAC(12). Detalle e intervalos en reports/.",[912,674,490,132],13,MUTED)]
        else:
            visuals += [chart("annual_trade","clusteredColumnChart",[36,136,850,340],"Exportaciones e importaciones · millones de USD FOB",("Calendar","year"),["Exportaciones FOB","Importaciones FOB"]),chart("trade_balance","clusteredColumnChart",[912,136,490,340],"Balanza de bienes · millones de USD FOB",("Calendar","year"),["Balanza de bienes"]),chart("oil_fx_indices","lineChart",[36,506,850,310],"Dólar y Brent · primer mes seleccionado = 100",("Calendar","month_label"),["Índice TRM","Índice Brent"]),textbox("valuation_note","FOB / FOB\n\nAmbas corrientes usan la misma valoración. Los valores nominales combinan precios, cantidades y composición. La balanza de bienes no equivale a la cuenta corriente.",[912,526,490,260],17,MUTED)]
        for z,v in enumerate(visuals):
            v["position"].update(z=z,tabOrder=z)
            write_json(folder/"visuals"/v["name"]/"visual.json",v)
    write_json(dest/"theme.json",{"name":"Peso & Pulso","dataColors":[TEAL,GOLD,"#F28179","#8CAAF2"],"background":BG,"foreground":WHITE,"tableAccent":TEAL,"textClasses":{"label":{"fontFace":"Segoe UI","color":MUTED},"title":{"fontFace":"Segoe UI Semibold","color":WHITE},"callout":{"fontFace":"Segoe UI Semibold","color":TEAL}}})
    dax_dir=model_dir/"DAXQueries"
    dax_dir.mkdir(exist_ok=True)
    (dax_dir/"01_indicadores_anuales.dax").write_text('EVALUATE\nSUMMARIZECOLUMNS(\n    Calendar[year],\n    "TRM promedio", [TRM promedio],\n    "Exportaciones USD M", [Exportaciones FOB],\n    "Importaciones USD M", [Importaciones FOB],\n    "Balanza USD M", [Balanza de bienes]\n)\nORDER BY Calendar[year]\n',encoding="utf-8")
    md=["# Medidas del modelo","", "Las tasas almacenadas en puntos porcentuales se dividen por 100 antes de aplicar el formato de porcentaje de Power BI. Los importes comerciales se expresan en millones de USD FOB.",""]
    for n,e,f,d in MEASURES:
        md.extend(["## "+n,"",d,"","```dax",n+" = "+e,"```",""])
    (dest/"MEDIDAS.md").write_text("\n".join(md),encoding="utf-8")
    print(f"Power BI: {len(pages)} páginas, {len(MEASURES)} medidas DAX y 3 tablas.")
