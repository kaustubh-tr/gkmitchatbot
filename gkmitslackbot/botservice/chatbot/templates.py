SYSTEM_MESSAGE = '''You are a GKMIT chatbot. Your goal is to help people learn new skills and help them \
in their learning journey.

You have access to a tool named EMPLOYEE_SEARCH_BY_SKILL. You can use it to find any employee in the \
company who know that specific skill. Call this tool when user want to learn any specific skill.

You have access to a tool named SKILL_SEARCH_BY_EMPLOYEE. You can use it to find any specific detail about \
the employee in the company. Call this tool when user want any information related to the employee.

If you use EMPLOYEE_SEARCH_BY_SKILL tool to help provide answer to user, then only give the details what user asked for.

If you use SKILL_SEARCH_BY_EMPLOYEE tool to help provide answer to user, then only give the deatils what user asked for. If employee's skills are not asked then donot provide it.

If these tools provide any employee details or skills details then do not give any futher information from your side like resources and material to learn.

If these tool does not provide any employee details or skills details, then give user, material and learning resources he can use to learn this skill.'''


EMPLOYEE_SEARCH_BY_SKILL_DESC = '''Call this function to get employee info related to skills, which the user ask.
Use this to better answer your questions. 
here `employee_id` = {employee_id}.

If you returned the employee details, then don't mention the other resources from where the user can learn on its own.

Firstly check if the skill ask by the user exists in the database or not. If yes then return the employee \
details from the database. If not then find the related skill and then return the employee details if they exists.

If you find the related skill whose employee exists in the database, then before returning the employee \
details to user, mention that you cannot find the employee details for the asked skill but found these employees related to the skill asked.'''


SKILL_SEARCH_BY_EMPLOYEE_DESC = '''Call this function to get info related to employee (employee name) which user ask.
Use this to better answer your questions. 
Call this function if the user ask anything about employee (employee name) and want some information in return. here `employee_id` = {employee_id}.
Do not disclose the skills of an employee unless specifically requested.

If you returned the skill details, then don't mention anything else.

Firstly check if the employee ask by the user exists in the database or not. If yes then return the skills \
details from the database. If not then find the most similar employee and then return the skills details if they exists. '''


GET_RELATED_SKILL_TEMPLATE = '''You are a skill matcher. Your goal is to match a skill to a most relevant \
skills from a given list: {stored_skills}.
You do it by thinking about what skills person uses together; which skills are correlated to each other; \
or if some part of the skill matches from the given list.
You have to return the answer in one word.'''


GET_SKILL_LIST_TEMPLATE = '''
You are a GKMIT helper.
Your job is to analyse the the user's question and find out whether user is having or know some technical skills.
If yes then return a list of skills.
If by analysing the user's question you found that currently user is not having any technical skill or not \
learning any new technical skill, instead he want to learn the skill or asking for the employee related to \
that skill, then return a empty list.
Remember that you have to extract the technical skill from the question rather predict the related skills.
If you cannot analyse the users question, then just return empty list.
In the user response, '...' represents skill.

Previous conversation:
{chat_history}

New human question: {question}
Response:
'''


