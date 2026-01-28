from loguru import logger
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    inference,
    room_io,
)
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel


load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful voice AI assistant. The user is interacting with you via voice, even if you perceive the conversation as text.
            You eagerly assist users with their questions by providing information from your extensive knowledge.
            Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
            You are curious, friendly, and have a sense of humor.""",
        )


class VoiceAgentApp:
    """Encapsulates the voice agent application with no globals."""

    def __init__(self):
        self.server = AgentServer()
        self._setup_server()

    def _setup_server(self):
        """Configure the server with prewarm and session handler."""
        self.server.setup_fnc = self._prewarm
        self.server.rtc_session()(self._agent_session_handler)

    @staticmethod
    def _prewarm(proc: JobProcess):
        """Prewarm function for loading VAD model."""
        proc.userdata["vad"] = silero.VAD.load()

    @staticmethod
    async def _agent_session_handler(ctx: JobContext):
        """Handle RTC sessions."""
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

    def run(self):
        """Run the application."""
        cli.run_app(self.server)


if __name__ == "__main__":
    app = VoiceAgentApp()
    app.run()
