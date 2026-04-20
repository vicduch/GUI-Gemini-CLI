from core.models import Agent, Session


def test_session_creation():
    session = Session(id="sess-1", model="gemini-3.1-pro", workspace="/tmp")
    assert session.id == "sess-1"
    assert session.model == "gemini-3.1-pro"

def test_agent_creation():
    agent = Agent(id="agt-1", status="running", role="master")
    assert agent.id == "agt-1"
    assert agent.status == "running"
