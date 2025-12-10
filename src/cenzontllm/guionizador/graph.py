# src/cenzontllm/guionizador/graph.py
import json
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from .agents.host import HostAgent
from .agents.guest import GuestAgent
from .agents.writer import WriterAgent
from .config import settings

class PodcastState(TypedDict):
    paper: Dict
    guests: List[Dict]
    outline: List[str]
    conversation: List[Dict[str, str]]
    round: int
    final_script: str
    should_end: bool

def create_podcast_graph(paper_json_path: str) -> Dict:
    with open(paper_json_path, "r", encoding="utf-8") as f:
        paper = json.load(f)

    host = HostAgent()
    guest_agents = [GuestAgent() for _ in range(settings.NUM_GUESTS)]
    writer = WriterAgent()

    workflow = StateGraph(PodcastState)

    def init_host(_: PodcastState):
        print("[HOST] Generando personalidades y outline...")
        result = host.generate_personalities_and_outline(paper)
        return {
            "paper": paper,
            "guests": result.get("guests", [{"name": "Dr. Luis Ramírez", "age": 50, "accent": "mexicano", "bio": "experto", "style": "claro"}]),
            "outline": result.get("outline", ["Intro", "Problema", "Solución", "Conclusiones"]),
            "conversation": [{"speaker": "Ana", "text": "¡Bienvenidos a CenzontLLM!"}],
            "round": 0,
            "final_script": "",
            "should_end": False
        }

    def guests_respond(state: PodcastState):
        print(f"[GUESTS] Ronda {state['round'] + 1}")
        history = "\n".join(f"{t['speaker']}: {t['text']}" for t in state["conversation"])
        new_turns = []
        paper = state.get("paper", {})
        
        for q in state["outline"]:
            for i, guest in enumerate(state["guests"]):
                # Pasar el paper completo al GuestAgent
                resp = guest_agents[i].respond(q, history, guest, paper)
                new_turns.append({"speaker": guest["name"], "text": resp})
            new_turns.append({"speaker": "Ana", "text": "¡Perfecto!"})
        
        return {
            "conversation": state["conversation"] + new_turns,
            "round": state["round"] + 1
        }

    def host_evaluate(state: PodcastState):
        print("[HOST] Decidiendo si terminar...")
        return {"should_end": True}

    def writer_finalize(state: PodcastState):
        print("[WRITER] Generando guion final...")
        conv = "\n".join(f"{t['speaker']}: {t['text']}" for t in state["conversation"])
        script = writer.write(conv, state["guests"], settings.TARGET_MINUTES)
        print(f"[WRITER] Guion generado ({len(script)} caracteres)")
        return {"final_script": script}

    workflow.add_node("init", init_host)
    workflow.add_node("respond", guests_respond)
    workflow.add_node("evaluate", host_evaluate)
    workflow.add_node("finalize", writer_finalize)

    workflow.set_entry_point("init")
    workflow.add_edge("init", "respond")
    workflow.add_edge("respond", "evaluate")
    workflow.add_conditional_edges(
        "evaluate",
        lambda s: "finalize" if s["should_end"] else "respond"
    )
    workflow.add_edge("finalize", END)

    app = workflow.compile()

    config = {"configurable": {"thread_id": "cenzontllm_demo"}}

    # Estado inicial vacío pero con todas las claves
    initial_state = {
        "paper": {},
        "guests": [],
        "outline": [],
        "conversation": [],
        "round": 0,
        "final_script": "",
        "should_end": False
    }

    # Ejecutamos y capturamos el estado final
    final_state = {}
    for step in app.stream(initial_state, config=config):
        if step:
            final_state.update(step)

    final_script = final_state.get('finalize', {}).get('final_script', "Error: no se generó guion")

    print("[GRAPH DEBUG] Final_script: ", final_script)

    return {"final_script": final_script}
