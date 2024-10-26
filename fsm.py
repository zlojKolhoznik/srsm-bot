from aiogram.fsm.state import StatesGroup, State


class QuestionTypes(StatesGroup):
    choosing_type = State()
    writing_question = State()
    choosing_activating_punkt = State()
    choosing_deactivating_punkt = State()
    choosing_subscribing_punkt = State()
    choosing_unsubscribing_punkt = State()
    choosing_opening_punkt = State()
    choosing_closing_punkt = State()
