import json 
import re
from typing import List,Dict,Optional,Any
from langchain_deepseek import ChatDeepSeek
from config import DEEPSEEK_API_KEY,DEEPSEEK_MODEL

def _build_client(temperature:float):
    return ChatDeepSeek(
        model=DEEPSEEK_MODEL,
        temperature=temperature,
        api_key=DEEPSEEK_API_KEY
    )

def call_llm(system_prompt:str,conversation_history:Optional[List[Dict[str,str]]]=None,
             user_input:Optional[str]=None,temperature:float=0.7)->str:
    from langchain_core.messages import SystemMessage,HumanMessage,AIMessage

    conversation_history=conversation_history or []
    messages=[SystemMessage(content=system_prompt)]

    for turn in conversation_history:
        if turn['role']=='user':
            messages.append(HumanMessage(content=turn['content']))
        elif turn['role'] == 'assiostent':
            messages.append(AIMessage(content=turn['content']))

    if user_input is not None:
        messages.append(HumanMessage(content=user_input))

    client=_build_client(temperature)
    return client.invoke(messages).content

def _extract_json(text:str)->Optional[Any]:

    fenced=re.search(r"```(?:json)?\s*(.*?)```",text,re.DOTALL)
    candidate=fenced.group(1).strip() if fenced else text.strip()

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    match=re.search(r"(\{.*\}|\[.*\])",candidate,re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None

def call_llm_structured(system_prompt:str,user_input:str,temperature:float= 0.0,max_retries: int=2,)-> Dict:

    prompt=system_prompt
    last_raw=""
    for attempt in range(max_retries+1):
        last_raw=call_llm(
            system_prompt=prompt,
            user_input=user_input,
            temperature=temperature,
        )
        parsed=_extract_json(last_raw)
        if isinstance(parsed, (dict,list)):
            return parsed

        prompt=(
            system_prompt
            +"\n\nIMPORTANT: Your previous reply was not valid JSON."
            "Reply with ONLY a single valid JSON object.No prose, no code fences."
        )
    raise ValueError(f"Model did not return valid JSON after retries. Last reply:\n{last_raw}")
    