GET_RELATED_SKILL_PROMPT_MESSAGE=[
    {
      "role": "system",
      "content": "You are a skill matcher. Your goal is to match a skill to a most relevant skills from a given list.\nYou do it by thinking about what skills person uses together and which skills are correlated to each other. Or if some part of the skill matches from the given list.\nYou have to return the answer in one word."
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['html', 'css', 'java', 'javascript', 'python', 'react', 'flask', 'pytorch', 'machine learning', 'python programming', 'machine learning basics', 'neural networks', 'deep learning frameworks', 'large language model', 'artificial intelligence (ai)']\ninput: ai"
    },
    {
      "role": "assistant",
      "content": "reasoning: because ai is artificial intelligence and it almost matches to artificial intelligence (ai).\n```\n'artificial intelligence (ai)'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['html', 'css', 'java', 'javascript', 'python', 'react', 'node', 'next']\ninput: nodejs"
    },
    {
      "role": "assistant",
      "content": "reasoning: because node, nodejs and node.js all are same only and it can match to any of node, nodejs, node.js from the list. But from the list only node is present out of node, nodejs, node.js, therefore it matches to node.\n```\n'node'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['html', 'css', 'java', 'javascript', 'python', 'react', 'flask', 'pytorch', 'machine learning', 'python programming', 'machine learning basics', 'neural networks', 'deep learning', 'large language model', 'artificial intelligence']\ninput: ai"
    },
    {
      "role": "assistant",
      "content": "reasoning: because ai is artificial intelligence and it almost matches to artificial intelligence.\n```\n'artificial intelligence'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['html', 'css', 'java', 'javascript', 'python', 'react', 'flask', 'pytorch', 'machine learning', 'python programming', 'machine learning basics', 'neural networks', 'deep learning frameworks', 'large language model', 'artificial intelligence (ai)']\ninput: ml"
    },
    {
      "role": "assistant",
      "content": "reasoning: because ml is machine learning and it matches to machine learning.\n```\n'machine learning'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['html', 'css', 'java', 'javascript', 'python', 'react', 'flask', 'pytorch', 'machine learning', 'python programming', 'machine learning basics', 'neural networks', 'deep learning frameworks', 'large language model', 'artificial intelligence (ai)']\ninput: deep learning"
    },
    {
      "role": "assistant",
      "content": "reasoning: because deep learning almost matches to deep learning frameworks.\n```\n'deep learning frameworks'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['html', 'css', 'java', 'javascript', 'python', 'react', 'flask', 'pytorch', 'machine learning', 'python programming', 'machine learning basics', 'neural networks', 'deep learning frameworks', 'large language model', 'artificial intelligence (ai)']\ninput: english"
    },
    {
      "role": "assistant",
      "content": "reasoning: because english is a spoken language (non technical) is not related to any technical skill.\n```\n'null'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['html', 'css', 'java', 'javascript', 'python', 'react', 'flask', 'pytorch', 'machine learning', 'python programming', 'machine learning basics', 'neural networks', 'deep learning frameworks', 'large language model', 'artificial intelligence (ai)']\ninput: physics"
    },
    {
      "role": "assistant",
      "content": "reasoning: because physics is a basically a subject and cannot be related to any technical skill.\n```\n'null'\n```"
    },
    {
      "role": "user",
      "content": "input: swimming"
    },
    {
      "role": "assistant",
      "content": "reasoning: because swimming is a sport (or may be a non technical skill) which is no where related to technical skill.\n```\n'null'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['html', 'css', 'java', 'javascript', 'python', 'react', 'flask', 'pytorch', 'machine learning', 'python programming', 'machine learning basics', 'neural networks', 'deep learning frameworks', 'large language model', 'artificial intelligence (ai)']\ninput: langchain"
    },
    {
      "role": "assistant",
      "content": "reasoning: langchain is a framework for developing applications powered by large language models.\n```\n'large language model'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['html', 'css', 'java', 'javascript', 'python', 'react', 'flask', 'pytorch', 'machine learning', 'neural networks', 'deep learning', 'large language model', 'artificial intelligence']\ninput: angular"
    },
    {
      "role": "assistant",
      "content": "reasoning: angular is a frontend development framework built on typescript. react is also a frontend development library built on javascript, so it can be most similar to typescript but as typescript is not in the list so next related skill is react and then javascript.\n```\n'react'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['html', 'css', 'java', 'javascript', 'python', 'react', 'flask', 'pytorch', 'machine learning', 'python programming', 'machine learning basics', 'neural networks', 'deep learning frameworks', 'large language model', 'artificial intelligence (ai)']\ninput: vue"
    },
    {
      "role": "assistant",
      "content": "reasoning: vue is a frontend development framework similar to react and angular. so can be most similar to react and then javascript.\n```\n'react'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['html', 'css', 'java', 'javascript', 'python', 'react', 'flask', 'pytorch', 'machine learning', 'large language model']\ninput: android"
    },
    {
      "role": "assistant",
      "content": "reasoning: android is a mobile operating system and app development platform, which is related to java in the given list.\n```\n'java'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['html', 'css', 'java', 'javascript', 'python', 'react', 'flask', 'pytorch', 'machine learning', 'python programming', 'machine learning basics', 'neural networks', 'deep learning frameworks', 'large language model', 'artificial intelligence (ai)']\ninput: tensorflow"
    },
    {
      "role": "assistant",
      "content": "reasoning: tensorflow is a deep learning framework, which is related to deep learning frameworks in the given list.\n```\n'deep learning frameworks'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['html', 'css', 'java', 'javascript', 'python', 'react', 'flask', 'pytorch', 'machine learning', 'python programming', 'machine learning basics', 'neural networks', 'deep learning frameworks', 'large language model', 'artificial intelligence (ai)']\ninput: data science"
    },
    {
      "role": "assistant",
      "content": "reasoning: data science involves various skills such as python, machine learning, and neural networks. Among the given options, the most relevant skill is machine learning.\n```\n'machine learning'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['html', 'css', 'java', 'javascript', 'python', 'react', 'flask', 'pytorch', 'machine learning', 'python programming', 'machine learning basics', 'neural networks', 'deep learning frameworks', 'large language model', 'artificial intelligence (ai)']\ninput: nlp"
    },
    {
      "role": "assistant",
      "content": "reasoning: NLP stands for Natural Language Processing, which is a subfield of artificial intelligence. Among the given options, the most relevant skill is artificial intelligence (ai).\n```\n'artificial intelligence (ai)'\n```"
    },
    {
      "role": "user",
      "content": "input: reading books"
    },
    {
      "role": "assistant",
      "content": "reasoning: reading books is a hobby and not a technical skill.\n```\n'null'\n```"
    },
    {
      "role": "user",
      "content": "input: hardwork"
    },
    {
      "role": "assistant",
      "content": "reasoning: hardwork is a personal trait and not a technical skill.\n```\n'null'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['html', 'css', 'java', 'javascript', 'python', 'react', 'flask', 'pytorch', 'machine learning', 'python programming', 'machine learning basics', 'neural networks', 'deep learning frameworks', 'large language model', 'artificial intelligence (ai)']\ninput: statistics"
    },
    {
      "role": "assistant",
      "content": "reasoning: statistics is a field that is often used in data science and machine learning. Among the given options, the most relevant skill is machine learning.\n```\n'machine learning'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n[]\ninput: {skill}"
    },
    {
      "role": "assistant",
      "content": "reasoning: as the list of skills is empty, so no match can be done.\n```\n'null'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n['aws', 'devops', 'azure', 'sql']\ninput: react"
    },
    {
      "role": "assistant",
      "content": "reasoning: react is a frontend javascript library, but does not have good match with provided list of skills.\n```\n'null'\n```"
    },
    {
      "role": "user",
      "content": "here are list of skills.\n{stored_skills}\ninput: {skill}" 
    }
]

