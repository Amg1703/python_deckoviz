import json
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, RoomInputOptions
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.plugins import google, deepgram, noise_cancellation, silero

from utils.logger import setup_logger
from utils.instructions import personal_painter, onboarding_prompt, image_search_prompt, image_search_guide_prompt
from utils.shutdown import personal_painter_shutdown, onboarding_shutdown, image_search_shutdown
from utils.image_search import search_image
from utils.assistant import Assistant

load_dotenv()
logger = setup_logger(name=__name__, logfile="agent.log")
logger.debug("Starting agent...")
    
task_modes = {
    "personal_painter": {
        "shutdown": personal_painter_shutdown,
        "prompt": personal_painter,
    },
    "onboarding": {
        "shutdown": onboarding_shutdown,
        "prompt": onboarding_prompt,
    },
    "image_search": {
        "shutdown": image_search_shutdown,
        "prompt": image_search_guide_prompt,
        "before_llm_callback": search_image,
    },
}

async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    participant = await ctx.wait_for_participant()
    logger.debug(f"Room: {ctx.room}")
    room_name = ctx.room.name
    logger.debug(f"Participant: {participant}")
    metadata = json.loads(participant.metadata or "{}")
    agent_name = metadata.get("agent_mode", "personal_painter")

    logger.debug(f"Metadata: {metadata}")
    logger.debug(f"Agent Name: {agent_name}")        
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=google.LLM(model="gemini-2.0-flash-exp"),
        tts=deepgram.TTS(model="aura-asteria-en"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(
            instructions=task_modes[agent_name]["prompt"],
            mode=agent_name,
            before_llm_callback=task_modes[agent_name].get("before_llm_callback"),
            context=ctx,
            metadata=metadata,
            room_name=room_name,
        ),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )

    async def shutdown():
        await task_modes[agent_name]["shutdown"](session, room_name=room_name, **metadata)
    ctx.add_shutdown_callback(shutdown)

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))