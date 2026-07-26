from Recruiter_module.Chains.followup_question_chain import generate_followup_question
from langchain_core.exceptions import OutputParserException

def follow_up_node(state):
    missing_fields=state.get("missing_fields",[])
    job_data=state.get("job_data",{})

    if not missing_fields:
        return{
            **state,
            "next_question":None
        }
    
    try:
        result=generate_followup_question(missing_fields,job_data)
        question=result.question
    except OutputParserException:
        question = f"Could you provide your {missing_fields[0].replace('_', ' ')}?"

    return{
        **state,
        "next_question":question,
        "stage":"followup"
    }