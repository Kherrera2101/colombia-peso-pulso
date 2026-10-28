"""Validación de archivos PBIR contra los esquemas oficiales de Microsoft."""
from pathlib import Path
import json
import requests
from jsonschema.validators import validator_for
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
CACHE = {}


def retrieve(uri):
    if uri not in CACHE:
        response = requests.get(uri,timeout=60)
        response.raise_for_status()
        CACHE[uri]=response.json()
    return Resource.from_contents(CACHE[uri])


def validate():
    registry=Registry(retrieve=retrieve)
    count=0
    for path in sorted((ROOT/"powerbi").rglob("*")):
        if not path.is_file() or path.suffix not in [".json",".pbip",".pbir",".pbism"]:
            continue
        doc=json.loads(path.read_text(encoding="utf-8"))
        if "$schema" not in doc:
            continue
        uri=doc["$schema"]
        retrieve(uri)
        schema=CACHE[uri]
        validator=validator_for(schema)(schema,registry=registry)
        errors=list(validator.iter_errors(doc))
        if errors:
            text="\n".join(f"{list(e.absolute_path)}: {e.message}" for e in errors[:8])
            raise ValueError(f"{path.relative_to(ROOT)}\n{text}")
        count+=1
    model=json.loads((ROOT/"powerbi/PesoPulso.SemanticModel/model.bim").read_text(encoding="utf-8"))["model"]
    fields={t["name"]:{c["name"] for c in t["columns"]} for t in model["tables"]}
    measures={t["name"]:{m["name"] for m in t.get("measures",[])} for t in model["tables"]}
    refs=0
    def walk(item):
        nonlocal refs
        if isinstance(item,dict):
            for kind in ["Column","Measure"]:
                if kind in item:
                    value=item[kind]
                    entity=value.get("Expression",{}).get("SourceRef",{}).get("Entity")
                    if entity:
                        collection=fields if kind=="Column" else measures
                        if value["Property"] not in collection.get(entity,set()):
                            raise ValueError(f"Referencia inexistente {entity}.{value['Property']}")
                        refs+=1
            for value in item.values():walk(value)
        elif isinstance(item,list):
            for value in item:walk(value)
    visual_paths=list((ROOT/"powerbi/PesoPulso.Report").rglob("visual.json"))
    for path in visual_paths:
        doc=json.loads(path.read_text(encoding="utf-8"))
        walk(doc)
        box=doc["position"]
        if min(box["x"],box["y"])<0 or box["x"]+box["width"]>1440 or box["y"]+box["height"]>900:
            raise ValueError("Visual fuera de la página.")
    result={"status":"passed","official_schemas_validated_files":count,"visuals":len(visual_paths),"model_field_references_checked":refs,"model_tables":len(fields),"dax_measures":sum(map(len,measures.values())),"desktop_opened":False,"dax_executed_in_desktop":False,"scope":"Validación de esquemas PBIR y referencias del modelo; no sustituye apertura, actualización y renderizado en Power BI Desktop."}
    (ROOT/"reports/powerbi_validation.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__":
    validate()