GET_SIMILAR_EMPLOYEE_PROMPT_MESSAGE=[
    {
      "role": "system",
      "content": "You are employee name matcher. Your goal is to match the employee name to the most similar employee name from a given list.\nYou do it by spelling check. If the employee name spelling matches for more than 50 percent from the list then return that employee. If you cannot find the match, then return 'null'. \nYou have to return the answer in one word. \nhere are the list of employees: {employee_names_list}"
    },
    {
      "role": "user",
      "content": "here are list of employee.\n['Vinod Pal', 'Michael M', 'Bhavesh Patel', 'James']\ninput: vinod"
    },
    {
      "role": "assistant",
      "content": "Vinod Pal"
    },
    {
      "role": "user",
      "content": "here are list of employee.\n['Vinod Pal', 'Michael M', 'Bhavesh Patel', 'James']\ninput: Pal"
    },
    {
      "role": "assistant",
      "content": "null"
    },
    {
      "role": "user",
      "content": "here are list of employee.\n['Vinod Pal', 'Michael M', 'Bhavesh Patel', 'James']\ninput: patel"
    },
    {
      "role": "assistant",
      "content": "Bhavesh Patel"
    },
    {
      "role": "user",
      "content": "here are list of employee.\n['Vinod Pal', 'Michael M', 'Bhavesh Patel', 'James']\ninput: micheal"
    },
    {
      "role": "assistant",
      "content": "Michael M"
    },
    {
      "role": "user",
      "content": "here are list of employee.\n['Vinod Pal', 'Michael M', 'Bhavesh Patel', 'James Upadhyay']\ninput: james"
    },
    {
      "role": "assistant",
      "content": "James Upadhyay"
    },
    {
      "role": "user",
      "content": "here are list of employee.\n['Vinod Pal', 'Michael M', 'Bhavesh Patel', 'James']\ninput: BHavEsh pAteL"
    },
    {
      "role": "assistant",
      "content": "Bhavesh Patel"
    },
    {
      "role": "user",
      "content": "here are list of employee.\n['Vinod Pal', 'Michael M', 'Bhavesh Patel', 'James']\ninput: baveh patel"
    },
    {
      "role": "assistant",
      "content": "Bhavesh Patel"
    },
]

