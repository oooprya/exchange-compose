import json

from loguru import logger
from openai import AsyncOpenAI

from config import OPENAI_API_KEY
from ai.tools import TOOLS, execute_tool


client = (
    AsyncOpenAI(api_key=OPENAI_API_KEY)
    if OPENAI_API_KEY
    else None
)


class Assistant:

    async def chat(
        self,
        messages,
        chat_id: str | None = None
    ):

        if not client:
            return (
                "OpenAI API key не настроен. "
                "Добавьте OPENAI_API_KEY, чтобы AI мог отвечать."
            )

        # ======================================================
        # ПЕРВЫЙ ЗАПРОС К OPENAI
        # ======================================================

        response = await client.responses.create(

            model="gpt-4o-mini",

            input=messages,

            tools=TOOLS,
        )

        logger.info(
            "OpenAI response id={}",
            response.id
        )

        logger.debug(
            "OpenAI output: {}",
            response.output
        )

        # ======================================================
        # ОБРАБОТКА TOOL CALLS
        # ======================================================

        tool_outputs = []

        for item in response.output:

            item_type = getattr(
                item,
                "type",
                None
            )

            logger.info(
                "Response item type={} name={} call_id={}",
                item_type,
                getattr(item, "name", None),
                getattr(item, "call_id", None),
            )

            # --------------------------------------------------
            # FUNCTION CALL
            # --------------------------------------------------

            if item_type != "function_call":
                continue

            name = item.name
            call_id = item.call_id

            try:

                # ----------------------------------------------
                # ARGUMENTS
                # ----------------------------------------------

                if isinstance(
                    item.arguments,
                    str
                ):
                    arguments = json.loads(
                        item.arguments
                    )
                else:
                    arguments = item.arguments

                logger.info(
                    "Tool call: {} {}",
                    name,
                    arguments
                )

                # ----------------------------------------------
                # EXECUTE TOOL
                # ----------------------------------------------

                result = await execute_tool(

                    name=name,
                    arguments=arguments,
                    chat_id=chat_id,
                )

                logger.info(
                    "Tool result: {}",
                    result
                )

                # ----------------------------------------------
                # TOOL OUTPUT
                # ----------------------------------------------

                tool_outputs.append({

                    "type": "function_call_output",

                    "call_id": call_id,

                    "output": json.dumps(
                        result,
                        ensure_ascii=False
                    ),
                })

            except Exception as e:

                logger.exception(
                    "Ошибка выполнения tool={} arguments={} chat_id={}",
                    name,
                    arguments,
                    chat_id,
                )

                # Очень важно:
                # даже если функция упала,
                # OpenAI должен получить output
                # для конкретного call_id.

                tool_outputs.append({

                    "type": "function_call_output",

                    "call_id": call_id,

                    "output": json.dumps(
                        {
                            "success": False,
                            "error": str(e),
                        },
                        ensure_ascii=False
                    ),
                })

        # ======================================================
        # ЕСЛИ TOOL НЕ ВЫЗЫВАЛСЯ
        # ======================================================

        if not tool_outputs:

            logger.info(
                "Tools не вызывались"
            )

            return response.output_text

        # ======================================================
        # ОТПРАВЛЯЕМ РЕЗУЛЬТАТЫ TOOLS ОБРАТНО OPENAI
        # ======================================================

        logger.info(
            "Отправляем {} tool outputs обратно OpenAI",
            len(tool_outputs)
        )

        second_response = await client.responses.create(

            model="gpt-4o-mini",

            previous_response_id=response.id,

            input=tool_outputs,
        )

        logger.info(
            "OpenAI second response id={}",
            second_response.id
        )

        logger.debug(
            "Second response output: {}",
            second_response.output
        )

        return second_response.output_text


assistant = Assistant()
