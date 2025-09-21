import os, json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MANAGER_SYS = """You produce ONLY valid JSON app specs for CRUD dashboards.
Schema:
{app:{name:string,non_functional?:string[]},
 entities:[{name,fields:[{name,type,required?,primary?,default?,values?}],relations?:[{type,target,via?}]}],
 pages:[{path,type,entity?,actions?,filters?,tabs?}],
 api_conventions?:{base_path:string,list_suffix:string,pagination:boolean}}
Constraints: snake_case fields, PascalCase entity names, types ∈ [uuid,string,text,int,float,bool,date,datetime,enum].
"""

SAMPLE_SPEC = {
  "app": {"name": "TaskTrack", "non_functional": ["auth-basic","pagination"]},
  "entities": [
    {"name":"Project","fields":[
      {"name":"id","type":"uuid","primary":True},
      {"name":"name","type":"string","required":True},
      {"name":"created_at","type":"datetime","default":"now"}], "relations":[]},
    {"name":"Task","fields":[
      {"name":"id","type":"uuid","primary":True},
      {"name":"title","type":"string","required":True},
      {"name":"status","type":"enum","values":["TODO","DOING","DONE"],"default":"TODO"},
      {"name":"project_id","type":"uuid","required":True}],
      "relations":[{"type":"belongsTo","target":"Project","via":"project_id"}]}
  ],
  "pages":[
    {"path":"/","type":"dashboard","widgets":["ProjectCount","TasksByStatus"]},
    {"path":"/projects","type":"list","entity":"Project","actions":["create"]},
    {"path":"/tasks","type":"list","entity":"Task","filters":["status","project_id"]}
  ]
}

def plan_spec(idea: str | None, domain: str | None):
    if not idea:
        # For speed in MVP, just return a sample spec. Replace with idea prompt if you want.
        return SAMPLE_SPEC
    prompt = f"User idea: {idea}\nReturn ONLY JSON matching the schema."
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=MANAGER_SYS)
    out = model.generate_content(prompt).text
    try:
        return json.loads(out)
    except Exception:
        return out  # let validator attempt to fix

def fix_invalid_json(bad):
    # simple fixer request
    model = genai.GenerativeModel("gemini-1.5-flash")
    out = model.generate_content(f"Fix to valid JSON, keep semantics:\n```{bad}```").text
    return out