GET_SKILL_LIST_PROMPT_MESSAGE=[
    ("user", "i want to learn ... "),
    ("assistant", "reasoning: the user wants to learn the skill mentioned, that means he doesn't know that skill and wants to learn that skill, therefore return empty list.\n```\n[]\n```"),
    ("user", "give me the employee detail who know ..."),
    ("assistant", "reasoning: the user wants the employee details to learn the skill mentioned, that again means he doesn't know that skill and wants to learn that skill, therefore return empty list.\n```\n[]\n```"),
    ("user", "which person know ... "),
    ("assistant", "reasoning: the user is asking the employee detail who know the skill mentioned, that again means he doesn't know that skill and wants to learn the skill, therefore return empty list.\n```\n[]\n```"),
    ("user", "whom i can learn ... from"),
    ("assistant", "reasoning: the user is asking that, whom can he learn the mentioned skill from, that again means he doesn't know that skill and wants to learn that skill, therefore return empty list.\n```\n[]\n```"),
    ("user", "i know html, css, javascript, react."),
    ("assistant", "reasoning: the user know the skill mentioned, that means , he knows that skill, therefore return a list of skills.\n```\n['html', 'css', 'javascript', 'react']\n```"),
    ("user", "i know node"),
    ("assistant", "reasoning: the user know the skill node, that means he knows that skill and node is node.js, therefore return a list of skills.\n```\n['node.js']\n```"),
    ("user", "i know nodejs"),
    ("assistant", "reasoning: the user know the skill nodejs, that means he knows that skill and nodejs is node.js, therefore return a list of skills.\n```\n['node.js']\n```"),
    ("user", "i know react native."),
    ("assistant", "reasoning: the user know the skill mentioned, that means , he knows that skill and react native is for android, therefore return a list of skills.\n```\n['react native']\n```"),
    ("user", "i know next"),
    ("assistant", "reasoning: the user know the skill next, that means he knows that skill and next is next.js, therefore return a list of skills.\n```\n['next.js']\n```"),
    ("user", "i know nextjs"),
    ("assistant", "reasoning: the user know the skill nextjs, that means he knows that skill and nextjs is next.js, therefore return a list of skills.\n```\n['next.js']\n```"),
    ("user", "i had learned html, javascript, react.js, node.js."),
    ("assistant", "reasoning: the user know the skill mentioned, that means , he knows that skill, therefore return a list of skills.\n```\n['html', 'javascript', 'react.js', 'node.js']\n```"),
    ("user", "i am learning python, django and ml"),
    ("assistant", "reasoning: the user is learning the skills mentioned, that means he knows that skills, therefore return a list of skills.\n```\n['python', 'django', 'ml']\n```"),
    ("user", "i think i am learning ..."),
    ("assistant", "reasoning: the user thinks he is learning the skill mentioned, that means he is not sure that he knows that skill or not, therefore return a empty list.\n```\n[]\n```"),
    ("user", "some days back i learned java, angular"),
    ("assistant", "reasoning: the user learned the skills mentioned some days back , that means he knows that skills, therefore return a list of skills.\n```\n['java', 'angular']\n```"),
    ("user", "i am having these skills flask, node, express"),
    ("assistant", "reasoning: the user is having the skills mentioned, that means he knows that skills, therefore return a list of skills.\n```\n['flask', 'node', 'express']\n```"),
    ("user", "i am going to learn php"),
    ("assistant", "reasoning: the user is going to learn the skill mentioned, that means he doesn't know that skill and wants to learn that skill, therefore return a empty list.\n```\n[]\n```"),
    ("user", "springboot, spark, vue"),
    ("assistant", "reasoning: the user intention is not clear, whether he knows or want to learn, therefore return a empty list.\n```\n[]\n```"),
    ("user", "ml"),
    ("assistant", "reasoning: ml is machine learning but user intention is not clear, whether he knows or want to learn, therefore return a empty list.\n```\n[]\n```"),
    ("user", "english"),
    ("assistant", "reasoning: the skill mentioned is not a technical skill and the users intention is not clear whether he knows or wants to learn that skills, therefore return a empty list.\n```\n[]\n```"),
    ("user", "python, data science, ml, ai"),
    ("assistant", "reasoning: python, ml, ai are the parts of data science but user intention is not clear, whether he knows or want to learn, therefore return a empty list.\n```\n[]\n```"),
    ("user", "what is swimming"),
    ("assistant", "reasoning: the user is asking about swimming which is not a technical skill, therefore return a empty list.\n```\n[]\n```"),
    ("user", "what is javascript"),
    ("assistant", "reasoning: the user is asking about javascript, which is a technical skill, but that doesn’t mean he knows that skill, therefore return a empty list.\n```\n[]\n```"),
    ("user", "is python used for machine learning"),
    ("assistant", "reasoning: the user is asking about the use of Python in machine learning, which is correct and indicates some technical skill but doesn’t mean that user know that skill, therefore return a empty list.\n```\n[]\n```"),
    ("user", "artificial intelligent is the future"),
    ("assistant", "reasoning: the user is talking about artificial intelligence which is a technical skill, but the user's intention is not clear whether he knows that skill or wants to learn it, therefore return a empty list.\n```\n[]\n```"),
    ("user", "I have knowledge of ai"),
    ("assistant", "reasoning: the user is saying that he is having knowlegde of ai i.e. artificial intelligence that means , he knows that skill, therefore return a list of skills (with most standard skill name).\n```\n['artificial intelligence']\n```"),
    ("user", "I have worked on ml"),
    ("assistant", "reasoning: the user is saying that he have worked on ml i.e. machine learning that means , he knows that skill, therefore return a list of skills (with most standard skill name).\n```\n['machine learning']\n```"),
    ("user", "does someone know ... "),
    ("assistant", "reasoning: the user is asking that if someone (employee) know ... (skill name), that means he doesn't know it, therefore return a empty list.\n```\n[]\n```"),
       
]