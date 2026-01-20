"""Server configuration module - server_config.py"""
from livekit.agents import AgentServer, JobProcess
from livekit.plugins import silero


def prewarm(proc: JobProcess):
    """Prewarm function for loading VAD model."""
    proc.userdata["vad"] = silero.VAD.load()


def create_server() -> AgentServer:
    """Factory function to create and configure the AgentServer."""
    server = AgentServer()
    server.setup_fnc = prewarm
    return server
