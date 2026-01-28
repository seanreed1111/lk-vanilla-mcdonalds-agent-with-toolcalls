"""Main agent file using separate server config."""
from loguru import logger
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    cli,
    inference,
    room_io,
)
from livekit.plugins import noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# Import from your new config module
from server_config import create_server


load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful voice AI assistant. The user is interacting with you via voice, even if you perceive the conversation as text.
            You eagerly assist users with their questions by providing information from your extensive knowledge.
            Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
            You are curious, friendly, and have a sense of humor.""",
        )


def setup_agent_handlers(server):
    """Set up agent session handlers on the server."""

    @server.rtc_session()
    async def my_agent(ctx: JobContext):
        # Logging setup
        ctx.log_context_fields = {
            "room": ctx.room.name,
        }

        # Set up a voice AI pipeline
        session = AgentSession(
            stt=inference.STT(model="assemblyai/universal-streaming", language="en"),
            llm=inference.LLM(model="openai/gpt-4.1-nano"),
            tts=inference.TTS(model="inworld/inworld-tts-1", voice="Ashley"),
            turn_detection=MultilingualModel(),
            vad=ctx.proc.userdata["vad"],
            preemptive_generation=True,
        )

        # Start the session
        await session.start(
            agent=Assistant(),
            room=ctx.room,
            room_options=room_io.RoomOptions(
                audio_input=room_io.AudioInputOptions(
                    noise_cancellation=lambda params: noise_cancellation.BVCTelephony()
                    if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC(),
                ),
            ),
        )

        # Join the room and connect to the user
        await ctx.connect()


if __name__ == "__main__":
    server = create_server()
    setup_agent_handlers(server)
    cli.run_app(server)
