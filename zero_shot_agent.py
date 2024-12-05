import os
from typing import Annotated
from dotenv import load_dotenv
from typing_extensions import TypedDict
from datetime import datetime

from langgraph.graph.message import AnyMessage, add_messages
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig

from tools.car_operations import search_car_rentals, book_car_rental, update_car_rental, cancel_car_rental
from tools.excursion_operations import search_trip_recommendations, book_excursion, update_excursion, cancel_excursion
from tools.flight_operations import search_flights, fetch_user_flight_information, update_ticket_to_new_flight, cancel_ticket
from tools.hotel_operations import search_hotels, book_hotel, update_hotel, cancel_hotel

from lookup_policy import lookup_policy
from google_search import google_search_results

load_dotenv(".env")
api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(
    # model="llama3-groq-70b-8192-tool-use-preview",
    model="llama-3.1-70b-versatile",
    temperature=0.3,
    api_key=api_key,
    timeout=None,
    max_retries=2,
    # other params...
)
# embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            configuration = config.get("configurable", {})
            passenger_id = configuration.get("passenger_id", None)
            state = {**state, "user_info": passenger_id}
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + \
                    [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}


primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful customer support assistant for Swiss Airlines. "
            " Use the provided tools to search for flights, company policies, and other information to assist the user's queries. "
            " When searching, be persistent. Expand your query bounds if the first search returns no results. "
            " If a search comes up empty, expand your search before giving up."
            "\n\nCurrent user:\n<User>\n{user_info}\n</User>"
            "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

part_1_tools = [
    google_search_results(max_results=1),
    fetch_user_flight_information,
    search_flights,
    lookup_policy,
    update_ticket_to_new_flight,
    cancel_ticket,
    search_car_rentals,
    book_car_rental,
    update_car_rental,
    cancel_car_rental,
    search_hotels,
    book_hotel,
    update_hotel,
    cancel_hotel,
    search_trip_recommendations,
    book_excursion,
    update_excursion,
    cancel_excursion,
]
part_1_assistant_runnable = primary_assistant_prompt | llm.bind_tools(
    part_1_tools)
