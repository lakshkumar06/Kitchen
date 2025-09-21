# orchestrator/agents/manager.py

# System prompt used by Gemini to produce ONE normalized spec.json
MANAGER_SYS = """
You are a software planner. Output ONLY valid JSON matching this schema:
{app:{name:string,non_functional?:string[]},
 entities:[{name,fields:[{name,type,required?,primary?,default?,values?}],
           relations?:[{type,target,via?}]}],
 pages:[{path,type,entity?,actions?,filters?,tabs?}],
 api_conventions?:{base_path:string,list_suffix:string,pagination:boolean},
 idea_candidates?: string[] }

Rules:
- Field names = snake_case; entity names = PascalCase.
- Types ∈ [uuid,string,text,int,float,bool,date,datetime,enum]; enums require `values`.
- Restrict to CRUD + dashboard patterns; no external JS/CSS frameworks.
- If user has no idea, propose EXACTLY 4 ideas in idea_candidates; otherwise omit it.
Return JSON only—no prose.
"""

# Optional: show 4 choices when the user picked only a domain
DOMAIN_STARTERS = {
    "Healthcare": ["ClinicApp", "MedicationTracker", "AppointmentScheduler", "TeleconsultNotes"],
    "Education":  ["CourseHub", "AssignmentTracker", "QuizBuilder", "OfficeHoursScheduler"],
    "Ecommerce":  ["MiniShop", "InventoryTracker", "OrderDesk", "CouponManager"],
    "Art":        ["Portfolio", "CommissionBoard", "GalleryManager", "EventSignup"]
}

def build_spec_prompt(idea: str) -> str:
    """Prompt to turn a concrete idea into spec.json."""
    return (
        f"User idea: {idea}\n"
        "Produce ONLY JSON matching the schema and rules in the system prompt."
    )

def build_ideas_prompt(domain: str) -> str:
    """Prompt to get exactly 4 idea candidates for a chosen domain (JSON array)."""
    return (
        f"For domain '{domain}', return EXACTLY 4 concise app ideas as a JSON array of strings. "
        "No explanations."
    )
