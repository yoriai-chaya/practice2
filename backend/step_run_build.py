from base import (
    EventType,
    LocalContext,
    SSEPayload,
    StepResult,
)
from config import Settings
from logger import logger
from run_build_cmd import run_build


async def run_build_step(
    context: LocalContext,
    settings: Settings,
) -> StepResult:
    logger.debug("run_build_step called")
    sse_events: list[SSEPayload] = []

    build_result = await run_build(context, settings)

    sse_events.append(
        SSEPayload(
            event=EventType.CHECK_RESULT,
            payload={
                "checker": "Build",
                "result": build_result.result,
                "rule_id": "npm run build",
                "detail": build_result.detail,
            },
        )
    )
    return StepResult(result=build_result, sse_events=sse_events)
