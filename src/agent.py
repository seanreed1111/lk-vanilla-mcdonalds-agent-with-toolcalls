"""McDonald's Drive-Thru Agent CLI.

This module provides the command-line interface for running the drive-thru agent
in various modes (console, dev, production) using LiveKit's built-in CLI.
"""

from dotenv import load_dotenv
from livekit.agents import AgentServer, JobContext, JobProcess, cli
from livekit.plugins import silero
from loguru import logger

from config import AppConfig
from conversation_logger import ConversationLogger
from logging_config import setup_logging
from session_handler import DriveThruSessionHandler

# Load environment variables
load_dotenv(".env.local")

# Configure logging
setup_logging()


def _prewarm(proc: JobProcess):
    """Module-level prewarm function for loading VAD model."""
    proc.userdata["vad"] = silero.VAD.load()


async def _handle_rtc_session(ctx: JobContext):
    """Module-level RTC session handler."""
    from livekit.agents import NOT_GIVEN, AgentSession, room_io
    from livekit.plugins import noise_cancellation
    from livekit.plugins.turn_detector.multilingual import MultilingualModel

    from factories import create_stt, create_tts

    # Initialize config and handler for this worker process
    config = AppConfig()
    handler = DriveThruSessionHandler(config)

    session_id = ctx.room.name

    logger.info(f"Starting drive-thru session for room: {session_id}")

    # Create drive-thru agent
    drive_thru_agent = await handler.create_agent(session_id)

    # Verify agent has tools registered
    logger.info(f"Agent has {len(drive_thru_agent.tools)} tools available")
    logger.debug(f"Agent LLM type: {type(drive_thru_agent.llm).__name__}")
    logger.debug(f"Agent has instructions: {len(drive_thru_agent.instructions) if hasattr(drive_thru_agent, 'instructions') else 'unknown'} chars")

    # Create voice pipeline components
    stt = create_stt(config.pipeline)
    tts = create_tts(config.pipeline)

    # Set up turn detection and VAD
    turn_detection = (
        MultilingualModel()
        if config.session.use_multilingual_turn_detector
        else NOT_GIVEN
    )
    vad = ctx.proc.userdata.get("vad") or NOT_GIVEN

    # Create AgentSession
    # Note: LLM is configured on the Agent itself, not here
    logger.debug("Creating AgentSession...")
    session = AgentSession(
        stt=stt,
        tts=tts,
        turn_detection=turn_detection,
        vad=vad,
        preemptive_generation=config.session.preemptive_generation,
    )
    logger.debug("AgentSession created successfully")

    # Create conversation logger
    conversation_logger = ConversationLogger(
        session_id=session_id,
        output_dir="logs",
    )

    # Register event handler for logging
    session.on("conversation_item_added", conversation_logger.on_conversation_item_added)

    # Room options - configure based on text_only_mode
    if config.session.text_only_mode:
        # Text-only mode: Disable audio input/output
        room_options = room_io.RoomOptions(
            audio_input=False,
            audio_output=False,
            text_input=True,   # Explicit for clarity
            text_output=True,  # Explicit for clarity
        )
    else:
        # Audio mode: Enable audio with optional noise cancellation
        if config.session.enable_noise_cancellation:
            logger.debug("Enabling noise cancellation")
            room_options = room_io.RoomOptions(
                audio_input=room_io.AudioInputOptions(
                    noise_cancellation=noise_cancellation.BVC(),
                ),
            )
        else:
            room_options = room_io.RoomOptions()

    # Log the selected mode for debugging
    mode = "text-only" if config.session.text_only_mode else "audio"
    logger.info(
        f"Starting session in {mode} mode",
        extra={
            "session_id": session_id,
            "text_only": config.session.text_only_mode,
            "noise_cancellation": config.session.enable_noise_cancellation,
        },
    )

    # Start the session
    logger.debug("Starting session with agent...")
    await session.start(
        agent=drive_thru_agent,
        room=ctx.room,
        room_options=room_options,
    )

    logger.info("Session started, connecting to room")

    # Join the room
    await ctx.connect()

    logger.info("Connected to room successfully")

    # Greet the user
    logger.debug("Sending greeting...")
    await session.say("Welcome to McDonald's! What can I get for you today?")
    logger.debug("Greeting sent")


def create_server() -> AgentServer:
    """Create and configure the AgentServer.

    This server is used by LiveKit's CLI to provide console, start, and dev commands.
    """
    server = AgentServer()
    server.setup_fnc = _prewarm
    server.rtc_session()(_handle_rtc_session)
    return server


if __name__ == "__main__":
    # Use LiveKit's built-in CLI which provides:
    # - console: Interactive testing mode (audio or text)
    # - start: Production mode
    # - dev: Development mode with auto-reload
    server = create_server()
    cli.run_app(server)
